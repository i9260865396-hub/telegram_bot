import asyncio
from database.base import Base, engine, async_session
from database.models import Service


async def init_models():
    # создаём все таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # добавляем тестовую услугу, если таблица пустая
    async with async_session() as session:
        result = await session.execute("SELECT COUNT(*) FROM services")
        count = result.scalar()
        if count == 0:
            service = Service(name="Визитки", price=10.0, is_active=True)
            session.add(service)
            await session.commit()
            print("✅ Добавлена тестовая услуга: Визитки — 10 руб.")
        else:
            print("ℹ Услуги уже есть в базе, пропускаем.")


if __name__ == "__main__":
    asyncio.run(init_models())
