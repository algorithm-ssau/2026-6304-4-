from sqlalchemy import select
from models.messages import Message
from repositories.base_repository import BaseRepository


class MessagesRepository(BaseRepository):

    LIMIT = 10

    async def get_message_history(self, user_id) -> list[Message]:
        return []

    async def write_new_message(self, user_id, message: Message):
        prev_msgs = await self.get_message_history(user_id)
        if len(prev_msgs) > self.LIMIT:
            msgs_to_cls = prev_msgs[-self.LIMIT:]
            await self.clear_messages(msgs_to_cls)
        
        self.session.add(message)


    async def clear_messages(self, msg_to_cls: list[Message]):
        for msg in msg_to_cls:
            await self.session.delete(msg)

