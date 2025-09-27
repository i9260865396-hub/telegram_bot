# handlers/admin.py
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from sqlalchemy import select

from config.settings import settings
from database.base import async_session
from database.models import Order, Service, Admin

router = Router()

# =======================
#   helpers / keyboards
# =======================

async def is_admin(user_id: int) -> bool:
    async with async_session() as session:
        res = await session.execute(select(Admin.user_id).where(Admin.user_id == user_id))
        return res.scalar_one_or_none() is not None

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

# ---- Услуги ----
def services_list_kb(items: list[Service]) -> types.InlineKeyboardMarkup:
    rows: list[list[types.InlineKeyboardButton]] = []
    line: list[types.InlineKeyboardButton] = []
    for svc in items:
        btn = types.InlineKeyboardButton(text=svc.name, callback_data=f"svc:open:{svc.id}")
        line.append(btn)
        if len(line) == 2:
            rows.append(line); line = []
    if line:
        rows.append(line)
    rows.append([types.InlineKeyboardButton(text="➕ Добавить услугу", callback_data="svc:add")])
    rows.append([types.InlineKeyboardButton(text="🔙 Назад в настройки", callback_data="svc:back")])
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
            [types.InlineKeyboardButton(text="❌ Удалить услугу", callback_data=f"svc:delete:{svc_id}")],
            [types.InlineKeyboardButton(text="🔙 К списку услуг", callback_data="svc:list")],
        ]
    )

UNIT_OPTIONS = {"pcs": "шт.", "m": "м", "m2": "м²"}

def units_kb(svc_id: int) -> types.InlineKeyboardMarkup:
    row = [
        types.InlineKeyboardButton(text=label, callback_data=f"svc:set_unit:{svc_id}:{code}")
        for code, label in UNIT_OPTIONS.items()
    ]
    return types.InlineKeyboardMarkup(
        inline_keyboard=[row, [types.InlineKeyboardButton(text="🔙 Назад", callback_data=f"svc:open:{svc_id}")]]
    )

# =======================
#          FSM
# =======================

class PriceEdit(StatesGroup):
    waiting_for_price = State()

class MinQtyEdit(StatesGroup):
    waiting_for_min = State()

class AddService(StatesGroup):
    waiting_for_name = State()
    waiting_for_price = State()
    waiting_for_unit = State()
    waiting_for_min = State()

class DeadlinesEdit(StatesGroup):
    waiting_for_deadline = State()

# =======================
#       /admin & menu
# =======================

@router.message(Command("admin"))
async def admin_menu(message: types.Message, state: FSMContext):
    if not await is_admin(message.from_user.id):
        await message.answer("⛔ У вас нет доступа."); return
    await state.clear()
    await message.answer("Админ-панель:", reply_markup=admin_main_kb())

@router.message(F.text == "🚪 Отмена")
async def cancel_action(message: types.Message, state: FSMContext):
    await state.clear()
    if not await is_admin(message.from_user.id): return
    await message.answer("Действие отменено. Возврат в админку.", reply_markup=admin_main_kb())

@router.message(F.text == "⚙ Настройки")
async def settings_menu(message: types.Message, state: FSMContext):
    if not await is_admin(message.from_user.id):
        await message.answer("⛔ У вас нет доступа."); return
    await state.clear()
    await message.answer("Раздел настроек:", reply_markup=settings_kb())

@router.message(F.text == "🔙 Назад")
async def back_to_admin(message: types.Message, state: FSMContext):
    if not await is_admin(message.from_user.id): return
    await state.clear()
    await message.answer("Возврат в админку:", reply_markup=admin_main_kb())

# =======================
#   Сроки (cut-off)
# =======================

@router.message(F.text == "⏰ Сроки")
async def deadlines_section(message: types.Message, state: FSMContext):
    if not await is_admin(message.from_user.id): return
    await state.set_state(DeadlinesEdit.waiting_for_deadline)
    await message.answer(
        f"📅 Текущий cut-off: {settings.workday_end_hour}:00\nВведите новое время (0-23):"
    )

@router.message(DeadlinesEdit.waiting_for_deadline, F.text.regexp(r"^\d{1,2}$"))
async def deadlines_update_numeric(message: types.Message, state: FSMContext):
    hour = int(message.text)
    if not 0 <= hour <= 23:
        await message.answer("Часы должны быть 0-23."); return
    settings.workday_end_hour = hour
    await state.clear()
    await message.answer(f"✅ Cut-off обновлён: {hour}:00", reply_markup=settings_kb())

# =======================
#   Заказы
# =======================

@router.message(F.text == "📦 Заказы")
async def show_orders(message: types.Message, state: FSMContext):
    if not await is_admin(message.from_user.id):
        await message.answer("⛔ У вас нет доступа."); return
    await state.clear()
    async with async_session() as session:
        res = await session.execute(select(Order).order_by(Order.created_at.desc()).limit(5))
        orders = res.scalars().all()
    if not orders:
        await message.answer("📦 Заказов пока нет."); return
    text = "📋 Последние заказы:\n\n"
    for o in orders:
        text += f"#{o.id} — {o.description}\nСтатус: {o.status}\n\n"
    await message.answer(text)

# =======================
#   Цены / Услуги (root)
# =======================

