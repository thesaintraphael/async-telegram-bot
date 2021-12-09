import logging

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ParseMode
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.utils.emoji import emojize
from aiogram.utils.markdown import text
from decouple import config

from utils.funcs import create_or_get_user, get_suggestions, search_movie, get_user
from utils.states import SearchState, SuggestState
from database.decorators import connect_db

from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler


async def tick():
    print("Tick! The time is: %s" % datetime.now())


API_TOKEN = config("API_TOKEN")

logging.basicConfig(level=logging.INFO)


bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


# HANDLE COMMANDS


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


@dp.message_handler(commands=["search"])
async def search(message: types.Message):

    await SearchState.movie_name.set()
    await message.reply(
        "Enter the movie name you want to explore.. \n Type cancel to cancel"
    )


@dp.message_handler(commands=["suggest"])
async def suggest(message: types.Message):

    await SuggestState.movie_name.set()
    await message.reply(
        "Enter a movie name to get sugesstions..\nType cancel to cancel"
    )


@dp.message_handler(commands=['subscribe'])
async def subscribe(message: types.Message):

    tg_id = types.User.get_current().id
    user = await get_user(tg_id)
    if user.subscribed:
       reply_text = "You are already subscribed"
    else:
        user.subscribed = True
        await user.save()
        reply_text = "You are successfully subscribed"
    
    return await message.reply(reply_text)


@dp.message_handler(commands=['unsubscribe'])
async def unsubscribe(message: types.Message):

    tg_id = types.User.get_current().id
    user = await get_user(tg_id)
    if not user.subscribed:
        reply_text = "You are not subscribed currently"
    else:
        user.subscribed = False
        await user.save()
        reply_text = "You are successfully unsubscribed"

    return await message.reply(reply_text)


@dp.message_handler()
async def echo(message: types.Message):

    reply_text = "Sorry,\nI dont understand this command yet :disappointed_relieved:"
    reply_text = emojize(text(reply_text))
    return await bot.send_message(
        message.chat.id, reply_text, parse_mode=ParseMode.MARKDOWN
    )


# PROCESS STATES


@dp.message_handler(state=SuggestState)
async def process_suggest_movie_name(message: types.Message, state: FSMContext):

    result = await get_suggestions(message.text)
    await state.finish()
    await message.reply(result)


@dp.message_handler(state=SearchState.movie_name)
async def process_movie_name(message: types.Message, state: FSMContext):

    user_id = types.User.get_current().id
    result = await search_movie(message.text, str(user_id))
    await state.finish()
    await bot.send_message(chat_id=user_id, text=result, parse_mode=ParseMode.HTML)


if __name__ == "__main__":

    scheduler = AsyncIOScheduler({'apscheduler.timezone': 'Europe/London'})
    scheduler.add_job(tick, 'cron', hour='11', minute='3', day='*')

    scheduler.start()
    executor.start_polling(dp, skip_updates=True)
