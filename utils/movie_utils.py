import asyncio
import random
from typing import List


from bs4 import BeautifulSoup
from aiohttp import ClientSession


from env import get_env_variable


MOVIE_MAP_URL = "https://www.movie-map.com/{}"
API_MOVIE_DATA_URL = "http://www.omdbapi.com/?t={}&apikey=" + \
    get_env_variable("OMDB_API_KEY")


class StrConverter:

    @staticmethod
    def movie_dict_to_str(movie_dict: dict) -> str:
        return (
            f'Movie: {movie_dict["Title"]}\nReleased on: {movie_dict["Released"]}\nIMDb Rating: {movie_dict["imdbRating"]}\nRuntime: {movie_dict["Runtime"]}\n'
            f'Director: {movie_dict["Director"]}\nGenre: {movie_dict["Genre"]}\nActors: {movie_dict["Actors"]}\n'
            f"""<a href='{movie_dict["Poster"]}'>Poster: </a>\nView trailer <a href='https://www.imdb.com/title/{movie_dict["imdbID"]}/'>here</a>"""

        )

    @staticmethod
    def list_to_str(suggestions: List[str]) -> str:
        return "".join(suggestions)


class MovieListUtil:

    IMDB_URL = "http://www.imdb.com/chart/top"

    @staticmethod
    async def fetch_movies(url: str) -> List[str]:
        async with ClientSession() as session:
            async with session.get(url) as resp:
                resp_text = await resp.text()
                soup = BeautifulSoup(resp_text, "html.parser")

                movie_tags = soup.select("td.titleColumn a")
                titles = [tag.text for tag in movie_tags]
                return list(set(titles))

    @classmethod
    async def get_movies_list(cls) -> List[str]:
        return await cls.fetch_movies(cls.IMDB_URL)

    @classmethod
    async def get_series_list(cls) -> List[str]:
        return await cls.fetch_movies(f"{cls.IMDB_URL}tv")


class MovieScrapper:

    def __init__(self, movie_name) -> None:
        self.movie_name = movie_name

    async def search_movie(self) -> str:
        request_url = API_MOVIE_DATA_URL.format(self.movie_name)

        async with ClientSession() as session:
            async with session.get(request_url) as resp:
                movie_dict = await resp.json()
                if movie_dict.get("Title"):
                    return StrConverter.movie_dict_to_str(movie_dict)
                else:
                    return "Not Found :(\nAre you sure movie name is correct?"

    async def get_movie_data(self) -> str:

        request_url = API_MOVIE_DATA_URL.format(self.movie_name)

        async with ClientSession() as session:
            async with session.get(request_url) as resp:
                movie_dict = await resp.json()
                return f"{movie_dict['Title']} - {movie_dict['imdbRating']}\n"

    async def get_suggestions(self) -> str:
        async with ClientSession() as session:
            async with session.get(MOVIE_MAP_URL.format(self.movie_name)) as response:
                html_text = await response.text()
                soup = BeautifulSoup(html_text, "html.parser")
                a_links = soup.find_all("a")

                tasks = [asyncio.create_task(self.get_movie_data(link.text))
                         for link in a_links[3:13]]

                suggestions = StrConverter.list_to_str(await asyncio.gather(*tasks))

                if not tasks:
                    suggestions = "Not Found :(\nAre you sure movie name is correct?"
                return suggestions

    @classmethod
    async def get_random_movie(cls, movie_list) -> str:
        while True:
            index = random.randint(0, len(movie_list) - 1)
            result = await cls(movie_list[index]).search_movie()
            if "Not found" not in result:
                return result
