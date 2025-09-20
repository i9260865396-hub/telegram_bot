from aiogram import Router, F
from aiogram.types import Message
from config.settings import settings

router = Router(name="admin")

@router.message(F.text == "🛠 Админка")
async def admin_entry(message: Message):
    if message.from_user.id not in settings.admin_ids:
        await message.answer("⛔ У вас нет прав доступа.")
        return
    await message.answer("Админка: /admin_orders — последние заказы, /grant_admin <id> — выдать права")
