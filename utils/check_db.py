import sqlite3

conn = sqlite3.connect("bot.db")
cursor = conn.cursor()

# Проверяем список таблиц
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("📂 Таблицы в базе:", tables)

if ("orders",) in tables:
    print("✅ Таблица 'orders' существует")

    # Проверяем структуру таблицы
    cursor.execute("PRAGMA table_info(orders);")
    columns = cursor.fetchall()
    print("📑 Структура таблицы 'orders':")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")

    # Мини-тест: попробуем выбрать 1 строку
    cursor.execute("SELECT * FROM orders LIMIT 1;")
    row = cursor.fetchone()
    print("📝 Пример данных:", row if row else "Пока пусто")
else:
    print("❌ Таблица 'orders' не найдена")
