import asyncio
from typing import List
from aiohttp import ClientSession
from decouple import config
from bs4 import BeautifulSoup

from database.models import Search, User
from database.decorators import connect_db


API_MOVIE_DATA_URL = config("API_MOVIE_DATA_URL")
MOVIE_MAP_URL = config("MOVIE_MAP_URL")


@connect_db
async def create_or_get_user(user) -> User:

    users = await User.filter(tg_id=user.id)

    if users:
        user = users[0]
    else:
        new_user = await User.create(tg_id=user.id, name=user.first_name)
        user = new_user

    return user


@connect_db
async def get_user(tg_id) -> User:

    return await User.filter(tg_id=tg_id).first()


async def create_search(name: str, tg_id: str) -> None:

    users = await User.filter(tg_id=tg_id)
    if users:
        user = users[0]
        await Search.create(movie_name=name, user=user)

    return


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


def convert_to_str(suggestions: List[str]) -> str:

    suggestions_str = ""
    for suggestion in suggestions:
        suggestions_str += suggestion

    return suggestions_str


async def search_movie(movie_name: str, user_id: str) -> str:

    request_url = API_MOVIE_DATA_URL.format(movie_name)

    async with ClientSession() as session:
        async with session.get(request_url) as resp:

            movie_dict = await resp.json()

            if not movie_dict.get("Error"):
                await create_search(movie_dict["Title"], user_id)
                return format_dict(movie_dict)
            else:
                return "Not Found :(\nAre you sure you movie name is correct?"


async def get_movie_data(movie_name: str) -> str:

    request_url = API_MOVIE_DATA_URL.format(movie_name)

    async with ClientSession() as session:
        async with session.get(request_url) as resp:
            movie_dict = await resp.json()
            return f"{movie_dict['Title']} - {movie_dict['imdbRating']}\n"


async def get_suggestions(movie_name: str) -> str:

    async with ClientSession() as session:
        async with session.get(MOVIE_MAP_URL.format(movie_name)) as response:
            html_text = await response.text()
            soup = BeautifulSoup(html_text, "html.parser")
            tasks = []
            a_links = soup.find_all("a")

            for link in a_links[3:13]:
                tasks.append(asyncio.create_task(get_movie_data(link.text)))

            suggestions = await asyncio.gather(*tasks)
            suggestions = convert_to_str(suggestions)

            if not tasks:
                suggestions = (
                    "Not Found :(\nAre you sure you sure movie name is correct?"
                )
            return suggestions


async def get_movie_names() -> List:

    url = 'http://www.imdb.com/chart/top'

    async with ClientSession() as session:
        async with session.get(url) as resp:
            resp_text = await resp.text()
            soup = BeautifulSoup(resp_text, 'html.parser')

            movie_tags = soup.select('td.titleColumn a')
            titles = [tag.text for tag in movie_tags]
            titles = list(set(titles))  # remove duplicates

            return titles
