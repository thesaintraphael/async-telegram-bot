from aiogram.types import message
from aiohttp import ClientSession
from decouple import config

from database.models import User


API_MOVIE_DATA_URL = config("API_MOVIE_DATA_URL")


async def create_or_get_user(user) -> User:

    users = await User.filter(tg_id=user.id)

    if users:
        user = users[0]
    else:
        new_user = await User.create(tg_id=user.id, name=user.first_name)
        user = new_user

    return user


def format_dict(movie_dict: dict) -> str:

    message = (
        "Movie: {}"
        "\nReleased on: {}\nIMDb Rating: {}\nRuntime: "
        "{}\n".format(
            movie_dict["Title"],
            movie_dict["Released"],
            movie_dict["imdbRating"],
            movie_dict["Runtime"],
        )
    )
    message += "Director: {}\nGenre: {}\nActors: " "{}\n".format(
        movie_dict["Director"], movie_dict["Genre"], movie_dict["Actors"]
    )
    message += (
        "<a href='{}'>Poster: </a>\nView trailer <a href='https://www.imdb.com/title/{}/'>here</a>"
        "".format(movie_dict["Poster"], movie_dict["imdbID"])
    )

    return message


async def search_movie(movie_name) -> str:

    request_url = API_MOVIE_DATA_URL.format(movie_name)

    async with ClientSession() as session:
        async with session.get(request_url) as resp:
            
            movie_dict = await resp.json()
            
            if not movie_dict.get('Error'):
                return format_dict(movie_dict)
            else:
                return 'Not Found :(\n Are you sure you typed right?'
