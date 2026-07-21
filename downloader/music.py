import os

import yt_dlp

from config.settings import STORAGE_PATH


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

    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)

    file_path = f"{os.path.splitext(filename)[0]}.mp3"

    if os.path.exists(file_path):
        return file_path

    raise FileNotFoundError("Не удалось найти скачанный аудиофайл.")


def download_youtube_audio(url: str) -> str:
    return download_music(url)


def download_soundcloud_audio(url: str) -> str:
    return download_music(url)
