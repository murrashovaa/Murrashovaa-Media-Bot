import os

from config.settings import YTDLP_COOKIES_FILE


def add_ytdlp_auth_options(options: dict) -> dict:
    if not YTDLP_COOKIES_FILE:
        return options

    cookies_file = os.path.expanduser(YTDLP_COOKIES_FILE)
    if not os.path.exists(cookies_file):
        raise FileNotFoundError(
            f"Файл cookies для yt-dlp не найден: {cookies_file}"
        )

    options["cookiefile"] = cookies_file
    return options
