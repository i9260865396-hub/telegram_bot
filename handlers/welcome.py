from aiogram import Router, types
from aiogram.filters import Command

router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Привет! Это бот для заказов печати.\n\n"
        "Доступные команды:\n"
        "/start — начать заново\n"
        "/admin — вход в админку (для админов)"
    )
