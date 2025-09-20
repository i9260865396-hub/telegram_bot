from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import select
from database.db import SessionLocal
from database.models import Order
from config.settings import settings

router = Router(name="admin_orders")

@router.message(Command("admin_orders"))
async def admin_orders(message: Message):
    if message.from_user.id not in settings.admin_ids:
        await message.answer("⛔ Доступ запрещен.")
        return
    async with SessionLocal() as session:
        res = await session.execute(select(Order).order_by(Order.id.desc()).limit(20))
        orders = res.scalars().all()
    if not orders:
        await message.answer("Заказов пока нет.")
        return
    lines = [f"Последние {len(orders)} заказов:"]
    for o in orders:
        lines.append(f"#{o.id} [{o.status}] {o.description[:120]} (user {o.user_id})")
    await message.answer("\n".join(lines))
