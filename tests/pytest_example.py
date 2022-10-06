import pytest

from utils.funcs import search_movie, get_random_movie, get_movie_names


@pytest.mark.parametrize("name, found", [("Dark", True), ("Some random text", False)])
def test_search_movie(name, found, loop):

    result = loop.run_until_complete(search_movie(name))

    if found:
        assert "Not Found" not in result
    else:
        assert "Not Found" in result


@pytest.mark.parametrize("movie_list", [["The Prestige", "Metro", "Dark"]])
def test_get_random_movie(movie_list, loop):
    result = loop.run_until_complete(get_random_movie(movie_list))

    assert "Movie" in result


def test_get_movie_names(loop):
    result = loop.run_until_complete(get_movie_names())

    assert isinstance(result, list)
    assert len(result) == 250
