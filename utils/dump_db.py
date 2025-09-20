from database.db import get_admins, get_all_orders

if __name__ == "__main__":
    print("=== ADMINS ===")
    admins = get_admins()
    if not admins:
        print("Пока админов нет")
    else:
        for a in admins:
            print({"user_id": a})

    print("\n=== ORDERS ===")
    orders = get_all_orders()
    if not orders:
        print("Пока заказов нет")
    else:
        for o in orders:
            print(o)
