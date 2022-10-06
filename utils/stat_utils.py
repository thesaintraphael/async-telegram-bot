from typing import Tuple

from database.models import Search, User


class Statistics:

    @staticmethod
    async def get_most_searched_movie_name() -> Tuple:
        searches = {}
        searches_list = await Search.all()
        for search in searches_list:
            if search.movie_name not in searches:
                searches[search.movie_name] = 1
            else:
                searches[search.movie_name] += 1

        search_stats = sorted(
            searches.items(), key=lambda search: search[1], reverse=True)

        return search_stats[0] if search_stats else (None, 0)

    @staticmethod
    async def get_subscribed_users_count() -> int:
        return await User.filter(subscribed=True).count()

    @staticmethod
    async def get_users_count() -> int:
        return await User.all().count()

    @classmethod
    async def get_stats(cls) -> dict:

        search_stats = await cls.get_most_searched_movie_name()

        return {
            "subs_count": await cls.get_subscribed_users_count(),
            "all_count": await cls.get_users_count(),
            "most_searched": search_stats[0],
            "searched_times": search_stats[1]
        }
