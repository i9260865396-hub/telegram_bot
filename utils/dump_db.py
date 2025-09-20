import asyncio
from sqlalchemy import select
from database.db import SessionLocal
from database.models import Admin, Order

async def run():
    async with SessionLocal() as session:
        admins = (await session.execute(select(Admin))).scalars().all()
        orders = (await session.execute(select(Order))).scalars().all()
    print("=== ADMINS ===")
    for a in admins:
        print({"user_id": a.user_id})
    print("\n=== ORDERS ===")
    for o in orders:
        print({"id": o.id, "user_id": o.user_id, "status": o.status, "desc": o.description[:80]})

if __name__ == "__main__":
    asyncio.run(run())
