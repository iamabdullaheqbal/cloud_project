"""
Ingest the Financial Study Pressure corpus from an Excel (.xlsx) or CSV file.

Usage (from backend/ directory):
  source .venv/bin/activate
  python scripts/ingest_corpus.py                                          # default: data/corpus.xlsx or corpus.xlsx in backend/
  python scripts/ingest_corpus.py Financial_Study_Pressure_Chatbot_Corpus.xlsx
  python scripts/ingest_corpus.py data/corpus.csv

Excel format expected (auto-detected):
  - Headers on row 3:  #  |  Category  |  Question  |  Detailed Answer  |  Key Points  |  Source
  - Data rows start at row 5 (row 4 is a section separator)
  - Section separator rows have None in the # column — they are skipped

CSV format expected:
  - First row is headers
  - Columns: question, answer, key_points, category, source  (flexible name matching)
"""
import asyncio
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import delete
from app.db.database import init_db, AsyncSessionLocal
from app.db.models import CorpusChunk
from app.services.mistral_service import get_embedding


# ── Excel reader ─────────────────────────────────────────────────────────────

def read_xlsx(path: str) -> list[dict]:
    try:
        import openpyxl
    except ImportError:
        print("ERROR: openpyxl not installed. Run: uv add openpyxl")
        sys.exit(1)

    wb = openpyxl.load_workbook(path)
    ws = wb.active

    rows = []
    for row in ws.iter_rows(values_only=True):
        num, category, question, answer, key_points, source = (
            row[0], row[1], row[2], row[3], row[4], row[5] if len(row) > 5 else None
        )

        # Skip title rows, header row, empty rows, and section separator rows
        # Data rows have an integer in the first column
        if not isinstance(num, int):
            continue
        if not question or not answer:
            continue

        rows.append({
            "question":   str(question).strip(),
            "answer":     str(answer).strip(),
            "key_points": str(key_points).strip() if key_points else None,
            "category":   str(category).strip() if category else "General",
            "source":     str(source).strip() if source else None,
        })

    return rows


# ── CSV reader ────────────────────────────────────────────────────────────────

COLUMN_ALIASES = {
    "question":   ["question", "q", "query"],
    "answer":     ["answer", "a", "response", "detailed answer", "text", "content"],
    "key_points": ["key_points", "key points", "keypoints", "keywords", "summary"],
    "category":   ["category", "cat", "topic", "type"],
    "source":     ["source", "ref", "reference", "citation", "source / url"],
}


def read_csv(path: str) -> list[dict]:
    rows = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        headers = list(reader.fieldnames or [])
        lower_map = {h.strip().lower(): h for h in headers}

        col: dict[str, str | None] = {}
        for field, aliases in COLUMN_ALIASES.items():
            col[field] = next((lower_map[a] for a in aliases if a in lower_map), None)

        if not col["question"] or not col["answer"]:
            print(f"ERROR: CSV must have question and answer columns.")
            print(f"  Found: {headers}")
            sys.exit(1)

        for i, row in enumerate(reader, 2):
            q = row.get(col["question"] or "", "").strip()
            a = row.get(col["answer"] or "", "").strip()
            if not q or not a:
                continue
            rows.append({
                "question":   q,
                "answer":     a,
                "key_points": row.get(col["key_points"] or "", "").strip() or None,
                "category":   row.get(col["category"] or "", "").strip() or "General",
                "source":     row.get(col["source"] or "", "").strip() or None,
            })
    return rows


# ── Main ──────────────────────────────────────────────────────────────────────

def find_corpus_file(arg: str | None) -> str:
    """Resolve corpus file path — checks several default locations."""
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    candidates = []
    if arg:
        candidates.append(arg if os.path.isabs(arg) else os.path.join(backend_dir, arg))
    candidates += [
        os.path.join(backend_dir, "Financial_Study_Pressure_Chatbot_Corpus.xlsx"),
        os.path.join(backend_dir, "data", "corpus.xlsx"),
        os.path.join(backend_dir, "data", "corpus.csv"),
    ]

    for p in candidates:
        if os.path.exists(p):
            return p

    print("ERROR: No corpus file found. Tried:")
    for p in candidates:
        print(f"  {p}")
    print("\nEither pass the path as an argument or place your file at backend/data/corpus.xlsx")
    sys.exit(1)


async def get_embedding_with_retry(text: str, max_retries: int = 5) -> list[float]:
    """Call get_embedding with exponential backoff on 503/transient errors."""
    import asyncio as _asyncio
    delay = 5
    for attempt in range(1, max_retries + 1):
        try:
            return await get_embedding(text)
        except Exception as e:
            msg = str(e)
            if attempt == max_retries:
                raise
            # Retry on 503, 429 (rate limit), or any network/server error
            if any(code in msg for code in ("503", "429", "500", "502", "timeout", "connection")):
                print(f"  Attempt {attempt} failed ({msg[:80]}). Retrying in {delay}s...")
                await _asyncio.sleep(delay)
                delay = min(delay * 2, 60)  # cap at 60s
            else:
                raise


async def ingest(path: str):
    ext = os.path.splitext(path)[1].lower()
    print(f"Reading corpus from: {path}")

    if ext in (".xlsx", ".xls"):
        rows = read_xlsx(path)
    elif ext == ".csv":
        rows = read_csv(path)
    else:
        print(f"ERROR: Unsupported file type '{ext}'. Use .xlsx or .csv")
        sys.exit(1)

    if not rows:
        print("ERROR: No valid rows found in file.")
        sys.exit(1)

    print(f"Found {len(rows)} Q&A pairs.\n")

    await init_db()

    async with AsyncSessionLocal() as session:
        await session.execute(delete(CorpusChunk))
        await session.commit()
        print("Cleared existing corpus.\n")

        for i, item in enumerate(rows, 1):
            print(f"[{i:>2}/{len(rows)}] {item['category']:<30} | {item['question'][:60]}...")
            embedding = await get_embedding_with_retry(item["question"])
            session.add(CorpusChunk(
                question=item["question"],
                answer=item["answer"],
                key_points=item["key_points"],
                category=item["category"],
                source=item["source"],
                embedding=embedding,
            ))
            # Flush every chunk so progress survives a mid-run failure
            await session.flush()

        await session.commit()
        print(f"\nDone. {len(rows)} corpus chunks ingested successfully.")


if __name__ == "__main__":
    path = find_corpus_file(sys.argv[1] if len(sys.argv) > 1 else None)
    asyncio.run(ingest(path))
