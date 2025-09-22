from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from sqlalchemy.future import select
from database.base import async_session
from database.models import Order, Service

router = Router()


# === FSM для изменения цены ===
class PriceEdit(StatesGroup):
    waiting_for_price = State()


# === 💰 Цены (список услуг с кнопками) ===
@router.message(lambda msg: msg.text == "💰 Цены")
async def show_services(message: types.Message):
    async with async_session() as session:
        result = await session.execute(select(Service).order_by(Service.id))
        services = result.scalars().all()

    if not services:
        await message.answer("❌ В базе пока нет услуг.")
        return

    for s in services:
        status = "✅ вкл" if s.is_active else "❌ выкл"
        kb = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(text="✏ Изменить цену", callback_data=f"edit_price:{s.id}")]
            ]
        )
        await message.answer(
            f"• {s.name} — {s.price} руб. ({status})",
            reply_markup=kb
        )


# === Обработка кнопки "✏ Изменить цену" ===
@router.callback_query(F.data.startswith("edit_price:"))
async def ask_new_price(callback: types.CallbackQuery, state: FSMContext):
    service_id = int(callback.data.split(":")[1])
    await state.update_data(service_id=service_id)
    await state.set_state(PriceEdit.waiting_for_price)
    await callback.message.answer("Введите новую цену для этой услуги:")
    await callback.answer()


# === Приём новой цены ===
@router.message(PriceEdit.waiting_for_price, F.text.regexp(r"^\d+(\.\d+)?$"))
async def save_new_price(message: types.Message, state: FSMContext):
    data = await state.get_data()
    service_id = data["service_id"]
    new_price = float(message.text)

    async with async_session() as session:
        result = await session.execute(select(Service).where(Service.id == service_id))
        service = result.scalar_one_or_none()
        if service:
            service.price = new_price
            await session.commit()
            await message.answer(f"✅ Цена изменена: {service.name} — {service.price} руб.")
        else:
            await message.answer("❌ Ошибка: услуга не найдена.")

    await state.clear()


# === Если ввели не число ===
@router.message(PriceEdit.waiting_for_price)
async def wrong_price_input(message: types.Message):
    await message.answer("❗ Введите корректное число (например: 15 или 15.5)")
