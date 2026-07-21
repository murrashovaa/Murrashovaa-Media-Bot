from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)


main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🎵 Скачать музыку"),
            KeyboardButton(text="🎬 Скачать видео"),
        ],
        [
            KeyboardButton(text="🏷 Редактировать теги"),
            KeyboardButton(text="✂️ Удалить фон"),
        ],
    ],
    resize_keyboard=True,
)

tags_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🎵 Название",
                callback_data="edit_title",
            ),
            InlineKeyboardButton(
                text="👤 Исполнитель",
                callback_data="edit_artist",
            ),
        ],
        [
            InlineKeyboardButton(
                text="💿 Альбом",
                callback_data="edit_album",
            ),
            InlineKeyboardButton(
                text="📅 Год",
                callback_data="edit_year",
            ),
        ],
        [
            InlineKeyboardButton(
                text="🎸 Жанр",
                callback_data="edit_genre",
            ),
            InlineKeyboardButton(
                text="🖼 Обложка",
                callback_data="edit_cover",
            ),
        ],
        [
            InlineKeyboardButton(
                text="✅ Готово",
                callback_data="finish_tags",
            )
        ],
    ],
)
