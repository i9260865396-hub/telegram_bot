from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
import logging

from config.settings import settings

router = Router(name="admin")


def _get_admin_ids() -> set[int]:
    if hasattr(settings, "get_admin_ids") and callable(settings.get_admin_ids):
        admin_ids = settings.get_admin_ids()
    else:
        admin_ids = getattr(settings, "admin_ids", [])
    normalized_ids: set[int] = set()
    for admin_id in admin_ids:
        try:
            normalized_ids.add(int(admin_id))
        except (TypeError, ValueError):
            continue
    return normalized_ids


def is_admin_id(user_id: int) -> bool:
    return user_id in _get_admin_ids()


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
