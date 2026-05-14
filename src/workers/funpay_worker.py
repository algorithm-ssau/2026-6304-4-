import asyncio
import threading
import logging

from FunPayAPI import Account, Runner
import FunPayAPI
from FunPayAPI.common.enums import EventTypes

from database.database import get_session_direct
from dependency import get_ai_api
from models.user import User

logger = logging.getLogger(__name__)

class FunpayWorker:
    def __init__(self, user: User):

        self.account_id = user.tg_id
        self.token = user.golden_token

        if self.token == None:
            raise Exception("Token not found in user")

        self.loop = None
        self.client = None
        self._running = False
        self._queue = asyncio.Queue()
        self._thread = None
        self.delay = 4


    async def run(self):
        self._running = True
        
        if self.token == None:
            raise Exception("Token not found in user")
        self.client = Account(self.token).get()
        self.runner = Runner(self.client)
        
        self.loop = asyncio.get_running_loop()
        self._thread = threading.Thread(
            target=self._polling_thread,
            daemon=True
        )
        self._thread.start()
        try:
            while self._running:
                await asyncio.sleep(self.delay)
                try:
                    event = await self._queue.get()
                    await self._handle_event(event)
                except (asyncio.TimeoutError, asyncio.CancelledError):
                    continue
                except Exception:
                    logger.exception("Handle event error")
        finally:
            await self._shutdown()

    async def stop(self):
        self._running = False

    async def _shutdown(self):

        logger.info(
            "Worker stopped",
            extra={"account_id": self.account_id}
        )

    def _polling_thread(self):

        """
        Sync polling inside separate thread.
        """
        try:
            for event in self.runner.listen(requests_delay=self.delay):

                if not self._running:
                    break
                asyncio.run_coroutine_threadsafe(
                    self._queue.put(event),
                    loop=self.loop
                )
        except Exception:
            logger.exception(
                "Polling thread crashed"
            )

    async def _handle_event(self, event: FunPayAPI.events.BaseEvent):
        print(event.__dict__)
        if event.type == EventTypes.NEW_MESSAGE and isinstance(event, FunPayAPI.events.NewMessageEvent):
            print(f"user {self.account_id} got message: {event.message}")
            # self.client.get_chat_history(event.)
            # event.stack.
            async with get_session_direct() as session:
                service = get_ai_api(session)
                service.send_message(self.account_id, event.message)

