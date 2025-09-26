import sys, asyncio
from database.base import async_session
from database.models import Admin

async def del_admin(user_id: int):
    async with async_session() as session:
        obj = await session.get(Admin, user_id)
        if not obj:
            print(f"⚠️ Админа {user_id} нет")
            return
        await session.delete(obj)
        await session.commit()
        print(f"✅ Админ {user_id} удалён")

if __name__ == "__main__":
    if len(sys.argv) != 2 or not sys.argv[1].isdigit():
        print("Использование: python -m utils.del_admin <user_id>")
        sys.exit(1)
    asyncio.run(del_admin(int(sys.argv[1])))
