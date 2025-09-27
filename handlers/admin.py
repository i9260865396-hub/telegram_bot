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
    waiting_for_min_qty = State()

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

# =======================
#   Услуги: callbacks + FSM handlers (добавлено)
# =======================

from sqlalchemy import select
from aiogram.exceptions import TelegramBadRequest

# Список услуг (обновить список по inline-кнопке)
@router.callback_query(F.data == "svc:list")
async def svc_list(callback: types.CallbackQuery, state: FSMContext):
    if not await is_admin(callback.from_user.id):
        return await callback.answer("Нет доступа", show_alert=True)
    await state.clear()
    async with async_session() as session:
        res = await session.execute(select(Service).order_by(Service.id))
        items = res.scalars().all()
    if not items:
        try:
            await callback.message.edit_text("Пока нет ни одной услуги.")
        except TelegramBadRequest:
            await callback.message.answer("Пока нет ни одной услуги.")
        return await callback.answer()
    try:
        await callback.message.edit_text("Выберите услугу:", reply_markup=services_list_kb(items))
    except TelegramBadRequest:
        await callback.message.answer("Выберите услугу:", reply_markup=services_list_kb(items))
    await callback.answer()

# Назад в настройки
@router.callback_query(F.data == "svc:back")
async def svc_back(callback: types.CallbackQuery, state: FSMContext):
    if not await is_admin(callback.from_user.id):
        return await callback.answer("Нет доступа", show_alert=True)
    await state.clear()
    await callback.message.edit_text("Раздел настроек:")
    await callback.message.answer("Раздел настроек:", reply_markup=settings_kb())
    await callback.answer()

# Открыть карточку услуги
@router.callback_query(F.data.startswith("svc:open:"))
async def svc_open(callback: types.CallbackQuery, state: FSMContext):
    if not await is_admin(callback.from_user.id):
        return await callback.answer("Нет доступа", show_alert=True)
    await state.clear()
    svc_id = int(callback.data.split(":")[2])
    async with async_session() as session:
        svc = await session.get(Service, svc_id)
        if not svc:
            await callback.answer("Услуга не найдена", show_alert=True); return
        text = service_card_text(svc)
    await callback.message.edit_text(text, reply_markup=service_card_kb(svc_id, svc.is_active), parse_mode="HTML")
    await callback.answer()

# Запросить изменение цены
@router.callback_query(F.data.startswith("svc:ask_price:"))
async def svc_ask_price(callback: types.CallbackQuery, state: FSMContext):
    if not await is_admin(callback.from_user.id):
        return await callback.answer("Нет доступа", show_alert=True)
    svc_id = int(callback.data.split(":")[2])
    await state.set_state(PriceEdit.waiting_for_price)
    await state.update_data(svc_id=svc_id)
    await callback.message.answer("Введите новую цену (число, можно с точкой):")
    await callback.answer()

# Принять новую цену
@router.message(PriceEdit.waiting_for_price)
async def svc_set_price(message: types.Message, state: FSMContext):
    if not await is_admin(message.from_user.id):
        return
    raw = (message.text or "").replace(",", ".").strip()
    try:
        price = float(raw)
        if price < 0:
            raise ValueError
    except ValueError:
        return await message.answer("⛔ Введите корректную цену (например: 12.5)")
    data = await state.get_data()
    svc_id = data.get("svc_id")
    async with async_session() as session:
        svc = await session.get(Service, svc_id)
        if not svc:
            await state.clear()
            return await message.answer("Услуга не найдена.")
        svc.price = price
        await session.commit()
        text = service_card_text(svc)
    await state.clear()
    await message.answer(f"✅ Цена обновлена: {price}")
    await message.answer(text, reply_markup=service_card_kb(svc_id, svc.is_active), parse_mode="HTML")

# Запросить изменение минимального тиража
@router.callback_query(F.data.startswith("svc:ask_min:"))
async def svc_ask_min(callback: types.CallbackQuery, state: FSMContext):
    if not await is_admin(callback.from_user.id):
        return await callback.answer("Нет доступа", show_alert=True)
    svc_id = int(callback.data.split(":")[2])
    await state.set_state(MinQtyEdit.waiting_for_min)
    await state.update_data(svc_id=svc_id)
    await callback.message.answer("Введите новый минимум (целое число >= 1):")
    await callback.answer()

# Принять минимальный тираж
@router.message(MinQtyEdit.waiting_for_min)
async def svc_set_min(message: types.Message, state: FSMContext):
    if not await is_admin(message.from_user.id):
        return
    try:
        min_qty = int(message.text.strip())
        if min_qty < 1:
            raise ValueError
    except ValueError:
        return await message.answer("⛔ Введите целое число >= 1")
    data = await state.get_data()
    svc_id = data.get("svc_id")
    async with async_session() as session:
        svc = await session.get(Service, svc_id)
        if not svc:
            await state.clear()
            return await message.answer("Услуга не найдена.")
        svc.min_qty = min_qty
        await session.commit()
        text = service_card_text(svc)
    await state.clear()
    await message.answer(f"✅ Минимальный тираж обновлён: {min_qty}")
    await message.answer(text, reply_markup=service_card_kb(svc_id, svc.is_active), parse_mode="HTML")

# Запросить выбор единицы измерения
@router.callback_query(F.data.startswith("svc:ask_unit:"))
async def svc_ask_unit(callback: types.CallbackQuery, state: FSMContext):
    if not await is_admin(callback.from_user.id):
        return await callback.answer("Нет доступа", show_alert=True)
    svc_id = int(callback.data.split(":")[2])
    await state.update_data(svc_id=svc_id)
    await callback.message.edit_text("Выберите единицу измерения:", reply_markup=units_kb(svc_id))
    await callback.answer()

