from sqlalchemy import select
from models.user import User
from repositories.base_repository import BaseRepository


class UserRepository(BaseRepository):

    async def get_all(self):
        pass

    async def find(self, user_id: int):
        return self.session.one((select(User).where(User.id == user_id)))

    async def find_by_tg_id(self, tg_id: int):
        return await self.session.one((select(User).where(User.tg_id == tg_id)))

    async def add_token(self, user: User, token: str):
        user.golden_token = token

    async def set_polling(self, user: User, is_polling: bool):
        user.is_polling = is_polling