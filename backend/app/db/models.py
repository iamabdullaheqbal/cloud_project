from datetime import datetime, timezone
from sqlalchemy import Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector
from app.db.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(80), default="New Conversation")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    messages: Mapped[list["Message"]] = relationship(
        "Message", back_populates="conversation", cascade="all, delete-orphan"
    )


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    conversation_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False
    )
    query: Mapped[str] = mapped_column(Text, nullable=False)
    mistral_response: Mapped[str | None] = mapped_column(Text, nullable=True)
    corpus_response: Mapped[str | None] = mapped_column(Text, nullable=True)
    s1_response: Mapped[str | None] = mapped_column(Text, nullable=True)
    s2_response: Mapped[str | None] = mapped_column(Text, nullable=True)
    corpus_question_matched: Mapped[str | None] = mapped_column(Text, nullable=True)
    corpus_category: Mapped[str | None] = mapped_column(String(120), nullable=True)
    corpus_source: Mapped[str | None] = mapped_column(Text, nullable=True)
    similarity_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    mistral_latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    corpus_latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    s1_latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    s2_latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    s2_risk_label: Mapped[str | None] = mapped_column(String(40), nullable=True)
    temperature: Mapped[float] = mapped_column(Float, default=0.4)
    top_p: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_tokens: Mapped[int] = mapped_column(Integer, default=800)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )

    conversation: Mapped["Conversation"] = relationship(
        "Conversation", back_populates="messages"
    )


class CorpusChunk(Base):
    __tablename__ = "corpus_chunks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    key_points: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(120), nullable=False)
    source: Mapped[str | None] = mapped_column(Text, nullable=True)
    embedding: Mapped[list[float]] = mapped_column(Vector(1024), nullable=True)
