from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🎵 Скачать музыку"),
            KeyboardButton(text="🎬 Скачать видео")
        ],
        [
            KeyboardButton(text="🏷 Редактировать теги"),
            KeyboardButton(text="✂️ Удалить фон")
        ],
    ],
    resize_keyboard=True
)