# Установить единицу
@router.callback_query(F.data.startswith("svc:set_unit:"))
async def svc_set_unit(callback: types.CallbackQuery, state: FSMContext):
    if not await is_admin(callback.from_user.id):
        return await callback.answer("Нет доступа", show_alert=True)
    _, _, svc_id_str, code = callback.data.split(":")
    svc_id = int(svc_id_str)
    label = UNIT_OPTIONS.get(code)
    if not label:
        return await callback.answer("Неизвестная единица", show_alert=True)
    async with async_session() as session:
        svc = await session.get(Service, svc_id)
        if not svc:
            return await callback.answer("Услуга не найдена", show_alert=True)
        svc.unit = label
        await session.commit()
        text = service_card_text(svc)
    await callback.message.edit_text(text, reply_markup=service_card_kb(svc_id, svc.is_active), parse_mode="HTML")
    await callback.answer("Обновлено")

# Переключить активность
@router.callback_query(F.data.startswith("svc:toggle:"))
async def svc_toggle(callback: types.CallbackQuery, state: FSMContext):
    if not await is_admin(callback.from_user.id):
        return await callback.answer("Нет доступа", show_alert=True)
    svc_id = int(callback.data.split(":")[2])
    async with async_session() as session:
        svc = await session.get(Service, svc_id)
        if not svc:
            return await callback.answer("Услуга не найдена", show_alert=True)
        svc.is_active = not svc.is_active
        await session.commit()
        text = service_card_text(svc)
    await callback.message.edit_text(text, reply_markup=service_card_kb(svc_id, svc.is_active), parse_mode="HTML")
    await callback.answer("Изменено")

# Удалить услугу
@router.callback_query(F.data.startswith("svc:delete:"))
async def svc_delete(callback: types.CallbackQuery, state: FSMContext):
    if not await is_admin(callback.from_user.id):
        return await callback.answer("Нет доступа", show_alert=True)
    svc_id = int(callback.data.split(":")[2])
    async with async_session() as session:
        svc = await session.get(Service, svc_id)
        if not svc:
            return await callback.answer("Услуга не найдена", show_alert=True)
        await session.delete(svc)
        await session.commit()
        res = await session.execute(select(Service).order_by(Service.id))
        items = res.scalars().all()
    if not items:
        await callback.message.edit_text("Услуга удалена. Больше услуг нет.")
        return await callback.answer("Удалено")
    await callback.message.edit_text("Услуга удалена. Список услуг:", reply_markup=services_list_kb(items))
    await callback.answer("Удалено")

# Добавить услугу
@router.callback_query(F.data == "svc:add")
async def add_service_start(callback: types.CallbackQuery, state: FSMContext):
    if not await is_admin(callback.from_user.id):
        return await callback.answer("Нет доступа", show_alert=True)
    await state.set_state(AddService.waiting_for_name)
    await state.update_data(new_service={})
    await callback.message.answer("Введите название новой услуги:")
    await callback.answer()

@router.message(AddService.waiting_for_name)
async def add_service_name(message: types.Message, state: FSMContext):
    if not await is_admin(message.from_user.id):
        return
    name = message.text.strip()
    if len(name) < 2:
        return await message.answer("Название слишком короткое. Введите снова:")
    data = await state.get_data()
    new = data.get("new_service", {{}})
    new["name"] = name
    await state.update_data(new_service={"name": message.text.strip()})
    await state.set_state(AddService.waiting_for_price)
    await message.answer("Введите цену (например: 12.5):")
    
@router.message(AddService.waiting_for_price)
async def add_service_price(message: types.Message, state: FSMContext):
    try:
        price = float(message.text.strip().replace(",", "."))
    except ValueError:
        return await message.answer("⛔ Введите корректное число (например: 12.5).")

    data = await state.get_data()
    new = data.get("new_service", {})
    new["price"] = price
    await state.update_data(new_service=new)
    await state.set_state(AddService.waiting_for_unit)
    await message.answer("Введите единицу измерения (шт., м, м²):")
    
@router.message(AddService.waiting_for_unit)
async def add_service_unit(message: types.Message, state: FSMContext):
    unit = message.text.strip().lower()
    allowed = {"шт.", "шт", "м", "м²", "м2"}
    if unit not in allowed:
        return await message.answer("⛔ Допустимые варианты: шт., м, м²")

    unit_norm = "шт." if unit.startswith("шт") else ("м²" if unit in {"м²", "м2"} else "м")

    data = await state.get_data()
    new = data.get("new_service", {})
    new["unit"] = unit_norm
    await state.update_data(new_service=new)
    await state.set_state(AddService.waiting_for_min_qty)
    await message.answer("Введите минимальное количество (целое число):")

@router.message(AddService.waiting_for_min_qty)
async def add_service_min_qty(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        return await message.answer("⛔ Введите целое число.")

    min_qty = int(message.text)
    data = await state.get_data()
    new = data.get("new_service", {})

    # Сохраняем в БД
    from database.models import Service
    from database import async_session
    async with async_session() as session:
        service = Service(
            name=new["name"],
            price=new["price"],
            unit=new["unit"],
            min_qty=min_qty,
        )
        session.add(service)
        await session.commit()

    await state.clear()
    await message.answer(f"✅ Услуга <b>{new['name']}</b> добавлена.")
    await message.answer("Список услуг:", reply_markup=services_list_kb(items))

