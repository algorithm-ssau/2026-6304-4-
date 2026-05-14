from fastapi import APIRouter, Depends

# from dependency import get_task_manager
# from gateaway.ai_api import AiApi
from models.user import User
from services.task_manager import TaskManager
from runtime import task_manager


router = APIRouter(prefix="/ai")

@router.post("/chat")
async def chat():
    pass

@router.post("/start")
async def start(
    token: str,
):
    service: TaskManager = task_manager
    user = User()
    user.golden_token = token
    user.tg_id = 0
    user.id = 0
    await service.start_worker(user)

@router.delete("/stop")
async def stop_polling(
    tg_id: int,
):
    service: TaskManager = task_manager
    await service.stop_all()
