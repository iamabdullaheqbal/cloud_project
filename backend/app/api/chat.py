import asyncio
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.database import get_db, AsyncSessionLocal
from app.db.models import Conversation, Message
from app.services.mistral_service import (
    get_basic_rag_response,
    get_mistral_response,
    get_safety_aware_rag_response,
)
from app.services.corpus_service import search_corpus

router = APIRouter(prefix="/api")


# ── Pydantic schemas ─────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    query: str
    temperature: float = 0.4
    top_p: float = 0.9
    max_tokens: int = 800


class ConversationRename(BaseModel):
    title: str


# ── Health ────────────────────────────────────────────────────────────────────

@router.get("/health")
async def health():
    return {"status": "ok"}


# ── Conversations ─────────────────────────────────────────────────────────────

@router.post("/conversations")
async def create_conversation(db: AsyncSession = Depends(get_db)):
    conv = Conversation(title="New Conversation")
    db.add(conv)
    await db.commit()
    await db.refresh(conv)
    return {
        "id": conv.id,
        "title": conv.title,
        "created_at": conv.created_at.isoformat(),
        "updated_at": conv.updated_at.isoformat(),
        "message_count": 0,
    }


@router.get("/conversations")
async def list_conversations(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(
            Conversation,
            func.count(Message.id).label("message_count"),
        )
        .outerjoin(Message, Message.conversation_id == Conversation.id)
        .group_by(Conversation.id)
        .order_by(Conversation.updated_at.desc())
    )
    rows = result.all()
    return [
        {
            "id": conv.id,
            "title": conv.title,
            "created_at": conv.created_at.isoformat(),
            "updated_at": conv.updated_at.isoformat(),
            "message_count": msg_count,
        }
        for conv, msg_count in rows
    ]


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: int, db: AsyncSession = Depends(get_db)
):
    conv = await db.get(Conversation, conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    await db.delete(conv)
    await db.commit()
    return {"ok": True}


@router.patch("/conversations/{conversation_id}")
async def rename_conversation(
    conversation_id: int,
    body: ConversationRename,
    db: AsyncSession = Depends(get_db),
):
    conv = await db.get(Conversation, conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    conv.title = body.title[:80]
    conv.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(conv)
    return {
        "id": conv.id,
        "title": conv.title,
        "created_at": conv.created_at.isoformat(),
        "updated_at": conv.updated_at.isoformat(),
    }


@router.get("/conversations/{conversation_id}/messages")
async def get_messages(
    conversation_id: int, db: AsyncSession = Depends(get_db)
):
    conv = await db.get(Conversation, conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
    )
    messages = result.scalars().all()
    return [_msg_dict(m) for m in messages]


async def _corpus_in_own_session(query: str) -> dict:
    """Run corpus search in its own isolated session so errors can't poison the main session."""
    async with AsyncSessionLocal() as session:
        return await search_corpus(query, session)


def classify_risk(query: str) -> str:
    """Lightweight project risk classifier for S2 routing."""
    q = query.lower()

    crisis_terms = [
        "kill myself",
        "suicide",
        "end my life",
        "harm myself",
        "hurt myself",
        "self-harm",
        "self harm",
        "i might die",
        "want to die",
        "violence",
        "hurt someone",
    ]
    medical_terms = [
        "diagnose",
        "diagnosis",
        "depression",
        "anxiety disorder",
        "medicine",
        "medication",
        "pills",
        "doctor prescribe",
        "clinical treatment",
        "mental illness",
    ]
    distress_terms = [
        "hopeless",
        "can't handle",
        "cannot handle",
        "overwhelmed",
        "breaking down",
        "panic",
        "nothing matters",
        "no way out",
    ]
    stress_terms = [
        "stressed",
        "stress",
        "worried",
        "nervous",
        "pressure",
        "anxious",
        "scared",
    ]
    student_support_terms = [
        "fee",
        "fees",
        "tuition",
        "loan",
        "scholarship",
        "budget",
        "financial",
        "money",
        "rent",
        "study",
        "university",
        "college",
        "exam",
        "assignment",
        "campus",
    ]

    if any(term in q for term in crisis_terms):
        return "L3_CRISIS"
    if any(term in q for term in medical_terms):
        return "L4_MEDICAL"
    if any(term in q for term in distress_terms):
        return "L2_DISTRESS"
    if any(term in q for term in stress_terms):
        return "L1_STRESS"
    if any(term in q for term in student_support_terms):
        return "L0_NORMAL"
    return "L5_OUT_OF_SCOPE"


@router.post("/conversations/{conversation_id}/chat")
async def chat(
    conversation_id: int,
    body: ChatRequest,
    db: AsyncSession = Depends(get_db),
):
    conv = await db.get(Conversation, conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Count existing messages to know if this is the first one
    count_result = await db.execute(
        select(func.count(Message.id)).where(
            Message.conversation_id == conversation_id
        )
    )
    existing_count = count_result.scalar_one()

    # Fire S0 and corpus retrieval concurrently — corpus uses its own session.
    (mistral_text, mistral_latency), corpus_result = await asyncio.gather(
        get_mistral_response(body.query, body.temperature, body.top_p, body.max_tokens),
        _corpus_in_own_session(body.query),
    )
    risk_label = classify_risk(body.query)

    # S1 and S2 both depend on retrieved corpus context.
    (s1_text, s1_latency), (s2_text, s2_latency) = await asyncio.gather(
        get_basic_rag_response(
            body.query,
            corpus_result,
            body.temperature,
            body.top_p,
            body.max_tokens,
        ),
        get_safety_aware_rag_response(
            body.query,
            corpus_result,
            risk_label,
            body.temperature,
            body.top_p,
            body.max_tokens,
        ),
    )

    # Persist message and update conversation in one transaction
    try:
        msg = Message(
            conversation_id=conversation_id,
            query=body.query,
            mistral_response=mistral_text,
            corpus_response=corpus_result.get("response"),
            s1_response=s1_text,
            s2_response=s2_text,
            corpus_question_matched=corpus_result.get("matched_question"),
            corpus_category=corpus_result.get("category"),
            corpus_source=corpus_result.get("source"),
            similarity_score=corpus_result.get("similarity"),
            mistral_latency_ms=mistral_latency,
            corpus_latency_ms=corpus_result.get("latency_ms"),
            s1_latency_ms=s1_latency,
            s2_latency_ms=s2_latency,
            s2_risk_label=risk_label,
            temperature=body.temperature,
            top_p=body.top_p,
            max_tokens=body.max_tokens,
        )
        db.add(msg)

        if existing_count == 0:
            conv.title = body.query[:60]
        conv.updated_at = datetime.now(timezone.utc)

        await db.commit()
        await db.refresh(msg)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"DB error: {type(e).__name__}: {e}")

    return {
        "message": _msg_dict(msg),
        "mistral": {
            "response": mistral_text,
            "latency_ms": mistral_latency,
            "source": "S0: Mistral AI (mistral-small-latest)",
        },
        "corpus": {
            "response": corpus_result.get("response"),
            "key_points": corpus_result.get("key_points"),
            "matched_question": corpus_result.get("matched_question"),
            "category": corpus_result.get("category"),
            "source": corpus_result.get("source"),
            "similarity": corpus_result.get("similarity"),
            "latency_ms": corpus_result.get("latency_ms"),
            "found": corpus_result.get("found", False),
        },
        "s1": {
            "response": s1_text,
            "latency_ms": s1_latency,
            "source": "S1: Basic RAG",
        },
        "s2": {
            "response": s2_text,
            "latency_ms": s2_latency,
            "risk_label": risk_label,
            "source": "S2: Safety-aware RAG",
        },
    }


# ── Helper ────────────────────────────────────────────────────────────────────

def _msg_dict(m: Message) -> dict:
    return {
        "id": m.id,
        "conversation_id": m.conversation_id,
        "query": m.query,
        "mistral_response": m.mistral_response,
        "corpus_response": m.corpus_response,
        "s1_response": m.s1_response,
        "s2_response": m.s2_response,
        "corpus_question_matched": m.corpus_question_matched,
        "corpus_category": m.corpus_category,
        "corpus_source": m.corpus_source,
        "similarity_score": m.similarity_score,
        "mistral_latency_ms": m.mistral_latency_ms,
        "corpus_latency_ms": m.corpus_latency_ms,
        "s1_latency_ms": m.s1_latency_ms,
        "s2_latency_ms": m.s2_latency_ms,
        "s2_risk_label": m.s2_risk_label,
        "temperature": m.temperature,
        "top_p": m.top_p,
        "max_tokens": m.max_tokens,
        "created_at": m.created_at.isoformat(),
    }
