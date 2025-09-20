from aiogram import Router, types
from aiogram.filters import Command
from database.db import get_all_orders
from utils.seed_admin import add_admin

router = Router()


@router.message(Command("admin"))
async def admin_entry(message: types.Message):
    await message.answer(
        "Админка:\n"
        "/admin_orders — последние заказы\n"
        "/grant_admin ID — выдать права"
    )


@router.message(Command("admin_orders"))
async def admin_orders(message: types.Message):
    orders = get_all_orders()
    if not orders:
        await message.answer("Заказов пока нет.")
    else:
        text = "\n\n".join([f"#{o['id']} — {o['item']} ({o['status']})" for o in orders])
        await message.answer("Последние заказы:\n" + text)


@router.message(Command("grant_admin"))
async def grant_admin(message: types.Message):
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("Укажите ID пользователя: /grant_admin 123456789")
        return
    try:
        user_id = int(parts[1])
        add_admin(user_id)
        await message.answer(f"Пользователь {user_id} теперь админ ✅")
    except ValueError:
        await message.answer("Некорректный ID.")