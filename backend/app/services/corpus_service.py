import time
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.services.mistral_service import get_embedding


async def search_corpus(query: str, db: AsyncSession) -> dict:
    """Embed the query and find the most similar corpus chunk via cosine distance."""
    start = time.monotonic()

    try:
        embedding = await get_embedding(query)
        # Build the vector literal directly — SQLAlchemy text() can't bind
        # a parameter that also has a Postgres cast (`:param::vector` confuses the parser)
        vec_literal = f"'[{','.join(str(v) for v in embedding)}]'::vector"

        result = await db.execute(
            text(
                f"""
                SELECT
                    id,
                    question,
                    answer,
                    key_points,
                    category,
                    source,
                    1 - (embedding <=> {vec_literal}) AS similarity
                FROM corpus_chunks
                ORDER BY embedding <=> {vec_literal}
                LIMIT 1
                """
            )
        )
        row = result.mappings().first()
        latency_ms = int((time.monotonic() - start) * 1000)

        if row is None:
            return {
                "found": False,
                "response": None,
                "key_points": None,
                "matched_question": None,
                "category": None,
                "source": None,
                "similarity": None,
                "latency_ms": latency_ms,
            }

        return {
            "found": True,
            "response": row["answer"],
            "key_points": row["key_points"],
            "matched_question": row["question"],
            "category": row["category"],
            "source": row["source"],
            "similarity": float(row["similarity"]),
            "latency_ms": latency_ms,
        }

    except Exception as exc:
        latency_ms = int((time.monotonic() - start) * 1000)
        return {
            "found": False,
            "response": f"Corpus search error: {exc}",
            "key_points": None,
            "matched_question": None,
            "category": None,
            "source": None,
            "similarity": None,
            "latency_ms": latency_ms,
        }
