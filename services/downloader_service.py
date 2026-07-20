from urllib.parse import urlparse

from downloader.youtube import download_youtube_audio
from downloader.soundcloud import download_soundcloud_audio


class UnsupportedSourceError(Exception):
    """Ссылка ведёт на неподдерживаемый источник."""


def download_audio(url: str) -> tuple[str, str]:
    """
    Определяет источник ссылки и скачивает аудио.

    Returns:
        tuple[str, str]: путь к файлу и название источника.
    """

    normalized_url = url.strip()

    if not normalized_url:
        raise ValueError("Ссылка не может быть пустой.")

    hostname = urlparse(normalized_url).hostname

    if hostname is None:
        raise ValueError("Не удалось распознать ссылку.")

    hostname = hostname.lower()

    if hostname.startswith("www."):
        hostname = hostname[4:]

    if hostname in {
        "youtube.com",
        "m.youtube.com",
        "music.youtube.com",
        "youtu.be",
    }:
        file_path = download_youtube_audio(normalized_url)
        return file_path, "YouTube"

    if hostname in {
        "soundcloud.com",
        "m.soundcloud.com",
        "on.soundcloud.com",
    }:
        file_path = download_soundcloud_audio(normalized_url)
        return file_path, "SoundCloud"

    raise UnsupportedSourceError(
        "Поддерживаются только ссылки YouTube и SoundCloud."
    )