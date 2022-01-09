from aiogram.dispatcher.filters.state import State, StatesGroup


class SearchState(StatesGroup):
    movie_name = State()


# creating another state due to Handlers
class SuggestState(StatesGroup):
    movie_name = State()
