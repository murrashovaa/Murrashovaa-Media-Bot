from urllib.parse import urlparse

from downloader.music import download_music

YOUTUBE_HOSTS = {
    "youtube.com",
    "m.youtube.com",
    "music.youtube.com",
    "youtu.be",
}

SOUNDCLOUD_HOSTS = {
    "soundcloud.com",
    "m.soundcloud.com",
    "on.soundcloud.com",
}

TIKTOK_HOSTS = {
    "tiktok.com",
    "m.tiktok.com",
    "vm.tiktok.com",
    "vt.tiktok.com",
}

INSTAGRAM_HOSTS = {
    "instagram.com",
    "www.instagram.com",
    "m.instagram.com",
}


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

    hostname = get_hostname(normalized_url)

    if hostname is None:
        raise ValueError("Не удалось распознать ссылку.")

    if hostname in YOUTUBE_HOSTS:
        file_path = download_music(normalized_url)
        return file_path, "YouTube"

    if hostname in SOUNDCLOUD_HOSTS:
        file_path = download_music(normalized_url)
        return file_path, "SoundCloud"

    if hostname in TIKTOK_HOSTS:
        file_path = download_music(normalized_url)
        return file_path, "TikTok"

    if hostname in INSTAGRAM_HOSTS:
        file_path = download_music(normalized_url)
        return file_path, "Instagram"

    raise UnsupportedSourceError(
        "Поддерживаются ссылки YouTube, SoundCloud, TikTok и Instagram."
    )


def get_hostname(url: str) -> str | None:
    hostname = urlparse(url).hostname

    if hostname is None:
        return None

    hostname = hostname.lower()

    if hostname.startswith("www."):
        return hostname[4:]

    return hostname
