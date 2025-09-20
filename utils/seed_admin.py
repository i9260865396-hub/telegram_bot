import asyncio
from sqlalchemy import select
from database.db import SessionLocal
from database.models import Admin
from config.settings import settings

async def run():
    async with SessionLocal() as session:
        for uid in settings.admin_ids:
            res = await session.execute(select(Admin).where(Admin.user_id == uid))
            if res.scalar_one_or_none() is None:
                session.add(Admin(user_id=uid))
        await session.commit()
    print("✅ Таблица admins: администраторы добавлены:", settings.admin_ids)

if __name__ == "__main__":
    asyncio.run(run())
