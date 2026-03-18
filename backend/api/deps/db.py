"""Database dependency for API routes."""

from sqlalchemy.ext.asyncio import AsyncSession

from backend.config.database import get_db


async def get_db_session() -> AsyncSession:
    async for session in get_db():
        return session
    raise RuntimeError("failed to create db session")

