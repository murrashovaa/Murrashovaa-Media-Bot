import asyncio
import os
from aiogram import Router, F
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from telegram_bot.keyboards import main_keyboard
from telegram_bot.states import (
    DownloadMusicState,
    DownloadVideoState
)

from services.downloader_service import (
    UnsupportedSourceError,
    download_audio,
)

router = Router()


# Команда /start

@router.message(Command("start"))
async def start_handler(message: Message):

    await message.answer(
        "🎵 Привет! Это Murrashovaa Media Bot\n\n"
        "Выберите действие:",
        reply_markup=main_keyboard
    )


# Команда /help

@router.message(Command("help"))
async def help_handler(message: Message):

    await message.answer(
        """
🎵 Murrashovaa Media Bot

Доступные функции:

🎵 Скачать музыку
🎬 Скачать видео
🏷 Редактировать теги
✂️ Удалить фон
"""
    )


# Кнопка скачать музыку

@router.message(F.text == "🎵 Скачать музыку")
async def download_music_handler(
    message: Message,
    state: FSMContext
):

    await state.set_state(
        DownloadMusicState.waiting_for_url
    )

    await message.answer(
       "🎵 Отправьте ссылку на музыку\n\n"
        "Поддерживаются:\n"
        "• YouTube\n"
        "• SoundCloud"
    )


# Кнопка скачать видео

@router.message(F.text == "🎬 Скачать видео")
async def download_video_handler(
    message: Message,
    state: FSMContext
):

    await state.set_state(
        DownloadVideoState.waiting_for_url
    )

    await message.answer(
        "🎬 Отправьте ссылку на видео\n\n"
        "Поддерживаются:\n"
        "• YouTube\n"
        "• TikTok\n"
        "• Instagram"
    )


# Работа с тегами

@router.message(F.text == "🏷 Редактировать теги")
async def tags_handler(message: Message):

    await message.answer(
        "🏷 Редактор тегов\n\n"
        "Отправьте MP3-файл,\n"
        "чтобы изменить:\n\n"
        "• название\n"
        "• автора\n"
        "• альбом\n"
        "• жанр\n"
        "• обложку"
    )


# Удаление фона

@router.message(F.text == "✂️ Удалить фон")
async def remove_background_handler(message: Message):

    await message.answer(
        "✂️ Отправьте изображение,\n"
        "и я удалю фон."
    )


# Обработка ссылки на музыку

@router.message(DownloadMusicState.waiting_for_url)
async def get_music_url(
    message: Message,
    state: FSMContext,
):
    file_path: str | None = None

    if not message.text:
        await message.answer(
            "Отправь ссылку на YouTube или SoundCloud."
        )
        return

    status_message = await message.answer(
        "⏳ Обрабатываю ссылку..."
    )

    try:
        file_path, source = await asyncio.to_thread(
            download_audio,
            message.text,
        )

        await status_message.edit_text(
            f"📤 Аудио скачано с {source}. Отправляю файл..."
        )

        audio_file = FSInputFile(file_path)

        await message.answer_audio(
            audio=audio_file,
        )

        await status_message.edit_text(
            f"✅ Файл с {source} успешно отправлен 🎵"
        )

    except UnsupportedSourceError as error:
        await status_message.edit_text(
            f"❌ {error}"
        )

    except ValueError as error:
        await status_message.edit_text(
            f"❌ Некорректная ссылка:\n{error}"
        )

    except Exception as error:
        await status_message.edit_text(
            f"❌ Не удалось скачать аудио:\n{error}"
        )

    finally:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)

        await state.clear()


# Обработка ссылки на видео

@router.message(
    DownloadVideoState.waiting_for_url
)
async def get_video_url(
    message: Message,
    state: FSMContext
):

    url = message.text

    await message.answer(
        f"🎬 Получена ссылка:\n{url}\n\n"
        "⏳ Скоро начну загрузку..."
    )

    await state.clear()