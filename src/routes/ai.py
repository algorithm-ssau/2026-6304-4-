from fastapi import APIRouter, Depends

from dependency import get_ai_api
from gateaway.ai_api import AiApi


router = APIRouter(prefix="ai")

@router.post("/chat")
async def chat():
    pass

@router.post("/start")
async def start(
    tg_id: int,
    service: AiApi = Depends(get_ai_api)
):
    pass

@router.delete("/stop")
async def stop_polling(
    tg_id: int,
    service: str
):
    pass
