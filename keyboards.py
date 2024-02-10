from aiogram.types import Message, Sticker, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def markup_daily():
    items = [
        "Дейли ПАИП",
        "Дейли НСИ"
    ]

    keyboard_builder = ReplyKeyboardBuilder()
    [keyboard_builder.button(text=item) for item in items]
    return keyboard_builder.as_markup(resize_keyboard=True, one_time_keyboard=True)