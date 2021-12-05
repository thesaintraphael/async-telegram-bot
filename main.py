import logging

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ParseMode
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from decouple import config

from utils.funcs import create_or_get_user, search_movie
from utils.states import SearchState
from database.decorators import connect_db


API_TOKEN = config("API_TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


@dp.message_handler(commands=["start"])
@connect_db
async def start(message: types.Message):
    user = await create_or_get_user(types.User.get_current())
    await message.reply(f"Hi, {user.name}")


@dp.message_handler(state="*", commands="cancel")
@dp.message_handler(Text(equals="cancel", ignore_case=True), state="*")
async def cancel_handler(message: types.Message, state: FSMContext):

    current_state = await state.get_state()
    if current_state is None:
        return
    
    logging.info("Cancelling state %r", current_state)
    await state.finish()
    await message.reply("Cancelled", reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(commands=['search'])
async def search(message: types.Message):

    await SearchState.movie_name.set()
    await message.reply("Enter the movie name you want to explore.. \n Type cancel to cancel")


@dp.message_handler(state=SearchState.movie_name)
async def process_movie_name(message: types.Message, state: FSMContext):
    
    result = await search_movie(message.text)
    await state.finish()
    await bot.send_message(chat_id=types.User.get_current().id, text=result, parse_mode=ParseMode.HTML)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
