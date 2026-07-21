import os

import yt_dlp

from config.settings import STORAGE_PATH

TELEGRAM_UPLOAD_LIMIT = 49 * 1024 * 1024

VIDEO_FORMATS = (
    "bv*[height<=720][ext=mp4]+ba[ext=m4a]/"
    "b[height<=720][ext=mp4]/best[height<=720]",
    "bv*[height<=480][ext=mp4]+ba[ext=m4a]/"
    "b[height<=480][ext=mp4]/best[height<=480]",
    "bv*[height<=360][ext=mp4]+ba[ext=m4a]/"
    "b[height<=360][ext=mp4]/best[height<=360]",
    "worst[ext=mp4]/worst",
)


class VideoTooLargeError(Exception):
    """Видео не удалось уложить в лимит Telegram Bot API."""


def download_video(url: str) -> str:
    os.makedirs(STORAGE_PATH, exist_ok=True)

    last_error: Exception | None = None

    for video_format in VIDEO_FORMATS:
        try:
            file_path = download_video_format(url, video_format)
        except yt_dlp.utils.DownloadError as error:
            last_error = error
            continue

        if get_file_size(file_path) <= TELEGRAM_UPLOAD_LIMIT:
            return file_path

        remove_file(file_path)

    if last_error:
        raise VideoTooLargeError(
            "Не удалось скачать видео в подходящем размере."
        ) from last_error

    raise VideoTooLargeError(
        "Даже самое лёгкое качество получилось слишком большим для Telegram."
    )


def download_video_format(url: str, video_format: str) -> str:
    options = {
        "format": video_format,
        "outtmpl": f"{STORAGE_PATH}/%(title)s_%(format_id)s.%(ext)s",
        "merge_output_format": "mp4",
        "max_filesize": TELEGRAM_UPLOAD_LIMIT,
        "noplaylist": True,
    }

    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)

    for item in info.get("requested_downloads", []):
        file_path = item.get("filepath")
        if file_path and os.path.exists(file_path):
            return file_path

    base_name = os.path.splitext(filename)[0]
    for file_path in (f"{base_name}.mp4", filename):
        if os.path.exists(file_path):
            return file_path

    raise FileNotFoundError("Не удалось найти скачанный видеофайл.")


def get_file_size(file_path: str) -> int:
    return os.path.getsize(file_path)


def remove_file(file_path: str) -> None:
    if os.path.exists(file_path):
        os.remove(file_path)
