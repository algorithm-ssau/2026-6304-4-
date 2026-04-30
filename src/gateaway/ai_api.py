from abc import abstractmethod
from dataclasses import dataclass

@dataclass
class AiApi:

    url: str
    model: str

    SYSTEM_PROMPT = ""

    @abstractmethod
    def send_message(self, user_id, msg):
        pass

@dataclass
class OllamaApi(AiApi):
    def send_message(self, user_id, msg):
        