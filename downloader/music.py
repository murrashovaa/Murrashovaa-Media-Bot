import os
import re
import shutil

import yt_dlp

from config.settings import STORAGE_PATH
from downloader.errors import raise_friendly_ytdlp_error
from downloader.options import add_ytdlp_auth_options


def download_music(url: str) -> str:
    os.makedirs(STORAGE_PATH, exist_ok=True)

    options = {
        "format": "bestaudio/best",
        "outtmpl": f"{STORAGE_PATH}/%(title)s.%(ext)s",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "320",
            }
        ],
        "noplaylist": True,
    }
    add_ytdlp_auth_options(options)

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
    except Exception as error:
        raise_friendly_ytdlp_error(error)

    file_path = f"{os.path.splitext(filename)[0]}.mp3"

    if os.path.exists(file_path):
        return rename_audio_file(file_path, info)

    raise FileNotFoundError("Не удалось найти скачанный аудиофайл.")


def download_youtube_audio(url: str) -> str:
    return download_music(url)


def download_soundcloud_audio(url: str) -> str:
    return download_music(url)


def rename_audio_file(file_path: str, info: dict) -> str:
    artist = get_artist(info)
    title = get_title(info)
    filename = build_audio_filename(artist, title)
    target_path = os.path.join(STORAGE_PATH, filename)

    if os.path.abspath(file_path) == os.path.abspath(target_path):
        return file_path

    target_path = get_unique_path(target_path)
    shutil.move(file_path, target_path)
    return target_path


def build_audio_filename(
    artist: str | None,
    title: str,
) -> str:
    clean_title = sanitize_filename(title)
    clean_artist = sanitize_filename(artist) if artist else None

    if clean_artist and not title_starts_with_artist(clean_title, clean_artist):
        return f"{clean_artist} - {clean_title}.mp3"

    return f"{clean_title}.mp3"


def get_artist(info: dict) -> str | None:
    return first_present_value(
        info,
        (
            "artist",
            "creator",
            "uploader",
            "channel",
        ),
    )


def get_title(info: dict) -> str:
    return (
        first_present_value(info, ("track", "title", "fulltitle"))
        or "audio"
    )


def first_present_value(
    data: dict,
    keys: tuple[str, ...],
) -> str | None:
    for key in keys:
        value = data.get(key)
        if value:
            return str(value).strip()

    return None


def title_starts_with_artist(
    title: str,
    artist: str,
) -> bool:
    return title.lower().startswith(f"{artist.lower()} - ")


def sanitize_filename(value: str) -> str:
    value = re.sub(r'[\\/:*?"<>|]+', " ", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip(" .") or "audio"


def get_unique_path(file_path: str) -> str:
    if not os.path.exists(file_path):
        return file_path

    base_path, extension = os.path.splitext(file_path)
    counter = 2

    while True:
        candidate = f"{base_path} ({counter}){extension}"
        if not os.path.exists(candidate):
            return candidate

        counter += 1
