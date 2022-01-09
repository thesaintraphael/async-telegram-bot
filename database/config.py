from decouple import config


DEBUG = config("DEBUG")
if DEBUG:
    DATABASE_URL = config("DATABASE_TEST_URL")
else:
    DATABASE_URL = config("DATABASE_URL")

TORTOISE_ORM = {
    "connections": {"default": DATABASE_URL},
    "apps": {
        "models": {
            "models": ["database.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}
