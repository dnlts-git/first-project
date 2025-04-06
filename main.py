import asyncio
import contextlib
import os

import aiogram
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv

from regular_user import user

load_dotenv()

bot = Bot(token=os.getenv('TOKEN'), default=DefaultBotProperties(parse_mode='HTML'))
dp = Dispatcher()


async def on_startup():
    dp.include_router(user)
    await bot.delete_webhook(drop_pending_updates=True)

async def main():
    await on_startup()
    try:
        await dp.start_polling(bot)
    except Exception as e:
        print(f'Exception: {e}')


if __name__ == '__main__':
    with contextlib.suppress(KeyboardInterrupt, SystemExit):
        asyncio.run(main())
