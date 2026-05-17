from abc import ABC, abstractmethod
from dataclasses import dataclass
import httpx
import logging

from repositories.messages import MessagesRepository

logger = logging.getLogger(__name__)

@dataclass
class AiApi(ABC):

    url: str
    model: str

    messages_repo: MessagesRepository

    SYSTEM_PROMPT = "Ты помощник для общения с клиентами на торговой площадке FunPay. Отвечай вежливо и профессионально."

    @abstractmethod
    async def send_message(self, user_id: int, msg: str) -> str:
        pass

@dataclass
class OllamaApi(AiApi):
    async def send_message(self, user_id: int, msg: str) -> str:
        try:
            messages = [{"role": "system", "content": self.SYSTEM_PROMPT}]

            # Получаем историю сообщений пользователя
            user_messages = await self.messages_repo.get_message_history(user_id)
            messages.extend(user_messages)

            # Добавляем новое сообщение
            messages.append({"role": "user", "content": msg})

            # Отправляем запрос к Ollama API
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.url}/api/chat",
                    json={
                        "model": self.model,
                        "messages": messages,
                        "stream": False
                    }
                )
                response.raise_for_status()

                result = response.json()
                ai_response = result.get("message", {}).get("content", "")

                # Сохраняем сообщения в историю
                await self.messages_repo.save_message(user_id, msg, "user")
                await self.messages_repo.save_message(user_id, ai_response, "assistant")

                return ai_response

        except Exception as e:
            logger.exception(f"Error sending message to AI for user {user_id}")
            return "Извините, произошла ошибка при обработке вашего сообщения."
