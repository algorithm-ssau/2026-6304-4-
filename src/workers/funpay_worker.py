import asyncio
import threading
import logging

from FunPayAPI import Account, Runner
import FunPayAPI
from FunPayAPI.common.enums import EventTypes

from database.database import get_session_direct
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
        try:
            if event.type == EventTypes.NEW_MESSAGE and isinstance(event, FunPayAPI.events.NewMessageEvent):
                await self._handle_new_message(event)
            elif event.type == EventTypes.NEW_ORDER and isinstance(event, FunPayAPI.events.NewOrderEvent):
                await self._handle_new_order(event)
        except Exception:
            logger.exception("Error handling event")

    async def _handle_new_message(self, event: FunPayAPI.events.NewMessageEvent):
        """Обрабатывает новое сообщение: отправляет в AI и получает ответ"""
        from dependency import get_ai_api

        message = event.message
        chat_id = message.chat_id
        message_text = message.text or ""

        logger.info(
            f"New message from chat {chat_id}",
            extra={"account_id": self.account_id, "message": message_text}
        )

        try:
            async with get_session_direct() as session:
                ai_service = get_ai_api(session)

                # Отправляем сообщение в AI и получаем ответ
                ai_response = await ai_service.send_message(self.account_id, message_text)

                # Отправляем ответ обратно в FunPay
                if ai_response and self.client:
                    self.client.send_message(chat_id, ai_response)
                    logger.info(
                        f"Sent AI response to chat {chat_id}",
                        extra={"account_id": self.account_id}
                    )
        except Exception:
            logger.exception(f"Error processing message for account {self.account_id}")

    async def _handle_new_order(self, event: FunPayAPI.events.NewOrderEvent):
        """Обрабатывает новый заказ: отправляет уведомление в Telegram"""
        order = event.order
        order_id = order.id

        logger.info(
            f"New order {order_id}",
            extra={"account_id": self.account_id, "order_id": order_id}
        )

        try:
            from runtime import chat_bot

            if chat_bot:
                await chat_bot.send_order_notification(
                    tg_id=self.account_id,
                    order_id=order_id
                )
                logger.info(
                    f"Sent order notification to Telegram user {self.account_id}",
                    extra={"order_id": order_id}
                )
        except Exception:
            logger.exception(f"Error sending order notification for account {self.account_id}")

