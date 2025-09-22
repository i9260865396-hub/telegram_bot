import os

print("Из .env прочитан ADMIN_IDS:")
print(os.getenv("ADMIN_IDS"))

print("\n⚡ Подсказка:")
print("1. Убедись, что твой user_id (из Telegram) есть в этом списке.")
print("2. В .env можно писать через запятую или точку с запятой, например:")
print("   ADMIN_IDS=123456789,987654321")
