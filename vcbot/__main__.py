
import asyncio
import traceback
import logging
import random
from telethon import events
from telethon import Button
from telethon.tl.types import InputWebDocument
from vcbot import *
from vcbot.config import Config as VAR
from time import perf_counter
from vcbot.youtube import download, search, playlist
from telethon.tl.custom import InlineBuilder as Builder


logging.basicConfig(level=logging.info)

class Queue:
    def __init__(self, ):
        self.data = ["https://music.youtube.com/watch?v=KjBYB_zFYUc&list=RDAMVMKjBYB_zFYUc"]
 
    def get(self):
        if self.data:
            return self.data.pop(0)
        else:
            return
 
    def add(self, data):
        self.data.append(data)
        return len(self.data)
    
    def any(self):
        if self.data:
            any_ = random.choice(self.data)
            _ = self.data.index(any_)
            return self.data.pop(_)

        else:
            return


generator = Queue()
 

factory = GroupCallFactory(user, GroupCallFactory.MTPROTO_CLIENT_TYPE.TELETHON)

class Factory:
    def __init__(self) -> None:
        self.groupcall = factory.get_group_call()
        

    async def stop(self):
        await self.groupcall.stop()

    @property 
    def is_connected(self):
        if self.groupcall.is_connected:
            return True
        return False

    async def start(self, id):
        await self.groupcall.start(id)

    async def start_video(self, input_):
        if self.is_connected:
            await self.groupcall.start_video(input_ ,repeat=False)
        



groupcall = Factory()


def admin(func):
    async def runner(event, *args, **kwargs):
        if hasattr(event, 'data'):
            sender = await event.get_sender()
            if sender.id in VAR.ADMINS:
                return await func(event, *args, **kwargs)
            else:
                pass
        else:
            return await func(event, *args, **kwargs)
    return runner


@bot.on(events.NewMessage(from_users=VAR.ADMINS, pattern="/start"))
async def start(event):
    await groupcall.start(event.chat_id)
    await event.respond("started",
    buttons = [
        [Button.inline("Next"), Button.inline("Any")],
        [Button.inline("Stop")]
        ]
    )
 
@bot.on(events.NewMessage(from_users=VAR.ADMINS, pattern="/iiii"))
async def uptime(e):
    await e.respond(f"Uptime: {perf_counter()/1e-9}")

@bot.on(events.CallbackQuery(pattern="Stop"))
@bot.on(events.NewMessage(from_users=VAR.ADMINS, pattern="/stop"))
@admin
async def stop(event):
    await groupcall.stop()
    if not hasattr(event, 'data'):
        await event.respond("stopped")
    else:
        await event.edit("stopped")
 
 
@bot.on(events.CallbackQuery(pattern="Next|Any"))
@bot.on(events.NewMessage(from_users=VAR.ADMINS, pattern="/next|/any"))
@admin
async def switch(event):
    await groupcall.stop()
    await groupcall.start(event.chat_id)
    
    temp = await event.respond("Starting...")
    url = False
    if hasattr(event, 'raw_text'):
        if event.raw_text == '/any':
            url= generator.any()
        if event.raw_text == '/next':
            url= generator.get()

    if hasattr(event, 'data'):
        await temp.delete()
        temp = await event.edit("Starting..")
        if event.data == b"Any":
            url= generator.get()
        if event.data == b"Next":
            url = generator.any()
    if url:
        try:
            text = await download(url)
        except TypeError as e:
            await temp.edit(f"Failed: {e}")
            return
        except Exception:
            await temp.edit(traceback.format_exc())
            return

        await temp.edit("starting video+audio...")
        
        if not text:
            await temp.edit("can't decode")
            return
        else:
            await groupcall.start_video(text[0])
            await temp.edit(f"**Currently Playing**: [{text[1]}]({url})",
            buttons= [
                [Button.inline("Next"), Button.inline("Any")],
                [Button.inline("Stop")]
            ]
            )
    else:
        await temp.edit("Empty queue")
 
@bot.on(events.CallbackQuery(pattern="/play (.+)"))
@bot.on(events.NewMessage(from_users=VAR.ADMINS, pattern="/play (.+)"))
@admin
async def play(event):
    if hasattr(event, 'data'):
        url= event.pattern_match.group(1)
        url = "https://www.youtube.com/watch?v=" + url.decode('utf-8')
        
    else:
        url= event.pattern_match.group(1)
    await groupcall.stop()
    await groupcall.start(event.chat_id)
    temp = await event.respond("Starting...")
    if url:
        try:
            text = await download(url)
        except TypeError as e:
            await temp.edit(f"Failed: {e}")
            return
        except Exception:
            await temp.edit(traceback.format_exc())
            return

        await temp.edit("starting video+audio...")
        
        if not text:
            await temp.edit("can't decode")
            return
        else:
            await groupcall.start_video(text[0])
            await temp.edit(f"**Currently Playing**: [{text[1]}]({url})",
            buttons= [
                [Button.inline("Next"), Button.inline("Any")],
                [Button.inline("Stop")]
            ]
            )
    else:
        await temp.edit("Empty queue")
 

@bot.on(events.NewMessage(from_users=VAR.ADMINS, pattern="/add (.+)"))
async def add_q(event):
    total = generator.add(event.pattern_match.group(1))
    await event.reply(f"Added: Total: {total}")

@bot.on(events.InlineQuery(users=VAR.ADMINS))
async def search_yt(event):
    builder = Builder(bot)
    result_ = await search(event.text)
    if not result_:
        return
    result = []

    for i in result_:
        if i['duration']:
            if i['duration'].count(':') > 2:
                continue
        
        x = builder.article(
            title=i['title'],
            description=i['descriptionSnippet'][0]['text'] if i['descriptionSnippet'] else i['title'],
            text='/add '+ i['link'],
            thumb=InputWebDocument(i['thumbnails'][0]['url'], 0, mime_type='image/jpeg', attributes=[]),
            buttons=Button.inline('Play Now', '/play ' + i['id']),
            # link_preview=False
            )
        result.append(x)
    if result:
        await event.answer(result)
    else:
        return

@bot.on(events.NewMessage(from_users=VAR.ADMINS, pattern="/addlist (.+)"))
async def add_lst(event):
    url =  event.pattern_match.group(1)
    if not url:
        return
    result = await playlist(url)
    if not result:
        return
    total = 0
    for i in result:
        total = generator.add(i)
    await event.reply(f"Added: Total: {total}")
user.run_until_disconnected()