from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from sqlalchemy import select, update
from database.base import async_session
from database.models import Order, Service
from config.settings import settings

router = Router()


# =======================
#   helpers / keyboards
# =======================

def is_admin(user_id: int) -> bool:
    try:
        return user_id in settings.get_admin_ids()
    except Exception:
        return False


def admin_main_kb() -> types.ReplyKeyboardMarkup:
    return types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="📦 Заказы")],
            [types.KeyboardButton(text="⚙ Настройки")],
            [types.KeyboardButton(text="🚪 Отмена")],
        ],
        resize_keyboard=True
    )


def settings_kb() -> types.ReplyKeyboardMarkup:
    # компактное меню настроек (как договорились)
    return types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="💰 Цены / Услуги")],
            [types.KeyboardButton(text="⏰ Сроки"), types.KeyboardButton(text="📦 Доставка")],
            [types.KeyboardButton(text="👨‍💻 Админы"), types.KeyboardButton(text="🤖 Инструменты ИИ")],
            [types.KeyboardButton(text="📢 Уведомления"), types.KeyboardButton(text="📊 Статистика")],
            [types.KeyboardButton(text="📂 Архив заказов"), types.KeyboardButton(text="⚡ Системные параметры")],
            [types.KeyboardButton(text="🔑 API"), types.KeyboardButton(text="🔙 Назад")],
        ],
        resize_keyboard=True
    )


def services_list_kb(items: list[Service]) -> types.InlineKeyboardMarkup:
    # строим inline-клавиатуру: по 2 кнопки в ряд
    rows: list[list[types.InlineKeyboardButton]] = []
    line: list[types.InlineKeyboardButton] = []
    for svc in items:
        btn = types.InlineKeyboardButton(text=svc.name, callback_data=f"svc:open:{svc.id}")
        line.append(btn)
        if len(line) == 2:
            rows.append(line)
            line = []
    if line:
        rows.append(line)
    # низ — назад
    rows.append([types.InlineKeyboardButton(text="🔙 Назад", callback_data="svc:back")])
    return types.InlineKeyboardMarkup(inline_keyboard=rows)


def service_card_text(s: Service) -> str:
    status = "✅ активна" if s.is_active else "❌ выключена"
    return (
        f"✏ <b>{s.name}</b>\n"
        f"Цена: <b>{s.price}</b> руб./{s.unit}\n"
        f"Мин. тираж: <b>{s.min_qty}</b>\n"
        f"Статус: {status}"
    )


def service_card_kb(svc_id: int, is_active: bool) -> types.InlineKeyboardMarkup:
    toggle_text = "🔴 Выключить" if is_active else "🟢 Включить"
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="✏ Изменить цену", callback_data=f"svc:ask_price:{svc_id}")],
            [types.InlineKeyboardButton(text="🔢 Изменить минималку", callback_data=f"svc:ask_min:{svc_id}")],
            [types.InlineKeyboardButton(text="📏 Единица (шт./м/м²)", callback_data=f"svc:ask_unit:{svc_id}")],
            [types.InlineKeyboardButton(text=toggle_text, callback_data=f"svc:toggle:{svc_id}")],
            [types.InlineKeyboardButton(text="🔙 К списку услуг", callback_data="svc:list")],
        ]
    )


# единицы измерения (код -> человекочитаемое)
UNIT_OPTIONS = {
    "pcs": "шт.",
    "m": "м",
    "m2": "м²",
}


def units_kb(svc_id: int) -> types.InlineKeyboardMarkup:
    row = [
        types.InlineKeyboardButton(text=label, callback_data=f"svc:set_unit:{svc_id}:{code}")
        for code, label in UNIT_OPTIONS.items()
    ]
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            row,
            [types.InlineKeyboardButton(text="🔙 Назад", callback_data=f"svc:open:{svc_id}")]
        ]
    )


# =======================
#          FSM
# =======================

class PriceEdit(StatesGroup):
    waiting_for_price = State()


class MinQtyEdit(StatesGroup):
    waiting_for_min = State()


# =======================
#       /admin & menu
# =======================

