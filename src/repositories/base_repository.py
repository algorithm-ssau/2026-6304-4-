from sqlalchemy.ext.asyncio import AsyncSession

from database.session import AsyncSessionUtil

class BaseRepository:
    session: AsyncSessionUtil

    def __init__(self, session: AsyncSession) -> None:
        self.session = AsyncSessionUtil(session)
