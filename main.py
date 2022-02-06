import asyncio
import logging

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ParseMode
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.utils.emoji import emojize
from aiogram.utils.markdown import text
from decouple import config

from utils.funcs import (
    create_or_get_user,
    get_stats,
    get_suggestions,
    search_movie,
    get_user,
    get_movie_names,
    get_random_movie,
    get_subscribed_users_list,
)
from utils.states import SearchState, SuggestState
from database.decorators import connect_db

from apscheduler.schedulers.asyncio import AsyncIOScheduler


API_TOKEN = config("API_TOKEN")
MOVIE_LIST = []
SERIES_LIST = []


logging.basicConfig(level=logging.INFO)


bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


# DECORATOR


def only_admin(func):
    async def wrapper(*args, **kwargs):
        if str(types.User.get_current().id) == config("ADMIN_TELEGRAM_ID"):
            return await func(*args)
        return await echo(*args)
        
    return wrapper


# HANDLE COMMANDS


@dp.message_handler(commands=["start"])
@connect_db
async def start(message: types.Message):
    user = await create_or_get_user(types.User.get_current())
    reply_text = (
        "Hi, {}. Welcome to MovieScrap {}\nType /view to view all possible commands\nVisit our website:"
        "https://moviescrap.herokuapp.com/".format(user.name, u"\U0001F973")
    )
    await message.reply(reply_text)


@dp.message_handler(commands=["admin"])
@only_admin
@connect_db
async def admin(message: types.Message):
    stats = await get_stats()
    return await message.reply(f"Users count: {stats['all_count']}\n"
                         f"Subscribed users count: {stats['subs_count']}")


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
        "Enter the movie name you want to explore..\nType cancel to cancel"
    )


@dp.message_handler(commands=["suggest"])
async def suggest(message: types.Message):

    await SuggestState.movie_name.set()
    await message.reply(
        "Enter a movie name to get suggestions..\nType cancel to cancel"
    )


@dp.message_handler(commands=["subscribe"])
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


@dp.message_handler(commands=["unsubscribe"])
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


@dp.message_handler(commands=["next"])
async def next_movie(message: types.Message):

    reply_text = await get_random_movie(MOVIE_LIST)
    return await message.reply(reply_text, parse_mode=ParseMode.HTML)


@dp.message_handler(commands=["series"])
async def series(message: types.Message):

    reply_text = await get_random_movie(SERIES_LIST)
    return await message.reply(
        reply_text.replace("Movie", "Series"), parse_mode=ParseMode.HTML
    )


@dp.message_handler(commands=["view"])
async def view(message: types.Message):

    reply_text = "/start - Starts the bot\n/view - Views all available commands\n/next - Generate next random movie " \
                 "suggestion\n/series - Generate next random TV show suggestion\n/search - Return the data movie you " \
                 "want to\n/suggest - Suggest couple of movies based on your input\n/subscribe - Subscribe to " \
                 "daily/weekly suggestions\n/unsubscribe - Unsubscribe from daily/weekly suggestions "
    await message.reply(reply_text)


@dp.message_handler()
async def echo(message: types.Message):

    reply_text = "Sorry,\nI dont understand this command yet :disappointed_relieved:\nType /view to see all possible " \
                 "commands "
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


@dp.message_handler(state=SearchState)
async def process_movie_name(message: types.Message, state: FSMContext):

    user_id = types.User.get_current().id
    result = await search_movie(message.text, str(user_id), search=False)
    await state.finish()
    await bot.send_message(chat_id=user_id, text=result, parse_mode=ParseMode.HTML)


# PERIODIC TASKS (EXTERNAL)


@connect_db
async def daily_suggestion():
    users = await get_subscribed_users_list()
    movie_data = "Suggestion of the day:\n" + await get_random_movie(MOVIE_LIST)

    for user in users:
        try:
            await bot.send_message(
                chat_id=user.tg_id, text=movie_data, parse_mode=ParseMode.HTML
            )
        except Exception as e:
            logging.error("Cannot send message:  %r", e)
            continue


@connect_db
async def weekly_suggestion():
    users = await get_subscribed_users_list()
    movie_data = (
        "Series of the week:\n" + await get_random_movie(SERIES_LIST)
    ).replace("Movie", "Series")

    for user in users:
        try:
            await bot.send_message(
                chat_id=user.tg_id, text=movie_data, parse_mode=ParseMode.HTML
            )
        except Exception as e:
            logging.error("Cannot send message:  %r", e)
            continue


#  INTERNAL COMMANDS


async def update_movie_names():

    global MOVIE_LIST
    global SERIES_LIST

    MOVIE_LIST = await get_movie_names()
    SERIES_LIST = await get_movie_names(series=True)


if __name__ == "__main__":

    asyncio.get_event_loop().run_until_complete(update_movie_names())

    scheduler = AsyncIOScheduler({"apscheduler.timezone": "Europe/London"})
    scheduler.add_job(update_movie_names, "cron", day="1st mon")
    scheduler.add_job(daily_suggestion, "cron", hour="10", minute="00")
    scheduler.add_job(
        weekly_suggestion, "cron", hour="9", minute="00", day_of_week="sun", week="*"
    )

    scheduler.start()
    executor.start_polling(dp, skip_updates=True)
