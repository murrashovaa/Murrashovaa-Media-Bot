import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession

from config.settings import BOT_TOKEN
from telegram_bot.handlers import router



async def main():

    session = AiohttpSession(
        timeout=120
    )

    bot = Bot(
        token=BOT_TOKEN,
        session=session
    )


    dp = Dispatcher()

    dp.include_router(router)


    print("Bot started")


    await dp.start_polling(bot)



if __name__ == "__main__":
    asyncio.run(main())