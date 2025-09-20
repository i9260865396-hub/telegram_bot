# handlers/order.py
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

router = Router()


# === Определяем состояния для оформления заказа ===
class OrderFSM(StatesGroup):
    choosing_product = State()
    entering_quantity = State()
    confirming = State()


# === Клавиатуры ===
main_menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Новый заказ")],
        [KeyboardButton(text="Статус заказа")],
    ],
    resize_keyboard=True
)

cancel_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="❌ Отмена")]
    ],
    resize_keyboard=True
)


# === Старт нового заказа ===
@router.message(F.text == "Новый заказ")
async def start_order(message: Message, state: FSMContext):
    await state.set_state(OrderFSM.choosing_product)
    await message.answer(
        "Что будем печатать? (листовки, буклеты, баннеры...)\n\n"
        "Или нажмите ❌ Отмена",
        reply_markup=cancel_kb
    )


# === Ввод названия продукта ===
@router.message(OrderFSM.choosing_product, ~F.text.lower().contains("отмена"))
async def choose_product(message: Message, state: FSMContext):
    await state.update_data(product=message.text)
    await state.set_state(OrderFSM.entering_quantity)
    await message.answer("Укажите тираж (например: 1000 шт):")


# === Ввод количества ===
@router.message(OrderFSM.entering_quantity, ~F.text.lower().contains("отмена"))
async def enter_quantity(message: Message, state: FSMContext):
    await state.update_data(quantity=message.text)
    data = await state.get_data()

    await state.set_state(OrderFSM.confirming)
    await message.answer(
        f"Подтвердите заказ:\n"
        f"📦 Продукт: {data['product']}\n"
        f"🔢 Тираж: {data['quantity']}\n\n"
        f"Если всё верно, напишите «Подтверждаю» или ❌ Отмена"
    )


# === Подтверждение ===
@router.message(OrderFSM.confirming, F.text.lower() == "подтверждаю")
async def confirm_order(message: Message, state: FSMContext):
    data = await state.get_data()
    await message.answer(
        f"✅ Заказ принят!\n"
        f"📦 {data['product']}\n"
        f"🔢 {data['quantity']}",
        reply_markup=main_menu_kb
    )
    await state.clear()


# === Отмена на любом шаге ===
@router.message(F.text.lower().contains("отмена"))
async def cancel_order(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Заказ отменён", reply_markup=main_menu_kb)
