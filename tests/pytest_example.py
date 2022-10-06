import pytest

from utils import MovieScrapper, MovieListUtil


@pytest.mark.parametrize("name, found", [("Dark", True), ("Some random text", False)])
def test_search_movie(name, found, loop):

    result = loop.run_until_complete(MovieScrapper(name).search_movie())

    if found:
        assert "Not Found" not in result
    else:
        assert "Not Found" in result


@pytest.mark.parametrize("movie_list", [["The Prestige", "Metro", "Dark"]])
def test_get_random_movie(movie_list, loop):
    result = loop.run_until_complete(
        MovieScrapper.get_random_movie(movie_list))

    assert "Movie" in result


def test_get_movie_names(loop):
    result = loop.run_until_complete(MovieListUtil.get_movies_list())

    assert isinstance(result, list)
    assert len(result) == 250
