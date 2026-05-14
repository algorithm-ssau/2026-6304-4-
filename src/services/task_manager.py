import asyncio
from typing import Dict

from models.user import User
from schemas.worker import WorkerState
from workers.funpay_worker import FunpayWorker


class TaskManager:
    def __init__(self):
        self._workers: Dict[int, WorkerState] = {}
        self._lock = asyncio.Lock()

    async def start_worker(self, user: User):

        async with self._lock:
            user_id = user.tg_id

            if user_id in self._workers:
                return

            worker = FunpayWorker(user)

            task = asyncio.create_task(
                worker.run(),
                name=f"funpay-worker-{user_id}"
            )

            self._workers[user_id] = WorkerState(
                account_id=user_id,
                task=task,
                worker=worker
            )

    async def stop_worker(self, account_id: int):

        async with self._lock:

            state = self._workers.get(account_id)

            if not state:
                return

            await state.worker.stop()

            state.task.cancel()

            try:
                await state.task
            except asyncio.CancelledError:
                pass

            del self._workers[account_id]

    async def restart_worker(self, account_id: int):

        await self.stop_worker(account_id)
        await self.start_worker(account_id)

    async def stop_all(self):

        ids = list(self._workers.keys())

        await asyncio.gather(
            *(self.stop_worker(i) for i in ids)
        )

    def is_running(self, account_id: int) -> bool:
        return account_id in self._workers