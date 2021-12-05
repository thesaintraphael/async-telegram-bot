from tortoise import Tortoise, run_async
# from .config import DATABASE_URL
import config

print(config.DATABASE_URL)

async def init():
    await Tortoise.init(db_url=config.DATABASE_URL, modules={"models": ["models"]})
    await Tortoise.generate_schemas()


if __name__ == "__main__":
    run_async(init())
