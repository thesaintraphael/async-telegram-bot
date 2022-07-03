import asyncio
from unittest import TestCase

from utils.funcs import get_movie_names, get_random_movie, search_movie


class TestUtils(TestCase):
    def setUp(self) -> None:
        self.loop = asyncio.get_event_loop()
        self.movie_list = ["The Prestige", "Metro", "Some random text"]

    def get_search_result(self, movie_name):
        return self.loop.run_until_complete(search_movie(movie_name, search=False))

    def test_search_movie_found(self):
        result = self.get_search_result("Dark")
        self.assertFalse("Not" in result)

    def test_search_movie_not_found(self):
        result = self.get_search_result("Some random text")
        self.assertTrue("Not" in result)

    def test_get_random_movie(self):
        result = self.loop.run_until_complete(
            get_random_movie(self.movie_list))
        self.assertTrue("Movie" in result)

    def test_get_movie_names(self):
        result = self.loop.run_until_complete(get_movie_names())
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 250)
