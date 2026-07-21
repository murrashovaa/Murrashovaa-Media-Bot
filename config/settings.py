import os

from dotenv import load_dotenv


load_dotenv()


BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = {
    int(admin_id)
    for admin_id in os.getenv("ADMIN_IDS", "").replace(" ", "").split(",")
    if admin_id
}
STORAGE_PATH = os.getenv("STORAGE_PATH", "storage/temp")
STORAGE_CLEANUP_MAX_AGE_HOURS = int(
    os.getenv("STORAGE_CLEANUP_MAX_AGE_HOURS", "12")
)
VIDEO_MAX_HEIGHT = int(os.getenv("VIDEO_MAX_HEIGHT", "1080"))
YTDLP_COOKIES_FILE = os.getenv("YTDLP_COOKIES_FILE") or os.path.join(
    STORAGE_PATH,
    "cookies",
    "youtube.txt",
)
YTDLP_COOKIES_FROM_BROWSER = os.getenv("YTDLP_COOKIES_FROM_BROWSER") or None
