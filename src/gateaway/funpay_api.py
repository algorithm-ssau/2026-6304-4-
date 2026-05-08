from dataclasses import dataclass
from FunPayAPI import Account, Runner, types, enums

@dataclass
class FunPayApiGateaway:
   golden_token: str
   username: str

   _account: Account | None = None
   _runner: Runner | None = None

   @property
   def account(self):
      if not self._account:
         self._account = Account(self.golden_token).get()
      return self._account

   @property
   def runner(self):
      if not self._runner:
         acc = self.account
         self._runner = Runner(acc)
      
      return self._runner

   async def send_message(self, chat_id, text):
      acc = self.account
      acc.send_message(chat_id, text)

   def get_listener(self):
      runner = self.runner
      return runner.listen(requests_delay=4)
