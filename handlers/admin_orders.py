from aiogram import Router, types
from aiogram.filters import Command
from config.settings import settings

router = Router()

@router.message(Command("orders"))
async def admin_orders(message: types.Message):
    if message.from_user.id not in settings.get_admin_ids():
        await message.answer("У тебя нет прав доступа")
        return
    await message.answer("Здесь список заказов (заглушка)")
