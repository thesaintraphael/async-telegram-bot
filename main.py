import logging

from aiogram import Bot, Dispatcher, executor, types
from decouple import config
from utils.funcs import create_or_get_user
from database.decorators import connect_db


API_TOKEN = config("API_TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=["start"])
@connect_db
async def start(message: types.Message):
    user = await create_or_get_user(types.User.get_current())
    await message.reply(f"Hi, {user.name}")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
