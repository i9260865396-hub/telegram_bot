from aiogram import Router, types
from aiogram.filters import Command
from database.db import get_admins

router = Router()


@router.message(Command("admin"))
async def admin_entry(message: types.Message):
    if message.from_user.id not in get_admins():
        await message.answer("❌ У вас нет прав доступа")
        return

    await message.answer(
        "Админка:\n"
        "/admin_orders — последние заказы\n"
        "/grant_admin ID — выдать права"
    )