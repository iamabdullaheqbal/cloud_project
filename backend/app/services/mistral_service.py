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


async def get_embedding(text: str) -> list[float]:
    response = await _client.embeddings.create_async(
        model=EMBED_MODEL,
        inputs=[text],
    )
    return response.data[0].embedding
