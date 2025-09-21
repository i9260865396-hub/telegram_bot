from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
import os
import logging

router = Router(name="admin")

def _parse_admin_ids():
    """ADMIN_IDS в .env: 12345,67890 или 12345;67890"""
    raw = os.getenv("ADMIN_IDS", "") or ""
    raw = raw.replace(";", ",")
    ids = [s.strip() for s in raw.split(",") if s.strip()]
    return set(ids)

def is_admin_id(user_id: int) -> bool:
    return str(user_id) in _parse_admin_ids()

def admin_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📦 Заказы",   callback_data="admin:orders")],
        [InlineKeyboardButton(text="⚙️ Настройки", callback_data="admin:settings")],
        [InlineKeyboardButton(text="💲 Цены",     callback_data="admin:prices")],
    ])

@router.message(Command("admin"))
async def admin_cmd(message: Message):
    if not is_admin_id(message.from_user.id):
        await message.answer("⛔ Нет прав доступа.")
        return
    await message.answer("Админ-панель:", reply_markup=admin_kb())

@router.message(F.text.func(lambda t: (t or "").lower().strip() in {"админ панель","админ-панель","admin"}))
async def admin_text(message: Message):
    await admin_cmd(message)

@router.callback_query(F.data.startswith("admin:"))
async def admin_cb(call: CallbackQuery):
    if not is_admin_id(call.from_user.id):
        await call.answer("Нет прав", show_alert=True)
        return
    data = call.data
    logging.info("ADMIN_CB %s from %s", data, call.from_user.id)
    if data == "admin:orders":
        await call.message.edit_text("Здесь будут последние заказы.\n\n(заглушка)")
    elif data == "admin:settings":
        await call.message.edit_text("Здесь будут настройки.\n\n(заглушка)")
    elif data == "admin:prices":
        await call.message.edit_text("Здесь будет редактор цен.\n\n(заглушка)")
    else:
        await call.answer()
