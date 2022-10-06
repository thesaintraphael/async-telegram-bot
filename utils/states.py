from aiogram.dispatcher.filters.state import State, StatesGroup


class SearchState(StatesGroup):
    movie_name = State()


class SuggestState(SearchState):
    movie_name = State()
