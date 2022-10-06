from env import get_env_variable


DEBUG = get_env_variable("DEBUG")
DATABASE_URL = get_env_variable(
    "DATABASE_TEST_URL") if DEBUG else get_env_variable("DATABASE_URL")
TORTOISE_ORM = {
    "connections": {"default": DATABASE_URL},
    "apps": {
        "models": {
            "models": ["database.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}
