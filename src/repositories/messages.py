from sqlalchemy import select, delete
from models.messages import Message
from repositories.base_repository import BaseRepository


class MessagesRepository(BaseRepository):

    LIMIT = 20

    async def get_message_history(self, user_id: int) -> list[dict]:
        """Получает историю сообщений пользователя в формате для AI API"""
        stmt = (
            select(Message)
            .where(Message.user_id == user_id)
            .order_by(Message.created_at.desc())
            .limit(self.LIMIT)
        )
        result = await self.session.execute(stmt)
        messages = result.scalars().all()

        # Возвращаем в обратном порядке (от старых к новым)
        return [
            {"role": msg.role, "content": msg.content}
            for msg in reversed(messages)
        ]

    async def save_message(self, user_id: int, content: str, role: str):
        """Сохраняет сообщение в историю"""
        message = Message(
            user_id=user_id,
            role=role,
            content=content
        )
        self.session.add(message)
        await self.session.flush()

        # Удаляем старые сообщения если превышен лимит
        await self._cleanup_old_messages(user_id)

    async def _cleanup_old_messages(self, user_id: int):
        """Удаляет старые сообщения, оставляя только LIMIT последних"""
        # Получаем ID сообщений, которые нужно удалить
        subquery = (
            select(Message.id)
            .where(Message.user_id == user_id)
            .order_by(Message.created_at.desc())
            .limit(self.LIMIT)
        )

        stmt = delete(Message).where(
            Message.user_id == user_id,
            Message.id.not_in(subquery)
        )
        await self.session.execute(stmt)

