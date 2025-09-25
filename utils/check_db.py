# utils/check_db.py
import sqlite3
from contextlib import closing

def dump_sqlite(db_path: str = "bot.db"):
    print(f"📦 SQLite файл: {db_path}")
    with closing(sqlite3.connect(db_path)) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        # Список таблиц
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY 1")
        tables = [r["name"] for r in cur.fetchall()]
        print("📂 Таблицы в базе:", tables or "— нет —")

        for t in tables:
            print(f"\n== 📑 {t} ==")
            # Структура
            cur.execute(f"PRAGMA table_info({t})")
            cols = cur.fetchall()
            for col in cols:
                pk = " PK" if col["pk"] else ""
                print(f"  - {col['name']} ({col['type']}){pk}")

            # Пять строк данных
            cur.execute(f"SELECT * FROM {t} LIMIT 5")
            rows = cur.fetchall()
            if rows:
                for r in rows:
                    print("  📝", dict(r))
            else:
                print("  — пусто —")

def try_orm_check():
    # Опционально: пробуем ORM. Если не получится — просто сообщим и идём дальше.
    try:
        import asyncio
        from sqlalchemy import select
        from database.base import async_session
        from database.models import Service, Order

        async def run():
            async with async_session() as s:
                svc = (await s.execute(select(Service))).scalars().all()
                print(f"\n✅ ORM: services = {len(svc)}")
                if svc:
                    print("  пример:", {"id": svc[0].id, "name": svc[0].name, "price": svc[0].price, "unit": svc[0].unit, "min_qty": svc[0].min_qty, "is_active": svc[0].is_active})

                ords = (await s.execute(select(Order).limit(1))).scalars().all()
                print(f"✅ ORM: orders = {len(ords)}")
                if ords:
                    print("  пример:", {"id": ords[0].id, "desc": ords[0].description, "status": ords[0].status})

        asyncio.run(run())
    except Exception as e:
        print(f"\nℹ️ ORM-проверку пропустили: {e}")

if __name__ == "__main__":
    dump_sqlite("bot.db")
    try_orm_check()
