# utils/dump_db.py

import asyncio
from database.base import async_session
from database.models import Admin, Order, Service
from sqlalchemy import select

async def dump_async():
    async with async_session() as session:
        print("=== ADMINS ===")
        res = await session.execute(select(Admin))
        for row in res.scalars().all():
            print({"user_id": row.user_id})

        print("\n=== ORDERS ===")
        res = await session.execute(select(Order))
        for row in res.scalars().all():
            print({"id": row.id, "user_id": row.user_id, "status": row.status})

        print("\n=== SERVICES ===")
        res = await session.execute(select(Service))
        for row in res.scalars().all():
            print({"id": row.id, "name": row.name, "price": row.price})

def dump():
    asyncio.run(dump_async())

if __name__ == "__main__":
    dump()
