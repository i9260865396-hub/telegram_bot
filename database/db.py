from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from config.settings import settings


class Base(DeclarativeBase):
    """Base declarative class for SQLAlchemy models."""


engine: AsyncEngine = create_async_engine(settings.database_url)
async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

__all__ = [
    "Base",
    "engine",
    "async_session_factory",
]
