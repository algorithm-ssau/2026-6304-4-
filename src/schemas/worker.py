import asyncio
from pydantic import BaseModel

from workers.funpay_worker import FunpayWorker

class WorkerState(BaseModel):
    account_id: int
    task: asyncio.Task
    worker: FunpayWorker

    model_config = {
        "arbitrary_types_allowed": True
    }
