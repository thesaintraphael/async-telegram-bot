
import functools
from aiogram import types
from decouple import config


def only_admin(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if str(types.User.get_current().id) == config("ADMIN_TELEGRAM_ID"):
            return func(*args, **kwargs)

        from main import echo
        return echo(*args, **kwargs)

    return wrapper
