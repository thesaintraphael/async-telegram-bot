from decouple import config


DEBUG = config("DEBUG")
DATABASE_URL = config("DATABASE_TEST_URL") if DEBUG else config("DATABASE_URL")
TORTOISE_ORM = {
    "connections": {"default": DATABASE_URL},
    "apps": {
        "models": {
            "models": ["database.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}
