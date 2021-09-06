import logging
logging.getLogger('telethon').setLevel(logging.WARNING)
# logging.getLogger('pytgcalls').setLevel(logging.)
from telethon import TelegramClient
from telethon.sessions import StringSession
from .config import Config as VAR
from datetime import datetime

logging.basicConfig(level=logging.DEBUG, format='[%(funcName)s]:%(levelname)s: %(message)s', filename="app.log")

user = TelegramClient(StringSession(VAR.STRING), VAR.API_ID, VAR.API_HASH).start()
bot = TelegramClient("bot_sess", VAR.API_ID, VAR.API_HASH).start(bot_token=VAR.BOT_TOKEN)

INIT_TIME = datetime.now()