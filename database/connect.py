from tortoise import Tortoise, run_async

import config


async def init():
    await Tortoise.init(
        db_url=config.DATABASE_URL, modules={"models": ["models", "aerich.models"]}
    )
    await Tortoise.generate_schemas()


if __name__ == "__main__":
    run_async(init())
