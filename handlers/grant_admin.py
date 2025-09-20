from aiogram import Router
from aiogram.filters import CommandObject, Command
from aiogram.types import Message
from sqlalchemy import select
from database.db import SessionLocal
from database.models import Admin
from config.settings import settings

router = Router(name="grant_admin")

@router.message(Command("grant_admin"))
async def grant_admin(message: Message, command: CommandObject):
    if message.from_user.id not in settings.admin_ids:
        await message.answer("⛔ Доступ запрещен.")
        return
    if not command.args:
        await message.answer("Использование: /grant_admin <user_id>")
        return
    try:
        uid = int(command.args.strip())
    except:
        await message.answer("Неверный user_id")
        return
    async with SessionLocal() as session:
        res = await session.execute(select(Admin).where(Admin.user_id == uid))
        exists = res.scalar_one_or_none()
        if exists is None:
            session.add(Admin(user_id=uid))
            await session.commit()
    if uid not in settings.admin_ids:
        settings.admin_ids.append(uid)
    await message.answer(f"✅ Пользователь {uid} теперь админ.")
