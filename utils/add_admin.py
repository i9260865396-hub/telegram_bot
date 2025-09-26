import sys, asyncio
from database.base import async_session
from database.models import Admin

async def add_admin(user_id: int):
    async with async_session() as session:
        exists = await session.get(Admin, user_id)
        if exists:
            print(f"⚠️ Админ {user_id} уже есть")
            return
        session.add(Admin(user_id=user_id))
        await session.commit()
        print(f"✅ Админ {user_id} добавлен")

if __name__ == "__main__":
    if len(sys.argv) != 2 or not sys.argv[1].isdigit():
        print("Использование: python -m utils.add_admin <user_id>")
        sys.exit(1)
    asyncio.run(add_admin(int(sys.argv[1])))
