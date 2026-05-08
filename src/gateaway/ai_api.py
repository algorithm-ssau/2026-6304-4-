from abc import abstractmethod
from dataclasses import dataclass

from repositories.messages import MessagesRepository

@dataclass
class AiApi:

    url: str
    model: str

    messages_repo: MessagesRepository

    SYSTEM_PROMPT = ""

    @abstractmethod
    def send_message(self, user_id, msg):
        pass

@dataclass
class OllamaApi(AiApi):
    def send_message(self, user_id, msg):
        messages = [{"role": "system", "content": self.SYSTEM_PROMPT}]
        user_messages = self.messages_repo.get_message_history(user_id)
        
