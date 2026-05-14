from dataclasses import dataclass
from sqlalchemy.ext import asyncio

from models.user import User

@dataclass
class TaskService:
    async def start_task(self, user: User):
        pass

    async def stop_task(self, user: User):
        pass