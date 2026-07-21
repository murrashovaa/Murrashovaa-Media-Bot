YOUTUBE_AUTH_ERROR_MARKERS = (
    "sign in to confirm you're not a bot",
    "sign in to confirm you’re not a bot",
    "use --cookies-from-browser or --cookies",
)


class YouTubeAuthError(Exception):
    """YouTube запросил авторизацию или антибот-проверку."""


def raise_friendly_ytdlp_error(error: Exception) -> None:
    message = str(error).lower()

    if any(marker in message for marker in YOUTUBE_AUTH_ERROR_MARKERS):
        raise YouTubeAuthError(
            "YouTube попросил дополнительную проверку. "
            "Бот попробует работать через общий YouTube-доступ, "
            "если он настроен на машине с ботом."
        ) from error

    raise error
