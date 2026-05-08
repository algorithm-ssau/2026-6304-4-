from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from config import get_config
from database.database import get_session
from gateaway.ai_api import AiApi
from gateaway.funpay_api import FunPayApiGateaway
from repositories.messages import MessagesRepository
from repositories.user import UserRepository


def get_user_repo(session: AsyncSession):
    return UserRepository(
        session=session
    )

def get_messages_repo(session: AsyncSession):
    return MessagesRepository(
        session=session
    )

def get_ai_api(session: AsyncSession = Depends(get_session)):
    conf = get_config()
    return AiApi(
        url=conf.ai.ai_url,
        model=conf.ai.model,
        messages_repo=get_messages_repo(session)
    )
