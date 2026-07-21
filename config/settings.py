import os

from dotenv import load_dotenv


load_dotenv()


BOT_TOKEN = os.getenv("BOT_TOKEN")
STORAGE_PATH = os.getenv("STORAGE_PATH", "storage/temp")
STORAGE_CLEANUP_MAX_AGE_HOURS = int(
    os.getenv("STORAGE_CLEANUP_MAX_AGE_HOURS", "12")
)
