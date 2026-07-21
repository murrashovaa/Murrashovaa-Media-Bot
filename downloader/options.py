import os

from config.settings import YTDLP_COOKIES_FILE, YTDLP_COOKIES_FROM_BROWSER


def add_ytdlp_auth_options(options: dict) -> dict:
    add_cookies_file(options)
    add_browser_cookies(options)
    return options


def add_cookies_file(options: dict) -> None:
    if not YTDLP_COOKIES_FILE:
        return

    cookies_file = os.path.expanduser(YTDLP_COOKIES_FILE)
    if os.path.exists(cookies_file):
        options["cookiefile"] = cookies_file


def add_browser_cookies(options: dict) -> None:
    if not YTDLP_COOKIES_FROM_BROWSER or "cookiefile" in options:
        return

    options["cookiesfrombrowser"] = (YTDLP_COOKIES_FROM_BROWSER,)
