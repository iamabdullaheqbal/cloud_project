<div align="center">

# 💸 FinStress Bot

### *Two Minds. One Answer.*

**AI-powered financial study pressure chatbot built for university students**

![Python](https://img.shields.io/badge/Python-3.13+-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.136+-009688?style=flat-square&logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-16-000000?style=flat-square&logo=next.js&logoColor=white)
![Mistral](https://img.shields.io/badge/Mistral-small--latest-FF7000?style=flat-square&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PC9zdmc+&logoColor=white)
![pgvector](https://img.shields.io/badge/pgvector-PostgreSQL-336791?style=flat-square&logo=postgresql&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

</div>

---

## What Is FinStress Bot

FinStress Bot is a full-stack chatbot application that helps university students navigate financial study pressure through safety-aware RAG comparison. Every query is shown as four side-by-side outputs: S0 Mistral AI, the retrieved research corpus evidence, S1 basic RAG, and S2 safety-aware RAG.

Unlike generic AI chatbots, FinStress Bot is purpose-built for the financial stress experience of university students — covering mental health impacts, budgeting strategies, loan anxiety, institutional support, and long-term consequences. The corpus is sourced directly from peer-reviewed studies, university wellbeing reports, and financial counselling literature.

Built as a Cloud Computing university project and aligned with the MindBridge-RAG student project requirements.

---

## How It Works

```
User sends a query
        ↓
S0 Mistral AI + pgvector corpus retrieval run concurrently
        ↓
Nearest research corpus Q&A becomes retrieved evidence
        ↓
S1 generates a basic RAG answer from the retrieved corpus
        ↓
S2 classifies risk and applies safety-aware RAG routing
        ↓
All outputs are saved to PostgreSQL
        ↓
Frontend renders four side-by-side cards:
S0 Mistral AI | Research Corpus | S1 Basic RAG | S2 Safety-aware RAG
```

---

## Key Features

- **Four-output comparison** — S0 Mistral AI, retrieved research corpus evidence, S1 basic RAG, and S2 safety-aware RAG shown side by side
- **Concurrent execution** — `asyncio.gather()` fires both calls at once; neither waits on the other
- **pgvector semantic search** — queries are embedded with `mistral-embed` (1024-dim) and matched via cosine distance
- **Safety-aware RAG routing** — S2 labels requests with project risk labels and handles crisis/medical cases with stricter safety behavior
- **Isolated DB sessions** — corpus search runs in its own session to prevent transaction poisoning on the main session
- **Full conversation history** — persisted in PostgreSQL, loaded on sidebar click, auto-titled from first message
- **Mistral parameter controls** — temperature, top-p, and max tokens adjustable per request via sidebar sliders with presets
- **Markdown rendering** — Mistral responses render with full GFM support (headings, lists, bold, code, tables)
- **XLSX corpus ingestion** — drop any `.xlsx` or `.csv` file, run one script, corpus is re-embedded and loaded
- **Clean ChatGPT-style UI** — white background, Inter font, green accent, conversation sidebar, floating input

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Frontend | Next.js 16 + Tailwind CSS v4 | Chat UI, conversation sidebar, parameter panel |
| Backend | FastAPI (Python 3.13, async) | REST API, concurrent AI orchestration |
| LLM | Mistral AI `mistral-small-latest` | Generative chat responses |
| Embeddings | Mistral AI `mistral-embed` | 1024-dim query and corpus embeddings |
| Vector DB | PostgreSQL + pgvector | Cosine similarity search over corpus chunks |
| ORM | SQLAlchemy async + asyncpg | Async DB sessions, models, migrations |
| Markdown | react-markdown + remark-gfm | Render formatted Mistral responses |
| Icons | lucide-react | UI icons |
| Package Manager (Python) | `uv` | Python dependency management |

---

## Project Structure

```
financial-chatbot/
├── README.md
├── .gitignore
│
├── backend/
│   ├── main.py                          # Entry point (imports app/main.py)
│   ├── pyproject.toml                   # Python dependencies (managed by uv)
│   ├── .env                             # Environment variables
│   ├── .python-version                  # Pins Python 3.13
│   ├── Financial_Study_Pressure_Chatbot_Corpus.xlsx  # Corpus source file
│   │
│   ├── app/
│   │   ├── main.py                      # FastAPI app, CORS, lifespan, router
│   │   ├── core/
│   │   │   └── config.py                # Typed settings via pydantic-settings
│   │   ├── db/
│   │   │   ├── database.py              # Async engine, session factory, init_db
│   │   │   └── models.py                # Conversation, Message, CorpusChunk models
│   │   ├── api/
│   │   │   └── chat.py                  # All REST endpoints, chat handler
│   │   └── services/
│   │       ├── mistral_service.py       # Mistral chat + embedding API calls
│   │       └── corpus_service.py        # pgvector cosine similarity search
│   │
│   ├── scripts/
│   │   └── ingest_corpus.py             # XLSX/CSV → embeddings → PostgreSQL
│   │
│   └── data/
│       └── corpus_sample.csv            # Sample CSV showing expected format
│
└── frontend/
    ├── package.json
    ├── next.config.ts
    ├── tsconfig.json
    │
    └── src/
        ├── app/
        │   ├── globals.css              # Design system, markdown styles, animations
        │   ├── layout.tsx               # Root layout
        │   └── page.tsx                 # Three-panel layout, top-level state
        ├── components/
        │   ├── ConversationSidebar.tsx  # Sidebar with conversations list + actions
        │   ├── ChatPanel.tsx            # Message thread, input box, suggested prompts
        │   ├── ResponseCard.tsx         # Reusable card with markdown rendering
        │   └── ParameterPanel.tsx       # Temperature / top-p / max-tokens sliders
        ├── lib/
        │   └── api.ts                   # Typed API client for all backend calls
        └── types/
            └── index.ts                 # Shared TypeScript interfaces
```

---

## Prerequisites

- Python 3.13+
- Node.js 18+
- [`uv`](https://docs.astral.sh/uv/getting-started/installation/) — Python package manager
- Mistral API key — [console.mistral.ai](https://console.mistral.ai) (free tier available)
- PostgreSQL with [pgvector extension](https://github.com/pgvector/pgvector)

---

## Environment Variables

| Variable | Purpose | Example |
|---|---|---|
| `DATABASE_URL` | Async PostgreSQL connection string | `postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/financial_chatbot` |
| `MISTRAL_API_KEY` | Mistral AI API key | `sk-...` |
| `CORS_ORIGINS` | Allowed frontend origin | `http://localhost:3000` |
| `APP_ENV` | Environment flag | `development` |
| `NEXT_PUBLIC_API_URL` | Backend URL for frontend | `http://localhost:8000` |

> Use `127.0.0.1` instead of `localhost` in `DATABASE_URL` to force TCP connection and avoid PostgreSQL peer auth issues on Linux.

---

## Database Setup

Run once in `psql` as the postgres superuser:

```sql
CREATE DATABASE financial_chatbot;
\c financial_chatbot
CREATE EXTENSION IF NOT EXISTS vector;
```

Set a password for the postgres user so password auth works over TCP:

```sql
ALTER USER postgres PASSWORD 'postgres';
```

---

## Running the Backend

```bash
# 1. Navigate to backend
cd backend

# 2. Activate virtual environment
source .venv/bin/activate

# 3. Install dependencies (first time only)
uv add fastapi "uvicorn[standard]" asyncpg "sqlalchemy[asyncio]" pgvector \
       "mistralai>=1.0.0" python-dotenv "pydantic>=2.0.0" pydantic-settings \
       httpx openpyxl

# 4. Set your Mistral API key in .env
# Edit backend/.env → MISTRAL_API_KEY=your_key_here

# 5. Start the server
uvicorn app.main:app --reload --port 8000
```

Backend runs at **http://localhost:8000**

---

## Ingesting the Corpus

Place your corpus file in `backend/` and run:

```bash
cd backend
source .venv/bin/activate

# Auto-detects the xlsx file in the backend directory
python scripts/ingest_corpus.py

# Or pass a path explicitly
python scripts/ingest_corpus.py Financial_Study_Pressure_Chatbot_Corpus.xlsx
python scripts/ingest_corpus.py data/corpus.csv
```

**Expected XLSX format** (auto-detected from `QA Corpus` sheet):

| # | Category | Question | Detailed Answer | Key Points | Source / URL |
|---|---|---|---|---|---|
| 2 | Mental Health Impacts | How does financial stress... | Financial stress is... | Anxiety, depression... | https://... |

**Expected CSV format:**

```csv
question,answer,key_points,category,source
How does financial stress...,Financial stress is...,Anxiety; depression,Mental Health,Source 2023
```

The script auto-maps common column name variants (`q`/`query`/`question`, `a`/`response`/`answer`, etc.) and skips section separator rows in the xlsx automatically.

---

## Running the Frontend

```bash
# 1. Navigate to frontend
cd frontend

# 2. Install dependencies (first time only)
npm install

# 3. Start dev server
npm run dev
```

Frontend runs at **http://localhost:3000**

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Health check |
| `POST` | `/api/conversations` | Create a new conversation |
| `GET` | `/api/conversations` | List all conversations (ordered by updated_at DESC) |
| `DELETE` | `/api/conversations/{id}` | Delete conversation and all its messages |
| `PATCH` | `/api/conversations/{id}` | Rename a conversation |
| `GET` | `/api/conversations/{id}/messages` | Get all messages in a conversation |
| `POST` | `/api/conversations/{id}/chat` | Send a message, get S0, corpus, S1, and S2 outputs |

### Chat Request

```json
{
  "query": "How does financial stress affect student mental health?",
  "temperature": 0.4,
  "top_p": 0.9,
  "max_tokens": 800
}
```

### Chat Response

```json
{
  "message": {
    "id": 1,
    "conversation_id": 3,
    "query": "How does financial stress...",
    "mistral_response": "Financial stress is one of...",
    "corpus_response": "Financial stress is one of the most widespread...",
    "s1_response": "Based on the retrieved corpus...",
    "s2_response": "A safe next step is...",
    "corpus_question_matched": "How prevalent is financial stress...",
    "corpus_category": "Mental Health Impacts",
    "corpus_source": "https://...",
    "similarity_score": 0.91,
    "mistral_latency_ms": 1842,
    "corpus_latency_ms": 312,
    "s1_latency_ms": 1480,
    "s2_latency_ms": 1520,
    "s2_risk_label": "L1_STRESS",
    "temperature": 0.4,
    "top_p": 0.9,
    "max_tokens": 800,
    "created_at": "2026-06-03T09:23:10.432759+00:00"
  },
  "mistral": {
    "response": "...",
    "latency_ms": 1842,
    "source": "S0: Mistral AI (mistral-small-latest)"
  },
  "corpus": {
    "response": "...",
    "key_points": "Anxiety, depression, sleep disruption...",
    "matched_question": "How prevalent is financial stress...",
    "category": "Mental Health Impacts",
    "source": "https://...",
    "similarity": 0.91,
    "latency_ms": 312,
    "found": true
  },
  "s1": {
    "response": "...",
    "latency_ms": 1480,
    "source": "S1: Basic RAG"
  },
  "s2": {
    "response": "...",
    "latency_ms": 1520,
    "risk_label": "L1_STRESS",
    "source": "S2: Safety-aware RAG"
  }
}
```

---

## Corpus Coverage

The current corpus covers **31 Q&A pairs** across 8 categories sourced from peer-reviewed literature, university wellbeing reports, and financial counselling organisations:

| Category | Q&A Pairs | Key Sources |
|---|---|---|
| Understanding Financial Study Pressure | 4 | Ellucian 2024, BMC Public Health, IJRISS |
| Mental Health Impacts | 4 | APA, Hope Center, NCBI |
| Coping Strategies | 4 | AFCPE, Oxford Mindfulness Centre |
| Financial Literacy | 4 | StepChange, CFPB, Khan Academy |
| Institutional Support | 4 | UCAS, HESA 2023 |
| Psychology & Behaviour | 4 | CareMe Health, Grand Rising |
| Specific Situations | 4 | ELFI, College Ave, Ellucian |
| Technology & Resources | 2 | AFCPE, Federal Student Aid |
| Long-term & Systemic | 1 | Ellucian Blog, Hope Center |

---

## Database Schema

```sql
-- Persists named conversation sessions
CREATE TABLE conversations (
    id         SERIAL PRIMARY KEY,
    title      VARCHAR(80) DEFAULT 'New Conversation',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- One row per user message + S0/corpus/S1/S2 outputs
CREATE TABLE messages (
    id                      SERIAL PRIMARY KEY,
    conversation_id         INTEGER REFERENCES conversations(id) ON DELETE CASCADE,
    query                   TEXT NOT NULL,
    mistral_response        TEXT,
    corpus_response         TEXT,
    s1_response             TEXT,
    s2_response             TEXT,
    corpus_question_matched TEXT,
    corpus_category         TEXT,
    corpus_source           TEXT,
    similarity_score        FLOAT,
    mistral_latency_ms      INTEGER,
    corpus_latency_ms       INTEGER,
    s1_latency_ms           INTEGER,
    s2_latency_ms           INTEGER,
    s2_risk_label           VARCHAR(40),
    temperature             FLOAT DEFAULT 0.4,
    top_p                   FLOAT,
    max_tokens              INTEGER DEFAULT 800,
    created_at              TIMESTAMPTZ DEFAULT NOW()
);

-- Research corpus with 1024-dim embeddings
CREATE TABLE corpus_chunks (
    id         SERIAL PRIMARY KEY,
    question   TEXT NOT NULL,
    answer     TEXT NOT NULL,
    key_points TEXT,
    category   VARCHAR(120) NOT NULL,
    source     TEXT,
    embedding  vector(1024)
);
```

---

*FinStress Bot is an AI-powered tool for informational and educational purposes. It is not a substitute for professional financial advice or mental health counselling. If you are experiencing a mental health crisis, please contact your university counselling service or a crisis helpline immediately.*
