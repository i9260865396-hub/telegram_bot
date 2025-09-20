import asyncio
from database.db import engine, Base
from database import models  # noqa

async def run():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Migrations applied")

if __name__ == "__main__":
    asyncio.run(run())