@router.message(F.text == "💰 Цены / Услуги")
async def services_root(message: types.Message, state: FSMContext):
    if not await is_admin(message.from_user.id):
        await message.answer("⛔ У вас нет доступа."); return
    await state.clear()
    async with async_session() as session:
        res = await session.execute(select(Service).order_by(Service.id))
        items = res.scalars().all()
    if not items:
        await message.answer("Пока нет ни одной услуги."); return
    await message.answer("Выберите услугу:", reply_markup=services_list_kb(items))

# =======================
#   Инструменты ИИ (inline)
# =======================

def ai_tools_kb() -> types.InlineKeyboardMarkup:
    status = "🟢 Включен" if settings.ai_enabled else "🔴 Выключен"
    toggle_text = "Выключить" if settings.ai_enabled else "Включить"
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text=status, callback_data="ai:noop")],
            [types.InlineKeyboardButton(text=f"🔁 {toggle_text}", callback_data="ai:toggle")],
            [types.InlineKeyboardButton(text="🔙 Назад", callback_data="ai:back")]
        ]
    )

@router.message(F.text == "🤖 Инструменты ИИ")
async def ai_section(message: types.Message, state: FSMContext):
    if not await is_admin(message.from_user.id): return
    await state.clear()
    await message.answer(
        f"🤖 Раздел «Инструменты ИИ»\n\nТекущее состояние: {'включен ✅' if settings.ai_enabled else 'выключен ❌'}",
        reply_markup=ai_tools_kb()
    )

@router.callback_query(F.data == "ai:toggle")
async def ai_toggle(callback: types.CallbackQuery):
    if not await is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True); return
    settings.ai_enabled = not settings.ai_enabled
    await callback.message.edit_text(
        f"🤖 Раздел «Инструменты ИИ»\n\nТекущее состояние: {'включен ✅' if settings.ai_enabled else 'выключен ❌'}",
        reply_markup=ai_tools_kb()
    )
    await callback.answer("Изменено")

@router.callback_query(F.data == "ai:back")
async def ai_back(callback: types.CallbackQuery):
    if not await is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True); return
    await callback.message.answer("Раздел настроек:", reply_markup=settings_kb())
    await callback.answer()

@router.callback_query(F.data == "ai:noop")
async def ai_noop(callback: types.CallbackQuery):
    await callback.answer()

# =======================
#   Другие разделы
# =======================

@router.message(F.text == "📦 Доставка")
async def delivery_section(message: types.Message, state: FSMContext):
    if not await is_admin(message.from_user.id): return
    await state.clear()
    await message.answer("🚚 Раздел «Доставка». Пока без настроек.", reply_markup=settings_kb())

@router.message(F.text == "👨‍💻 Админы")
async def admins_section(message: types.Message, state: FSMContext):
    if not await is_admin(message.from_user.id): return
    await state.clear()
    async with async_session() as session:
        res = await session.execute(select(Admin))
        admins = res.scalars().all()
    text = "👨‍💻 Список админов:\n" + "\n".join(str(a.user_id) for a in admins)
    await message.answer(text if admins else "Пока нет админов.", reply_markup=settings_kb())

@router.message(F.text == "📢 Уведомления")
async def notifications_section(message: types.Message, state: FSMContext):
    if not await is_admin(message.from_user.id): return
    await state.clear()
    settings.notify_enabled = not settings.notify_enabled
    await message.answer(
        f"🔔 Уведомления: {'включены ✅' if settings.notify_enabled else 'выключены ❌'}",
        reply_markup=settings_kb()
    )

@router.message(F.text == "📊 Статистика")
async def stats_section(message: types.Message, state: FSMContext):
    if not await is_admin(message.from_user.id): return
    await state.clear()
    async with async_session() as session:
        total_orders = (await session.execute(select(Order))).scalars().all()
        total_services = (await session.execute(select(Service))).scalars().all()
    await message.answer(
        f"📊 Статистика:\nЗаказов: {len(total_orders)}\nУслуг: {len(total_services)}",
        reply_markup=settings_kb()
    )

@router.message(F.text == "📂 Архив заказов")
async def archive_section(message: types.Message, state: FSMContext):
    if not await is_admin(message.from_user.id): return
    await state.clear()
    async with async_session() as session:
        res = await session.execute(select(Order).where(Order.status == "done").limit(5))
        items = res.scalars().all()
    if not items:
        await message.answer("📂 Архив пуст.", reply_markup=settings_kb()); return
    text = "📦 Последние завершённые заказы:\n\n"
    for o in items:
        text += f"#{o.id} — {o.description}\n\n"
    await message.answer(text, reply_markup=settings_kb())

@router.message(F.text == "⚡ Системные параметры")
async def system_section(message: types.Message, state: FSMContext):
    if not await is_admin(message.from_user.id): return
    await state.clear()
    await message.answer(
        f"⚙ Системные параметры:\n"
        f"Таймзона: {settings.timezone}\n"
        f"Cut-off: {settings.workday_end_hour}:00\n"
        f"AI: {'on' if settings.ai_enabled else 'off'}\n"
        f"Уведомления: {'on' if settings.notify_enabled else 'off'}",
        reply_markup=settings_kb()
    )

@router.message(F.text == "🔑 API")
async def api_section(message: types.Message, state: FSMContext):
    if not await is_admin(message.from_user.id): return
    await state.clear()
    await message.answer("🔑 Раздел «API». Тут будут ключи/интеграции.", reply_markup=settings_kb())
