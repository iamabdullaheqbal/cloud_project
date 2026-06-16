# FinStress Bot Frontend

Next.js frontend for the MindBridge-RAG financial study pressure chatbot.

## What It Shows

Each submitted student question renders four response cards side by side on desktop:

1. `S0 Mistral AI` - basic chatbot response without retrieval grounding.
2. `Research Corpus` - nearest retrieved corpus answer and match metadata.
3. `S1 Basic RAG` - generated answer grounded in the retrieved corpus context.
4. `S2 Safety-aware RAG` - generated answer with MindBridge risk routing and safety rules.

The layout keeps all four cards in one row and scrolls horizontally when the available width is too small.

## Run

```bash
npm install
npm run dev
```

By default, the API client calls `http://localhost:8000`. To point at another backend port:

```bash
NEXT_PUBLIC_API_URL=http://127.0.0.1:8001 npm run dev
```

## Checks

```bash
npm run lint
npm run build
```
