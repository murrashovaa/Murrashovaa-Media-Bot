import os

from dotenv import load_dotenv


load_dotenv()


BOT_TOKEN = os.getenv("BOT_TOKEN")
STORAGE_PATH = os.getenv("STORAGE_PATH", "storage/temp")
STORAGE_CLEANUP_MAX_AGE_HOURS = int(
    os.getenv("STORAGE_CLEANUP_MAX_AGE_HOURS", "12")
)
VIDEO_MAX_HEIGHT = int(os.getenv("VIDEO_MAX_HEIGHT", "1080"))
YTDLP_COOKIES_FILE = os.getenv("YTDLP_COOKIES_FILE") or None
