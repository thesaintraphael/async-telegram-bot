import asyncio
from unittest import TestCase

from utils import MovieListUtil, MovieScrapper


class TestUtils(TestCase):
    def setUp(self) -> None:
        self.loop = asyncio.get_event_loop()
        self.movie_list = ["The Prestige", "Metro", "Some random text"]

    def get_search_result(self, movie_name):
        return self.loop.run_until_complete(MovieScrapper(movie_name).search_movie())

    def test_search_movie_found(self):
        result = self.get_search_result("Dark")
        self.assertFalse("Not" in result)

    def test_search_movie_not_found(self):
        result = self.get_search_result("Some random text")
        self.assertTrue("Not" in result)

    def test_get_random_movie(self):
        result = self.loop.run_until_complete(
            MovieScrapper.get_random_movie(self.movie_list[:3]))
        self.assertTrue("Movie" in result)

    def test_get_movie_names(self):
        result = self.loop.run_until_complete(MovieListUtil.get_movies_list())
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 250)
