import asyncio
import os

from aiogram import Router, F
from aiogram.types import (
    Message, 
    FSInputFile, 
    Document,
    CallbackQuery,
    BufferedInputFile
)
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from telegram_bot.keyboards import (
    main_keyboard, 
    tags_keyboard
)
from telegram_bot.states import (
    DownloadMusicState,
    DownloadVideoState,
    TagsState
)

from services.downloader_service import (
    UnsupportedSourceError,
    download_audio,
)

from tags.parser import read_metadata
from tags.formatter import format_metadata
from tags.editor import update_metadata
from tags.cover import (
    add_cover, 
    extract_cover
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
async def tags_start(
    message: Message,
    state: FSMContext
):
    await message.answer(
        "🏷 Отправьте MP3-файл для анализа"
    )
    await state.set_state(
        TagsState.waiting_for_audio
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


# Обработчик MP3

@router.message(
    TagsState.waiting_for_audio,
    F.audio
)
async def process_audio(
    message: Message,
    state: FSMContext
):
    file_path = None
    try:
        await message.answer(
            "⏳ Анализирую файл..."
        )
        file_name = (
            message.audio.file_name
            or "track.mp3"
        )
        file_path = (
            f"storage/temp/{file_name}"
        )
        file = await message.bot.get_file(
            message.audio.file_id
        )
        await message.bot.download_file(
            file.file_path,
            file_path
        )
        await state.update_data(
            file_path=file_path
        )
        metadata = read_metadata(
            file_path
        )
        text = format_metadata(
            metadata
        )
        await send_track_info(
            message,
            file_path,
            text
        )
        await state.set_state(
            TagsState.editing_tags
        )
    except Exception as e:
        await message.answer(
            f"❌ Ошибка:\n{e}"
        )


# Обработчик кнопок для тегов 

@router.callback_query(
    F.data.startswith("edit_"),
    F.data != "edit_cover"
)
async def choose_tag(
    callback: CallbackQuery,
    state: FSMContext
):
    field = callback.data.replace(
        "edit_",
        ""
    )
    if field == "cover":
        await callback.answer()
        return
    await state.update_data(
        editing_field=field
    )
    await state.set_state(
        TagsState.editing_field
    )
    names = {
        "title": "название",
        "artist": "исполнитель",
        "album": "альбом",
        "year": "год",
        "genre": "жанр"
    }
    await callback.message.answer(
        f"✏️ Введите новое значение для поля "
        f"«{names[field]}»"
    )
    await callback.answer()


# Обработчик новых тегов 

@router.message(
    TagsState.editing_field
)
async def save_new_value(
    message: Message,
    state: FSMContext
):
    data = await state.get_data()
    file_path = data["file_path"]
    field = data["editing_field"]
    update_metadata(
        file_path,
        field,
        message.text
    )
    metadata = read_metadata(
        file_path
    )
    text = format_metadata(
        metadata
    )
    await message.answer(
        "✅ Тег успешно обновлен!\n\n"
        + text,
        parse_mode="HTML",
        reply_markup=tags_keyboard
    )
    await state.set_state(
        TagsState.editing_tags
    )


# Обработчик кнопки Готово

@router.callback_query(
    F.data == "finish_tags"
)
async def finish_tags(
    callback: CallbackQuery,
    state: FSMContext
):
    data = await state.get_data()
    file_path = data["file_path"]
    metadata = read_metadata(
        file_path
    )
    await callback.message.answer(
        "🎉 Готово! Отправляю обновленный трек..."
    )
    await callback.message.answer_audio(
        audio=FSInputFile(file_path),
        title=metadata.get("title"),
        performer=metadata.get("artist")
    )
    os.remove(file_path)
    await state.clear()
    await callback.answer()


# Обработчик кнопки Обложка

@router.callback_query(
    F.data == "edit_cover"
)
async def choose_cover(
    callback: CallbackQuery,
    state: FSMContext
):
    await state.set_state(
        TagsState.waiting_for_cover
    )
    await callback.message.answer(
        "🖼 Отправьте изображение для обложки\n\n"
        "Поддерживается JPG/PNG"
    )
    await callback.answer()


# Обработчик обложки

@router.message(
    TagsState.waiting_for_cover,
    F.photo | F.document
)
async def process_cover(
    message: Message,
    state: FSMContext
):
    data = await state.get_data()
    audio_path = data["file_path"]
    image_path = (
        "storage/temp/cover.jpg"
    )
    if message.photo:
        file_id = message.photo[-1].file_id
    elif message.document:
        file_id = message.document.file_id
    else:
        await message.answer(
            "❌ Не удалось получить изображение"
        )
        return
    file = await message.bot.get_file(
        file_id
    )
    await message.bot.download_file(
        file.file_path,
        image_path
    )
    add_cover(
        audio_path,
        image_path
    )
    metadata = read_metadata(
        audio_path
    )
    text = format_metadata(
        metadata
    )
    cover = extract_cover(
        audio_path
    )
    if cover:
        photo_file = BufferedInputFile(
            cover,
            filename="cover.jpg"
        )
        await message.answer_photo(
            photo=photo_file,
            caption=(
                "✅ Обложка добавлена!\n\n"
                + text
            ),
            parse_mode="HTML",
            reply_markup=tags_keyboard
        )
    else:
        await message.answer(
            "✅ Обложка добавлена!\n\n"
            + text,
            parse_mode="HTML",
            reply_markup=tags_keyboard
        )
    await state.set_state(
        TagsState.editing_tags
    )

# Если есть обложка показываем ее 

async def send_track_info(
    message,
    file_path,
    text
):
    cover = extract_cover(
        file_path
    )
    if cover:
        photo_file = BufferedInputFile(
            cover,
            filename="cover.jpg"
        )
        await message.answer_photo(
            photo=photo_file,
            caption=text,
            parse_mode="HTML",
            reply_markup=tags_keyboard
        )
    else:
        await message.answer(
            text,
            parse_mode="HTML",
            reply_markup=tags_keyboard
        )