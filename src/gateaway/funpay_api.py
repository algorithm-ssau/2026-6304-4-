from dataclasses import dataclass
from FunPayAPI import Account, Runner, types, enums

@dataclass
class FunPayApiGateaway:
   golden_token: str

   _account: Account | None = None

   def get_account(self):
      if not self._account:
         self._account = Account(self.golden_token).get()

      return self._account

   async def send_message(self, text):
      acc = self.get_account()
      # acc.send_message()

   async def l(self):
      acc = self.get_account()