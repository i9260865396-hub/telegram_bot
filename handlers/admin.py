from aiogram import Router, types
from aiogram.filters import Command
from database.db import get_admins

router = Router()


@router.message(Command("admin"))
async def admin_entry(message: types.Message):
    if message.from_user.id not in get_admins():
        await message.answer("вќЊ РЈ РІР°СЃ РЅРµС‚ РїСЂР°РІ РґРѕСЃС‚СѓРїР°")
        return

    await message.answer(
        "РђРґРјРёРЅРєР°:\n"
        "/admin_orders вЂ” РїРѕСЃР»РµРґРЅРёРµ Р·Р°РєР°Р·С‹\n"
        "/grant_admin ID вЂ” РІС‹РґР°С‚СЊ РїСЂР°РІР°"
    )

