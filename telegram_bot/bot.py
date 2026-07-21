import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession

from config.settings import BOT_TOKEN
from services.storage_cleanup import cleanup_storage
from telegram_bot.handlers import router

logger = logging.getLogger(__name__)


async def main():
    logging.basicConfig(level=logging.INFO)
    cleanup_storage()

    session = AiohttpSession(timeout=120)
    bot = Bot(token=BOT_TOKEN, session=session)

    dp = Dispatcher()
    dp.include_router(router)

    logger.info("Bot started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
