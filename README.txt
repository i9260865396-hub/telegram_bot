Telegram Print Bot — Ready Package (Aiogram 3)

Шаги запуска (Windows):
1) Python 3.13 установлен и в PATH.
2) scripts\install_deps_once.bat — создаст venv и поставит зависимости.
3) Скопируйте .env.example в .env, заполните BOT_TOKEN и ADMIN_IDS (через запятую).
4) scripts\start_bot.bat — запуск.
5) scripts\start_daily.bat — автозапуск через Планировщик.

Особенности:
- Aiogram 3.x (>=3.20,<3.23), без объединения фильтров через |
- DefaultBotProperties(parse_mode=HTML)
- SQLite (async) через SQLAlchemy 2 + aiosqlite
- Логи в logs/bot.log
