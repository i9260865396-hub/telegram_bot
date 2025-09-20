import sys
from database.db import add_admin

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Использование: python -m utils.seed_admin add <user_id>")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "add":
        try:
            user_id = int(sys.argv[2])
            add_admin(user_id)
            print(f"✅ Админ {user_id} добавлен")
        except ValueError:
            print("Ошибка: user_id должен быть числом")
