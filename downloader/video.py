import os
import json
import subprocess

import yt_dlp

from config.settings import STORAGE_PATH

TELEGRAM_UPLOAD_LIMIT = 49 * 1024 * 1024
TARGET_UPLOAD_LIMIT = 45 * 1024 * 1024
MIN_VIDEO_BITRATE = 120_000
DEFAULT_AUDIO_BITRATE = 64_000

VIDEO_FORMATS = (
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
            file_path, duration = download_video_format(url, video_format)
        except yt_dlp.utils.DownloadError as error:
            last_error = error
            continue

        try:
            prepared_path = prepare_for_telegram(file_path, duration)
        except VideoTooLargeError:
            remove_file(file_path)
            continue

        if prepared_path != file_path:
            remove_file(file_path)

        return prepared_path

    if last_error:
        raise VideoTooLargeError(
            "Не удалось скачать видео в подходящем размере."
        ) from last_error

    raise VideoTooLargeError(
        "Даже самое лёгкое качество получилось слишком большим для Telegram."
    )


def download_video_format(
    url: str,
    video_format: str,
) -> tuple[str, int | float | None]:
    options = {
        "format": video_format,
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
            return file_path, info.get("duration")

    base_name = os.path.splitext(filename)[0]
    for file_path in (f"{base_name}.mp4", filename):
        if os.path.exists(file_path):
            return file_path, info.get("duration")

    raise FileNotFoundError("Не удалось найти скачанный видеофайл.")


def prepare_for_telegram(file_path: str, duration: int | float | None) -> str:
    normalized_path = normalize_for_telegram(file_path)

    if get_file_size(normalized_path) <= TELEGRAM_UPLOAD_LIMIT:
        return normalized_path

    remove_file(normalized_path)
    return compress_for_telegram(file_path, duration)


def normalize_for_telegram(file_path: str) -> str:
    base_name = os.path.splitext(file_path)[0]
    output_path = f"{base_name}_normalized.mp4"

    command = [
        "ffmpeg",
        "-y",
        "-i",
        file_path,
        "-vf",
        "scale=854:854:force_original_aspect_ratio=decrease:"
        "force_divisible_by=2",
        "-r",
        "30",
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "23",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        str(DEFAULT_AUDIO_BITRATE),
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

    if result.returncode != 0 or not os.path.exists(output_path):
        remove_file(output_path)
        raise VideoTooLargeError("Не удалось подготовить видео через ffmpeg.")

    return output_path


def compress_for_telegram(file_path: str, duration: int | float | None) -> str:
    if not duration or duration <= 0:
        raise VideoTooLargeError("Не удалось определить длительность видео.")

    total_bitrate = int((TARGET_UPLOAD_LIMIT * 8) / duration)
    audio_bitrate = DEFAULT_AUDIO_BITRATE
    video_bitrate = total_bitrate - audio_bitrate

    if video_bitrate < MIN_VIDEO_BITRATE:
        raise VideoTooLargeError(
            "Ролик слишком длинный, нормальное качество не поместится в лимит."
        )

    base_name = os.path.splitext(file_path)[0]
    output_path = f"{base_name}_telegram.mp4"

    command = [
        "ffmpeg",
        "-y",
        "-i",
        file_path,
        "-vf",
        "scale=854:854:force_original_aspect_ratio=decrease:"
        "force_divisible_by=2",
        "-r",
        "30",
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-b:v",
        str(video_bitrate),
        "-pix_fmt",
        "yuv420p",
        "-maxrate",
        str(video_bitrate),
        "-bufsize",
        str(video_bitrate * 2),
        "-c:a",
        "aac",
        "-b:a",
        str(audio_bitrate),
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

    if result.returncode != 0 or not os.path.exists(output_path):
        remove_file(output_path)
        raise VideoTooLargeError("Не удалось сжать видео через ffmpeg.")

    if get_file_size(output_path) > TELEGRAM_UPLOAD_LIMIT:
        remove_file(output_path)
        raise VideoTooLargeError(
            "После сжатия видео всё равно больше лимита Telegram."
        )

    return output_path


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
