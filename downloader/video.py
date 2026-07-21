import json
import os
import subprocess

import yt_dlp

from config.settings import STORAGE_PATH

TELEGRAM_UPLOAD_LIMIT = 49 * 1024 * 1024
BEST_VIDEO_FORMAT = "bestvideo+bestaudio/best"
COMPRESSION_PRESETS = (
    {"height": 1080, "crf": 24, "audio_bitrate": "128k"},
    {"height": 720, "crf": 26, "audio_bitrate": "128k"},
    {"height": 540, "crf": 28, "audio_bitrate": "96k"},
    {"height": 480, "crf": 30, "audio_bitrate": "96k"},
    {"height": 360, "crf": 32, "audio_bitrate": "64k"},
    {"height": 240, "crf": 35, "audio_bitrate": "64k"},
)


class VideoTooLargeError(Exception):
    """Видео больше лимита Telegram Bot API."""


def download_video(url: str) -> str:
    os.makedirs(STORAGE_PATH, exist_ok=True)

    file_path = download_best_video(url)
    prepared_path = remux_for_telegram(file_path)

    if prepared_path != file_path:
        remove_file(file_path)

    if get_file_size(prepared_path) > TELEGRAM_UPLOAD_LIMIT:
        compressed_path = compress_until_telegram_limit(prepared_path)
        remove_file(prepared_path)
        return compressed_path

    return prepared_path


def download_best_video(url: str) -> str:
    options = {
        "format": BEST_VIDEO_FORMAT,
        "outtmpl": f"{STORAGE_PATH}/%(title)s_%(format_id)s.%(ext)s",
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


def remux_for_telegram(file_path: str) -> str:
    base_name = os.path.splitext(file_path)[0]
    output_path = f"{base_name}_telegram.mp4"

    command = [
        "ffmpeg",
        "-y",
        "-i",
        file_path,
        "-map",
        "0:v:0",
        "-map",
        "0:a?",
        "-c",
        "copy",
        "-movflags",
        "+faststart",
        output_path,
    ]
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode == 0 and os.path.exists(output_path):
        return output_path

    remove_file(output_path)
    return file_path


def compress_until_telegram_limit(file_path: str) -> str:
    for index, preset in enumerate(COMPRESSION_PRESETS, start=1):
        output_path = compress_for_telegram(file_path, preset, index)

        if get_file_size(output_path) <= TELEGRAM_UPLOAD_LIMIT:
            return output_path

        remove_file(output_path)

    raise VideoTooLargeError(
        "Даже после сильного сжатия видео больше лимита Telegram Bot API."
    )


def compress_for_telegram(
    file_path: str,
    preset: dict,
    index: int,
) -> str:
    base_name = os.path.splitext(file_path)[0]
    output_path = f"{base_name}_compressed_{index}.mp4"
    height = preset["height"]

    command = [
        "ffmpeg",
        "-y",
        "-i",
        file_path,
        "-map",
        "0:v:0",
        "-map",
        "0:a?",
        "-vf",
        f"scale=-2:'min({height},ih)'",
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        str(preset["crf"]),
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        preset["audio_bitrate"],
        "-movflags",
        "+faststart",
        output_path,
    ]
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode == 0 and os.path.exists(output_path):
        return output_path

    remove_file(output_path)
    raise VideoTooLargeError("Не удалось сжать видео через ffmpeg.")


def get_file_size(file_path: str) -> int:
    return os.path.getsize(file_path)


def get_video_dimensions(file_path: str) -> tuple[int | None, int | None]:
    command = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=width,height",
        "-of",
        "json",
        file_path,
    ]
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        return None, None

    data = json.loads(result.stdout)
    stream = (data.get("streams") or [{}])[0]
    return stream.get("width"), stream.get("height")


def remove_file(file_path: str) -> None:
    if os.path.exists(file_path):
        os.remove(file_path)
