from aiogram import Router, types
from aiogram.filters import Command

router = Router()

@router.message(Command("status"))
async def status_handler(message: types.Message):
    await message.answer("Проверка статуса заказа (заглушка)")
