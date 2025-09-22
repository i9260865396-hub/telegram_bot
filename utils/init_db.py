import asyncio
from database.base import engine, Base
from database import models  # noqa: F401
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    asyncio.run(init_db())
