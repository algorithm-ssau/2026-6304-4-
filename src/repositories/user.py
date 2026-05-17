from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from models.user import User
from repositories.base_repository import BaseRepository


class UserRepository(BaseRepository):

    async def get_all(self):
        """Получить всех пользователей"""
        stmt = select(User)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_id(self, user_id: int) -> User | None:
        """Получить пользователя по ID"""
        stmt = select(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_tg_id(self, tg_id: int) -> User | None:
        """Получить пользователя по Telegram ID"""
        stmt = select(User).where(User.tg_id == tg_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, user: User) -> User:
        """Создать нового пользователя"""
        user = await self.session.save(user)
        return user

    async def update(self, user: User) -> User:
        """Обновить пользователя"""
        user = await self.session.save(user)
        return user

    async def delete(self, user: User):
        """Удалить пользователя"""
        await self.session.delete(user)
        await self.session.flush()

    async def add_token(self, user: User, token: str):
        """Добавить токен пользователю"""
        user.golden_token = token

    async def set_polling(self, user: User, is_polling: bool):
        """Установить статус polling"""
        user.is_polling = is_polling