from aiogram import Router, types, F
from aiogram.filters import Command


router = Router()


async def _reply_with_status(message: types.Message) -> None:
    await message.answer("Проверка статуса заказа (заглушка)")


@router.message(Command("status"))
async def status_handler(message: types.Message):
    await _reply_with_status(message)


@router.message(F.text.in_({"Статус заказа", "📦 Статус заказа"}))
async def status_text_handler(message: types.Message):
    await _reply_with_status(message)
