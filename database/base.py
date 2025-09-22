from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config.settings import settings

# Используем SQLite (файл bot.db в корне проекта)
DATABASE_URL = "sqlite+aiosqlite:///./bot.db"

# Создаём движок
engine = create_async_engine(DATABASE_URL, echo=False, future=True)

# Асинхронная фабрика сессий
async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

# Базовый класс для моделей
Base = declarative_base()
