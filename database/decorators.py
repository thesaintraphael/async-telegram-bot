from tortoise import Tortoise
from . import config


def connect_db(function):
    async def wrapper(*args):
        await Tortoise.init(
            db_url=config.DATABASE_URL,
            modules={"models": ["database.models", "aerich.models"]},
        )

        return await function(*args)

    return wrapper
