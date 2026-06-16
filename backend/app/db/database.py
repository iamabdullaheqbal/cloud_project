from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text
from app.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_size=10,
    max_overflow=20,
)
AsyncSessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(
            text("ALTER TABLE messages ADD COLUMN IF NOT EXISTS s1_response TEXT")
        )
        await conn.execute(
            text("ALTER TABLE messages ADD COLUMN IF NOT EXISTS s2_response TEXT")
        )
        await conn.execute(
            text("ALTER TABLE messages ADD COLUMN IF NOT EXISTS s1_latency_ms INTEGER")
        )
        await conn.execute(
            text("ALTER TABLE messages ADD COLUMN IF NOT EXISTS s2_latency_ms INTEGER")
        )
        await conn.execute(
            text("ALTER TABLE messages ADD COLUMN IF NOT EXISTS s2_risk_label VARCHAR(40)")
        )
