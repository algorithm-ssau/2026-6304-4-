# # from fastapi import FastAPI


# # _tasks: dict[int, object]


# # app = FastAPI()

# from FunPayAPI import Account, Runner, types, enums
# from FunPayAPI.updater.events import ChatsListChangedEvent, InitialChatEvent, NewMessageEvent


# TOKEN = "704hdplq7cejk8c9dvr6hkgk7mw5lmlh"

# # Создаем класс аккаунта и сразу же получаем данные аккаунта.
# acc = Account(TOKEN).get()

# # Создаем класс "прослушивателя" событий.
# runner = Runner(acc)

# print("Initialized")

# k = 0

# # "Слушаем" события
# for event in runner.listen(requests_delay=6):
#     if event.type is enums.EventTypes.NEW_MESSAGE:
#         msg = event.message
#         if msg.author_id == acc.id:
#             continue
#         print("ПОЛУЧЕНО СООБЩЕНИЕ")
#         print(f"user: {event.message.id} from {event.message.chat_id} sent: {event.message.text}")
#         resp = ""
#         if k == 0:
#             resp = f"""Здравствуйте! 😊
# В наличии есть лот на 500 робуксов, всё проходит быстро и безопасно. Готов оформить для вас прямо сейчас — будете брать?
#             """
#         if k == 1:
#             resp = f"""Понимаю предложение, но я работаю только с продажей робуксов за оплату 😊
# Обмены, к сожалению, не рассматриваю.

# Могу прямо сейчас оформить для вас лот на 500 робуксов — всё быстро и без лишних сложностей. Будете брать?"""
#         if resp != "":
#             acc.send_message(msg.chat_id, resp)
#         k += 1