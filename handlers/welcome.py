from aiogram import Router, types
from aiogram.filters import Command

router = Router()


@router.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("👋 Привет! Это бот для заказов печати.\n\nДоступные команды:\n/start — перезапуск\n/admin — админка (для админов)")