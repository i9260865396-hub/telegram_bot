from aiogram import Router, F
from aiogram.types import Message
from database.db import SessionLocal
from database.models import Order

router = Router(name="order")

@router.message(F.text == "🆕 Новый заказ")
async def order_start(message: Message):
    await message.answer("Опишите, что нужно напечатать (одним сообщением):")

# Любой обычный текст (не команда и не пункты меню) становится заказом
@router.message(F.text & ~F.text.startswith("/") & (F.text != "🆕 Новый заказ") & (F.text != "📦 Статус заказа") & (F.text != "🛠 Админка"))
async def capture_description(message: Message):
    desc = message.text.strip()
    if not desc:
        return
    async with SessionLocal() as session:
        order = Order(user_id=message.from_user.id, description=desc, status="new")
        session.add(order)
        await session.commit()
        await session.refresh(order)
    await message.answer(f"✅ Заказ #{order.id} создан. Мы свяжемся с вами в чате.")
