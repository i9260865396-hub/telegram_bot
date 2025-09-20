from aiogram import Router, types
from aiogram.filters import Command

router = Router()

@router.message(Command("start"))
async def welcome_handler(message: types.Message):
    await message.answer(
        "Привет! Я бот типографии.\n\n"
        "Доступные команды:\n"
        "- /order — новый заказ\n"
        "- /status — статус заказа\n"
        "- /admin — админ-панель"
    )
