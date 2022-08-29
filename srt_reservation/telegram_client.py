import telegram

class TelegramClient(object):
    def __init__(self, token: str, chat_id: int) -> None: 
        self.bot = telegram.Bot(token = token)
        self.chat_id = chat_id
    
    def send_message(self, message: str):
        self.bot.sendMessage(chat_id = self.chat_id, text=message)
