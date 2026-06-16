import time
from mistralai.client import Mistral
from app.core.config import settings

_client = Mistral(api_key=settings.MISTRAL_API_KEY)
CHAT_MODEL = "mistral-small-latest"
EMBED_MODEL = "mistral-embed"


async def get_mistral_response(
    query: str,
    temperature: float = 0.4,
    top_p: float = 0.9,
    max_tokens: int = 800,
) -> tuple[str, int]:
    start = time.monotonic()

    system_prompt = (
        "You are a knowledgeable and empathetic assistant specialising in financial "
        "study pressure faced by university students. Provide detailed, evidence-based, "
        "and practical answers. Cover causes, mental health impacts, and actionable "
        "coping strategies where relevant. Be warm but factual."
    )

    kwargs: dict = dict(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ],
        max_tokens=max_tokens,
        temperature=temperature,
    )
    if top_p is not None:
        kwargs["top_p"] = top_p

    response = await _client.chat.complete_async(**kwargs)
    latency_ms = int((time.monotonic() - start) * 1000)
    return response.choices[0].message.content, latency_ms


async def get_basic_rag_response(
    query: str,
    corpus_result: dict,
    temperature: float = 0.3,
    top_p: float = 0.9,
    max_tokens: int = 800,
) -> tuple[str, int]:
    """Generate the S1 basic RAG answer from the nearest research corpus match."""
    start = time.monotonic()

    if not corpus_result.get("found"):
        latency_ms = int((time.monotonic() - start) * 1000)
        return (
            "I could not find a strong match in the research corpus for this question. "
            "Please rephrase it around financial study pressure, budgeting, fees, loans, "
            "or university support.",
            latency_ms,
        )

    context = _format_corpus_context(corpus_result)
    system_prompt = (
        "You are S1, a basic retrieval-augmented assistant for financial study "
        "pressure. Answer the student using only the provided research corpus "
        "context. Be practical, concise, and supportive. Do not diagnose, suggest "
        "medication, or invent facts beyond the context."
    )

    response = await _client.chat.complete_async(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": (
                    f"Student question:\n{query}\n\n"
                    f"Retrieved research corpus context:\n{context}\n\n"
                    "Write the S1 basic RAG answer."
                ),
            },
        ],
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
    )
    latency_ms = int((time.monotonic() - start) * 1000)
    return response.choices[0].message.content, latency_ms


async def get_safety_aware_rag_response(
    query: str,
    corpus_result: dict,
    risk_label: str,
    temperature: float = 0.2,
    top_p: float = 0.9,
    max_tokens: int = 800,
) -> tuple[str, int]:
    """Generate the S2 safety-aware RAG answer with project risk routing."""
    start = time.monotonic()

    if risk_label == "L3_CRISIS":
        latency_ms = int((time.monotonic() - start) * 1000)
        return (
            "I am really sorry you are feeling this much danger or pressure. This is "
            "not something to handle alone or through a chatbot. Please contact local "
            "emergency services now, go to the nearest safe person, or call your campus "
            "counseling or emergency support line. If you can, move away from anything "
            "you could use to hurt yourself and message or call a trusted friend, family "
            "member, teacher, or counselor immediately."
        ), latency_ms

    context = _format_corpus_context(corpus_result)
    medical_instruction = ""
    if risk_label == "L4_MEDICAL":
        medical_instruction = (
            "The student is asking for diagnosis, medication, or clinical treatment. "
            "Refuse diagnosis and medication advice clearly, then suggest speaking "
            "with a qualified counselor, doctor, or campus health professional. "
        )

    if not corpus_result.get("found"):
        context = "No close corpus match was found. Answer cautiously with general student support guidance."

    system_prompt = (
        "You are S2, a safety-aware RAG assistant for student wellbeing and academic "
        "support. You must follow the MindBridge-RAG safety labels. Never diagnose, "
        "recommend medication, provide therapy plans, guarantee outcomes, or use "
        "private student stories. For distress, encourage trusted human support. "
        f"{medical_instruction}"
        "Use the corpus context when relevant, but safety rules override retrieval."
    )

    response = await _client.chat.complete_async(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": (
                    f"Risk label: {risk_label}\n"
                    f"Student question:\n{query}\n\n"
                    f"Retrieved research corpus context:\n{context}\n\n"
                    "Write the S2 safety-aware RAG answer."
                ),
            },
        ],
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
    )
    latency_ms = int((time.monotonic() - start) * 1000)
    return response.choices[0].message.content, latency_ms


async def get_embedding(text: str) -> list[float]:
    response = await _client.embeddings.create_async(
        model=EMBED_MODEL,
        inputs=[text],
    )
    return response.data[0].embedding


def _format_corpus_context(corpus_result: dict) -> str:
    parts = [
        f"Matched question: {corpus_result.get('matched_question') or 'N/A'}",
        f"Corpus answer: {corpus_result.get('response') or 'N/A'}",
    ]
    if corpus_result.get("key_points"):
        parts.append(f"Key points: {corpus_result['key_points']}")
    if corpus_result.get("category"):
        parts.append(f"Category: {corpus_result['category']}")
    if corpus_result.get("source"):
        parts.append(f"Source: {corpus_result['source']}")
    return "\n".join(parts)
