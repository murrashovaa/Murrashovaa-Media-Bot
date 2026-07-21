import os

import yt_dlp

from config.settings import STORAGE_PATH


def download_video(url: str) -> str:
    os.makedirs(STORAGE_PATH, exist_ok=True)

    options = {
        "format": "bestvideo+bestaudio/best",
        "outtmpl": f"{STORAGE_PATH}/%(title)s.%(ext)s",
        "merge_output_format": "mp4",
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
