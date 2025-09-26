import asyncio
from sqlalchemy import select
from database.base import async_session
from database.models import Admin

async def main():
    async with async_session() as session:
        res = await session.execute(select(Admin.user_id))
        ids = [row[0] for row in res.all()]
        print("=== ADMINS ===")
        for uid in ids:
            print({"user_id": uid})

if __name__ == "__main__":
    asyncio.run(main())