@router.message(Command("admin"))
async def admin_menu(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ У вас нет доступа.")
        return
    await message.answer("Админ-панель:", reply_markup=admin_main_kb())


@router.message(F.text == "🚪 Отмена")
async def cancel_action(message: types.Message, state: FSMContext):
    await state.clear()
    if not is_admin(message.from_user.id):
        return
    await message.answer("Действие отменено. Возврат в админку.", reply_markup=admin_main_kb())


@router.message(F.text == "⚙ Настройки")
async def settings_menu(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ У вас нет доступа.")
        return
    await message.answer("Раздел настроек:", reply_markup=settings_kb())


@router.message(F.text == "🔙 Назад")
async def back_to_admin(message: types.Message, state: FSMContext):
    await state.clear()
    if not is_admin(message.from_user.id):
        return
    await message.answer("Админ-панель:", reply_markup=admin_main_kb())


# =======================
#         Заказы
# =======================

@router.message(F.text == "📦 Заказы")
async def show_orders(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ У вас нет доступа.")
        return
    async with async_session() as session:
        result = await session.execute(select(Order).order_by(Order.created_at.desc()).limit(5))
        orders = result.scalars().all()

    if not orders:
        await message.answer("📦 Заказов пока нет.")
        return

    text = "📋 Последние заказы:\n\n"
    for o in orders:
        text += f"#{o.id} — {o.description}\nСтатус: {o.status}\n\n"
    await message.answer(text)


# =======================
#   Цены / Услуги (список)
# =======================

@router.message(F.text == "💰 Цены / Услуги")
async def services_list(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ У вас нет доступа.")
        return
    async with async_session() as session:
        result = await session.execute(select(Service).order_by(Service.id))
        services = result.scalars().all()

    if not services:
        await message.answer("❌ В базе пока нет услуг.")
        return

    # одно сообщение + inline-кнопки
    lines = ["📋 Услуги:"]
    for s in services:
        lines.append(f"• {s.name} — {s.price} руб./{s.unit} (мин. {s.min_qty})")
    text = "\n".join(lines)

    await message.answer(text, reply_markup=services_list_kb(services))


# Показ карточки услуги
@router.callback_query(F.data.startswith("svc:open:"))
async def open_service(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return
    svc_id = int(callback.data.split(":")[2])
    async with async_session() as session:
        res = await session.execute(select(Service).where(Service.id == svc_id))
        svc = res.scalar_one_or_none()
    if not svc:
        await callback.answer("Услуга не найдена", show_alert=True)
        return

    await callback.message.edit_text(
        service_card_text(svc),
        reply_markup=service_card_kb(svc.id, svc.is_active),
        parse_mode="HTML"
    )
    await callback.answer()


# Вернуться к списку услуг
@router.callback_query(F.data == "svc:list")
async def back_to_list(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return
    async with async_session() as session:
        result = await session.execute(select(Service).order_by(Service.id))
        services = result.scalars().all()
    if not services:
        await callback.message.edit_text("❌ В базе пока нет услуг.")
        await callback.answer()
        return

    lines = ["📋 Услуги:"]
    for s in services:
        lines.append(f"• {s.name} — {s.price} руб./{s.unit} (мин. {s.min_qty})")
    text = "\n".join(lines)

    await callback.message.edit_text(text, reply_markup=services_list_kb(services))
    await callback.answer()


# Назад из списка (к настройкам)
@router.callback_query(F.data == "svc:back")
async def list_back(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return
    # вместо отдельного сообщения — просто отвечаем и просим нажать «🔙 Назад» в клавиатуре
    await callback.message.edit_text("Раздел настроек:", reply_markup=None)
    # отправим новое сообщение с reply-клавиатурой настроек
    await callback.message.answer("Раздел настроек:", reply_markup=settings_kb())
    await callback.answer()


# =======================
#     Тоггл активности
# =======================

@router.callback_query(F.data.startswith("svc:toggle:"))
async def toggle_service(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return
    svc_id = int(callback.data.split(":")[2])

    async with async_session() as session:
        res = await session.execute(select(Service).where(Service.id == svc_id))
        svc = res.scalar_one_or_none()
        if not svc:
            await callback.answer("Услуга не найдена", show_alert=True)
            return
        new_val = not svc.is_active
        await session.execute(
            update(Service).where(Service.id == svc_id).values(is_active=new_val)
        )
        await session.commit()
        svc.is_active = new_val  # для обновлённой карточки

    await callback.message.edit_text(
        service_card_text(svc),
        reply_markup=service_card_kb(svc.id, svc.is_active),
        parse_mode="HTML"
    )
    await callback.answer("Готово")


# =======================
#     Изменение цены
# =======================

@router.callback_query(F.data.startswith("svc:ask_price:"))
async def ask_price(callback: types.CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return
    svc_id = int(callback.data.split(":")[2])
    await state.update_data(service_id=svc_id)
    await state.set_state(PriceEdit.waiting_for_price)
    await callback.answer()
    await callback.message.answer("Введите новую цену (число, например 15 или 15.5):")


@router.message(PriceEdit.waiting_for_price, F.text.regexp(r"^\d+(\.\d+)?$"))
async def save_price(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    data = await state.get_data()
    svc_id = int(data["service_id"])
    new_price = float(message.text)

    async with async_session() as session:
        res = await session.execute(select(Service).where(Service.id == svc_id))
        svc = res.scalar_one_or_none()
        if not svc:
            await message.answer("❌ Услуга не найдена.")
            await state.clear()
            return
        await session.execute(update(Service).where(Service.id == svc_id).values(price=new_price))
        await session.commit()
        svc.price = new_price

    await message.answer(f"✅ Цена обновлена: {svc.name} — {svc.price} руб./{svc.unit}")
    await state.clear()


@router.message(PriceEdit.waiting_for_price)
async def wrong_price(message: types.Message):
    if not is_admin(message.from_user.id):
        return
    await message.answer("❗ Введите корректное число (пример: 12 или 12.5)")


# =======================
#   Изменение минималки
# =======================

@router.callback_query(F.data.startswith("svc:ask_min:"))
async def ask_min(callback: types.CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return
    svc_id = int(callback.data.split(":")[2])
    await state.update_data(service_id=svc_id)
    await state.set_state(MinQtyEdit.waiting_for_min)
    await callback.answer()
    await callback.message.answer("Введите минимальный тираж (целое число, например 100):")


@router.message(MinQtyEdit.waiting_for_min, F.text.regexp(r"^\d+$"))
async def save_min(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    data = await state.get_data()
    svc_id = int(data["service_id"])
    new_min = int(message.text)

    async with async_session() as session:
        res = await session.execute(select(Service).where(Service.id == svc_id))
        svc = res.scalar_one_or_none()
        if not svc:
            await message.answer("❌ Услуга не найдена.")
            await state.clear()
            return
        await session.execute(update(Service).where(Service.id == svc_id).values(min_qty=new_min))
        await session.commit()
        svc.min_qty = new_min

    await message.answer(f"✅ Минимальный тираж обновлён: {svc.name} — мин. {svc.min_qty}")
    await state.clear()


@router.message(MinQtyEdit.waiting_for_min)
async def wrong_min(message: types.Message):
    if not is_admin(message.from_user.id):
        return
    await message.answer("❗ Нужно целое число (например 100)")


# =======================
#   Изменение единицы
# =======================

@router.callback_query(F.data.startswith("svc:ask_unit:"))
async def ask_unit(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return
    svc_id = int(callback.data.split(":")[2])
    await callback.message.answer("Выберите единицу измерения:", reply_markup=units_kb(svc_id))
    await callback.answer()


@router.callback_query(F.data.startswith("svc:set_unit:"))
async def set_unit(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return
    _, _, svc_id_str, unit_code = callback.data.split(":")
    svc_id = int(svc_id_str)
    unit_value = UNIT_OPTIONS.get(unit_code, "шт.")

    async with async_session() as session:
        res = await session.execute(select(Service).where(Service.id == svc_id))
        svc = res.scalar_one_or_none()
        if not svc:
            await callback.answer("Услуга не найдена", show_alert=True)
            return
        await session.execute(update(Service).where(Service.id == svc_id).values(unit=unit_value))
        await session.commit()
        svc.unit = unit_value

    # после смены единицы — вернёмся в карточку
    await callback.message.edit_text(
        service_card_text(svc),
        reply_markup=service_card_kb(svc.id, svc.is_active),
        parse_mode="HTML"
    )
    await callback.answer("Готово")


# =======================
#  Фоллбек (чтобы не молчал)
# =======================

@router.message()
async def fallback_admin(message: types.Message):
    if is_admin(message.from_user.id) and message.text:
        await message.answer("❗ Используй кнопки меню для навигации.")
