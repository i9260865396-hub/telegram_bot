from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def main_menu() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="🆕 Новый заказ")
    kb.button(text="📦 Статус заказа")
    kb.button(text="🛠 Админка")
    kb.adjust(2,1)
    return kb.as_markup(resize_keyboard=True)
