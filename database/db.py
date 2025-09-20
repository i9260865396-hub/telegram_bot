import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "bot.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


# ==== Работа с администраторами ====
def add_admin(user_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "CREATE TABLE IF NOT EXISTS admins (user_id INTEGER PRIMARY KEY)"
    )
    cur.execute(
        "INSERT OR IGNORE INTO admins (user_id) VALUES (?)", (user_id,)
    )
    conn.commit()
    conn.close()


def get_admins():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS admins (user_id INTEGER PRIMARY KEY)")
    cur.execute("SELECT user_id FROM admins")
    rows = cur.fetchall()
    conn.close()
    return [row[0] for row in rows]


# ==== Работа с заказами ====
def add_order(item: str, status: str = "новый"):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item TEXT,
            status TEXT
        )
        """
    )
    cur.execute("INSERT INTO orders (item, status) VALUES (?, ?)", (item, status))
    conn.commit()
    conn.close()


def get_all_orders():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item TEXT,
            status TEXT
        )
        """
    )
    cur.execute("SELECT id, item, status FROM orders ORDER BY id DESC LIMIT 10")
    rows = cur.fetchall()
    conn.close()
    return [{"id": r[0], "item": r[1], "status": r[2]} for r in rows]