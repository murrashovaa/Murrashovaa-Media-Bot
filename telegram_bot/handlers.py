import asyncio
import os

from aiogram import F, Router
from aiogram.exceptions import TelegramEntityTooLarge
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, FSInputFile, Message

from downloader.video import (
    VideoTooLargeError,
    download_video,
    get_video_dimensions,
)
from image.remove_background import remove_background
from config.settings import STORAGE_PATH
from services.downloader_service import UnsupportedSourceError, download_audio
from tags.cover import add_cover, extract_cover
from tags.editor import update_metadata
from tags.formatter import format_metadata
from tags.parser import read_metadata
from telegram_bot.keyboards import main_keyboard, tags_keyboard
from telegram_bot.states import (
    DownloadMusicState,
    DownloadVideoState,
    ImageState,
    TagsState,
)

router = Router()

TEMP_DIR = STORAGE_PATH

TAG_FIELD_NAMES = {
    "title": "название",
    "artist": "исполнитель",
    "album": "альбом",
    "year": "год",
    "genre": "жанр",
}


# Команды

@router.message(Command("start"))
async def start_handler(message: Message):
    await message.answer(
        "🎵 Привет! Это Murrashovaa Media Bot\n\n"
        "Выберите действие:",
        reply_markup=main_keyboard,
    )


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


# Главное меню

@router.message(F.text == "🎵 Скачать музыку")
async def start_music_download_handler(
    message: Message,
    state: FSMContext,
):
    await state.set_state(DownloadMusicState.waiting_for_url)
    await message.answer(
        "🎵 Отправьте ссылку на музыку\n\n"
        "Поддерживаются:\n"
        "• YouTube\n"
        "• SoundCloud\n"
        "• TikTok\n"
        "• Instagram"
    )


@router.message(F.text == "🎬 Скачать видео")
async def start_video_download_handler(
    message: Message,
    state: FSMContext,
):
    await state.set_state(DownloadVideoState.waiting_for_url)
    await message.answer(
        "🎬 Отправьте ссылку на видео\n\n"
        "Поддерживаются:\n"
        "• YouTube\n"
        "• TikTok\n"
        "• Instagram"
    )


@router.message(F.text == "🏷 Редактировать теги")
async def start_tags_handler(
    message: Message,
    state: FSMContext,
):
    await state.set_state(TagsState.waiting_for_audio)
    await message.answer("🏷 Отправьте MP3-файл для анализа")


@router.message(F.text == "✂️ Удалить фон")
async def start_background_remove_handler(
    message: Message,
    state: FSMContext,
):
    await state.set_state(ImageState.waiting_for_image)
    await message.answer(
        "✂️ Отправьте изображение,\n"
        "поддерживаются JPG, PNG, WEBP, HEIC"
    )


# Музыка

@router.message(DownloadMusicState.waiting_for_url)
async def download_music_url_handler(
    message: Message,
    state: FSMContext,
):
    file_path: str | None = None

    if not message.text:
        await message.answer(
            "Отправь ссылку на YouTube, SoundCloud, TikTok или Instagram."
        )
        return

    status_message = await message.answer("⏳ Обрабатываю ссылку...")

    try:
        file_path, source = await asyncio.to_thread(
            download_audio,
            message.text,
        )
        await status_message.edit_text(
            f"📤 Аудио скачано с {source}. Отправляю файл..."
        )
        await message.answer_audio(audio=FSInputFile(file_path))
        await status_message.edit_text(
            f"✅ Файл с {source} успешно отправлен 🎵"
        )
    except UnsupportedSourceError as error:
        await status_message.edit_text(f"❌ {error}")
    except ValueError as error:
        await status_message.edit_text(f"❌ Некорректная ссылка:\n{error}")
    except Exception as error:
        await status_message.edit_text(f"❌ Не удалось скачать аудио:\n{error}")
    finally:
        remove_file(file_path)
        await state.clear()


# Видео

@router.message(
    DownloadVideoState.waiting_for_url,
    F.text,
)
async def download_video_url_handler(
    message: Message,
    state: FSMContext,
):
    file_path: str | None = None
    url = message.text.strip()
    status_message = await message.answer(
        "⏳ Скачиваю видео. Если файл будет большим, сожму до 720p..."
    )

    try:
        file_path = await asyncio.to_thread(download_video, url)
        await status_message.edit_text(
            "📤 Видео скачано. Отправляю файл..."
        )
        await send_video_file(message, file_path)
        await status_message.edit_text("✅ Видео успешно отправлено 🎬")
    except VideoTooLargeError as error:
        await status_message.edit_text(
            "❌ Видео слишком большое для отправки через Telegram.\n"
            f"{error}"
        )
    except TelegramEntityTooLarge:
        await status_message.edit_text(
            "❌ Telegram не принял видео даже после подготовки."
        )
    except Exception as error:
        await status_message.edit_text(f"❌ Ошибка:\n{error}")
    finally:
        remove_file(file_path)
        await state.clear()


# Теги


async def send_video_file(
    message: Message,
    file_path: str,
) -> None:
    video_file = FSInputFile(file_path)
    width, height = get_video_dimensions(file_path)
    await message.answer_video(
        video_file,
        width=width,
        height=height,
        supports_streaming=True,
    )

