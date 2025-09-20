import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import settings
from handlers import welcome, admin  # при желании добавишь и другие роутеры


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    # ВАЖНО: создаём бота (раньше здесь у тебя было "..." и ничего не инициализировалось)
    bot = Bot(
        token=settings.bot_token,  # alias для BOT_TOKEN из .env
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    dp = Dispatcher()

    # Подключаем роутеры
    dp.include_router(welcome.router)
    dp.include_router(admin.router)

    logging.info("Starting bot...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped")