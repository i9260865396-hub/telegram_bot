from aiogram import Router, F
from aiogram.types import Message
from keyboards.main import main_menu

router = Router(name="welcome")

@router.message(F.text == "/start")
async def start_cmd(message: Message):
    await message.answer(
        "Привет! Я бот типографии. Выберите действие ниже 👇",
        reply_markup=main_menu()
    )
