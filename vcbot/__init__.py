import logging
from telethon import TelegramClient
from telethon.sessions import StringSession
from .config import Config as VAR
from pytgcalls import GroupCallFactory
from datetime import datetime

logging.basicConfig(level=logging.INFO)
user = TelegramClient(StringSession(VAR.STRING), VAR.API_ID, VAR.API_HASH).start()
bot = TelegramClient("bot_sess", VAR.API_ID, VAR.API_HASH).start(bot_token=VAR.BOT_TOKEN)

INIT_TIME = datetime.now()