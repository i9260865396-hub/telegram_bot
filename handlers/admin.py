from aiogram import Router, types
from aiogram.filters import Command
from config.settings import settings

router = Router()

@router.message(Command("admin"))
async def admin_panel(message: types.Message):
    if message.from_user.id not in settings.get_admin_ids():
        await message.answer("У тебя нет прав доступа")
        return
    await message.answer("Добро пожаловать в админ-панель!")
