import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config.settings import settings
from config.logger import setup_logging
from database.migrate import run as migrate_run
from handlers import welcome, order, status, admin, grant_admin, admin_orders

async def main():
    setup_logging()
    logging.getLogger(__name__).info("Starting bot...")
    await migrate_run()

    bot = Bot(token=settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(welcome.router)
    dp.include_router(order.router)
    dp.include_router(status.router)
    dp.include_router(admin.router)
    dp.include_router(grant_admin.router)
    dp.include_router(admin_orders.router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
