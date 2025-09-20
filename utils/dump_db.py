from database import db

def dump():
    admins = db.get_admins()
    orders = db.get_orders()

    print("=== ADMINS ===")
    for admin in admins:
        print(admin)

    print("\n=== ORDERS ===")
    for order in orders:
        print(order)


if __name__ == "__main__":
    dump()
