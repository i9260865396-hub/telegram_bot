from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy import select
from database.db import SessionLocal
from database.models import Order

router = Router(name="status")

@router.message(F.text == "📦 Статус заказа")
async def status_menu(message: Message):
    user_id = message.from_user.id
    async with SessionLocal() as session:
        res = await session.execute(select(Order).where(Order.user_id == user_id).order_by(Order.id.desc()).limit(5))
        orders = res.scalars().all()
    if not orders:
        await message.answer("У вас пока нет заказов.")
        return
    text = ["Ваши последние заказы:"]
    for o in orders:
        text.append(f"#{o.id} — {o.status}: {o.description[:200]}")
    await message.answer("\n".join(text))
