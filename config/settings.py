import os
from dotenv import load_dotenv


load_dotenv()


BOT_TOKEN = os.getenv("BOT_TOKEN")

DATABASE_URL = os.getenv(
    "DATABASE_URL"
)

STORAGE_PATH = os.getenv(
    "STORAGE_PATH"
)