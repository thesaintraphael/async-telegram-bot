from typing import List

from aiogram import types

from database.models import User
from database.decorators import connect_db


class UserUtil:

    @staticmethod
    @connect_db
    async def create_or_get_user(user: types.User) -> User:
        users = await User.filter(tg_id=user.id)
        if users:
            return users[0]
        else:
            return await User.create(tg_id=user.id, name=user.first_name)

    @staticmethod
    @connect_db
    async def get_user(tg_id: str) -> User:
        return await User.get(tg_id=tg_id)

    @staticmethod
    async def get_subscribed_user_list() -> List[User]:
        return await User.filter(subscribed=True)
