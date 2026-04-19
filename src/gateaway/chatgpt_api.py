from dataclasses import dataclass

@dataclass
class ChatgptApi:
    def _init(self): pass

    def __init__(self, api_key):
        self.api_key = api_key

    def send_message(self, message):
        # ...
        response = f"Echo: {message}"
        return response