@router.message(
    TagsState.waiting_for_audio,
    F.audio,
)
async def process_audio_handler(
    message: Message,
    state: FSMContext,
):
    ensure_temp_dir()
    file_path: str | None = None

    try:
        await message.answer("⏳ Анализирую файл...")
        file_name = message.audio.file_name or "track.mp3"
        file_path = os.path.join(TEMP_DIR, file_name)

        file = await message.bot.get_file(message.audio.file_id)
        await message.bot.download_file(file.file_path, file_path)

        await state.update_data(file_path=file_path)
        text = format_metadata(read_metadata(file_path))
        await send_track_info(message, file_path, text)
        await state.set_state(TagsState.editing_tags)
    except Exception as error:
        remove_file(file_path)
        await state.clear()
        await message.answer(f"❌ Ошибка:\n{error}")


@router.callback_query(
    F.data.startswith("edit_"),
    F.data != "edit_cover",
)
async def choose_tag_handler(
    callback: CallbackQuery,
    state: FSMContext,
):
    field = callback.data.replace("edit_", "")

    if field not in TAG_FIELD_NAMES:
        await callback.answer()
        return

    await state.update_data(editing_field=field)
    await state.set_state(TagsState.editing_field)
    await callback.message.answer(
        f"✏️ Введите новое значение для поля «{TAG_FIELD_NAMES[field]}»"
    )
    await callback.answer()


@router.message(TagsState.editing_field)
async def save_new_tag_value_handler(
    message: Message,
    state: FSMContext,
):
    data = await state.get_data()
    file_path = data["file_path"]
    field = data["editing_field"]

    update_metadata(file_path, field, message.text)

    text = format_metadata(read_metadata(file_path))
    await message.answer(
        "✅ Тег успешно обновлен!\n\n" + text,
        parse_mode="HTML",
        reply_markup=tags_keyboard,
    )
    await state.set_state(TagsState.editing_tags)


@router.callback_query(F.data == "edit_cover")
async def choose_cover_handler(
    callback: CallbackQuery,
    state: FSMContext,
):
    await state.set_state(TagsState.waiting_for_cover)
    await callback.message.answer(
        "🖼 Отправьте изображение для обложки\n\n"
        "Поддерживается JPG/PNG"
    )
    await callback.answer()


@router.message(
    TagsState.waiting_for_cover,
    F.photo | F.document,
)
async def process_cover_handler(
    message: Message,
    state: FSMContext,
):
    ensure_temp_dir()
    data = await state.get_data()
    audio_path = data["file_path"]
    image_path = os.path.join(TEMP_DIR, "cover.jpg")

    file_id = get_image_file_id(message)
    if file_id is None:
        await message.answer("❌ Не удалось получить изображение")
        return

    file = await message.bot.get_file(file_id)
    await message.bot.download_file(file.file_path, image_path)

    add_cover(audio_path, image_path)
    remove_file(image_path)

    text = "✅ Обложка добавлена!\n\n" + format_metadata(
        read_metadata(audio_path)
    )
    await send_track_info(message, audio_path, text)
    await state.set_state(TagsState.editing_tags)


@router.callback_query(F.data == "finish_tags")
async def finish_tags_handler(
    callback: CallbackQuery,
    state: FSMContext,
):
    data = await state.get_data()
    file_path = data["file_path"]
    metadata = read_metadata(file_path)

    await callback.message.answer(
        "🎉 Готово! Отправляю обновленный трек..."
    )
    await callback.message.answer_audio(
        audio=FSInputFile(file_path),
        title=metadata.get("title"),
        performer=metadata.get("artist"),
    )
    remove_file(file_path)
    await state.clear()
    await callback.answer()


# Изображения

@router.message(
    ImageState.waiting_for_image,
    F.photo | F.document,
)
async def process_background_remove_handler(
    message: Message,
    state: FSMContext,
):
    ensure_temp_dir()
    input_path = os.path.join(TEMP_DIR, "input_image")
    output_path = os.path.join(TEMP_DIR, "no_background.png")

    file_id = get_image_file_id(message)
    if file_id is None:
        await message.answer("❌ Не удалось получить изображение")
        return

    try:
        file = await message.bot.get_file(file_id)
        await message.bot.download_file(file.file_path, input_path)

        await message.answer("⏳ Удаляю фон...")
        remove_background(input_path, output_path)
        await message.answer_document(
            document=FSInputFile(output_path),
            caption="✅ Готово! Фон удален",
        )
    except Exception as error:
        await message.answer(f"❌ Ошибка:\n{error}")
    finally:
        remove_file(input_path)
        remove_file(output_path)
        await state.clear()


# Вспомогательные функции

async def send_track_info(
    message: Message,
    file_path: str,
    text: str,
):
    cover = extract_cover(file_path)

    if cover:
        await message.answer_photo(
            photo=BufferedInputFile(cover, filename="cover.jpg"),
            caption=text,
            parse_mode="HTML",
            reply_markup=tags_keyboard,
        )
        return

    await message.answer(
        text,
        parse_mode="HTML",
        reply_markup=tags_keyboard,
    )


def ensure_temp_dir() -> None:
    os.makedirs(TEMP_DIR, exist_ok=True)


def get_image_file_id(message: Message) -> str | None:
    if message.photo:
        return message.photo[-1].file_id

    if message.document:
        return message.document.file_id

    return None


def remove_file(file_path: str | None) -> None:
    if file_path and os.path.exists(file_path):
        os.remove(file_path)
