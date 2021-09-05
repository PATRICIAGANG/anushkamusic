
import asyncio
from asyncio.locks import Event
import traceback
import logging
import random
from telethon import events
from telethon import Button
from telethon.tl.types import InputWebDocument
from vcbot import *
from vcbot.config import Config as VAR
from time import perf_counter
from vcbot.youtube import download, search, playlist, redio_v
from telethon.tl.custom import InlineBuilder as Builder
from pytgcalls.implementation.group_call import GroupCall


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
        self.is_running = False
        

    async def stop(self):
        await self.groupcall.stop()
        self.is_running = False

    @property 
    def is_connected(self):
        if self.groupcall.is_connected:
            return True
        return False

    async def start(self, id):
        if self.is_connected:
            await self.stop()
        await self.groupcall.start(id)

    async def start_video(self, input_, repeat=False, with_audio=True):
        if self.is_connected:
            await self.groupcall.start_video(input_ ,repeat=repeat, with_audio=with_audio)
            self.is_running = True
    async def start_audio(self, input_, repeat=False):
        if self.is_connected:
            await self.groupcall.start_audio(input_ ,repeat=repeat)
            self.is_running = True
    
    async def play_pause(self, play=False):
        if self.is_connected:
            if play:
                self.groupcall.resume_playout()
            else:
                self.groupcall.pause_playout()
    
    async def restart(self):
        if self.is_connected:
            self.groupcall.restart_playout()






groupcall = Factory()


def admin(func):
    async def runner(event, *args, **kwargs):
        if hasattr(event, 'data'):
            try:

                sender = await event.get_sender()
                if sender.id in VAR.ADMINS:
                    return await func(event, *args, **kwargs)
                else:
                    pass
            except (ValueError, TypeError):
                await event.answer("NoneType: Retry")
        else:
            return await func(event, *args, **kwargs)
    return runner

# def stopifstarted(func):
#     async def runner(event, *args, **kwargs):
#         group_call = factory.get_group_call()
#         if group_call.is_connected:
#             logging.info("Stopped running call")
#             await group_call.stop()
#         return await func(event, *args, **kwargs)
#     return runner

# @bot.on(events.NewMessage(from_users=VAR.ADMINS, pattern="/start"))
# async def start(event):
#     await groupcall.start(event.chat_id)
#     await event.respond("started",
#     buttons = [
#         [Button.inline("Next"), Button.inline("Any")],
#         [Button.inline("Stop")]
#         ]
#     )
 
@bot.on(events.NewMessage(from_users=VAR.ADMINS, pattern="/iiii"))
async def uptime(e):
    await e.respond(f"Uptime: {perf_counter()/1e-9}")


 
 
@bot.on(events.CallbackQuery(pattern="Next|Any"))
@bot.on(events.NewMessage(from_users=VAR.ADMINS, pattern="/next|/any"))
@admin
# @stopifstarted
async def switch(event):
    
    # await groupcall.groupcall.pause_playout()    
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
            video, audio, title = await redio_v(url)
        except TypeError as e:
            await temp.edit(f"Failed: {e}")
            return
        except Exception:
            await temp.edit(traceback.format_exc())
            return

        await temp.edit("starting video+audio...")
        
        if not video or not audio:
            await temp.edit("can't decode")
            return
        else:
            task1 = bot.loop.create_task(groupcall.start_audio(audio))
            task2 = bot.loop.create_task(groupcall.start_video(video, with_audio=False))
            # await task1
            # await task2
            await asyncio.gather(task1, task2)
            await temp.edit(f"**Currently Playing**: [{title}]({url})",
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
    # await groupcall.stop()
    await groupcall.start(event.chat_id)
    temp = await event.respond("Starting...")
    if url:
        try:
            video, audio, title = await redio_v(url)
        except TypeError as e:
            await temp.edit(f"Failed: {e}")
            return
        except Exception:
            await temp.edit(traceback.format_exc())
            return

        await temp.edit("starting video+audio...")
        
        if not video or not audio:
            await temp.edit("can't decode")
            return
        else:
            await groupcall.start_audio(audio)
            await groupcall.start_video(video, with_audio=False)
            await temp.edit(f"**Currently Playing**: [{title}]({url})",
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
    result_ = search(event.text)
    if not result_:
        return
    result = []

    async for i in result_:
        if i['duration']:
            if i['duration'].count(':') > 2:
                continue
        
        x = builder.article(
            title=i['title'],
            description=i['duration'] if i['duration'] else i['title'],
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

@bot.on(events.CallbackQuery(pattern="Start|Join|Resume|Pause|Replay|Stop"))
@bot.on(events.NewMessage(from_users=VAR.ADMINS, pattern=".start|.join|.resume|.pause|.replay|.stop"))
@admin
async def etc(event):
    buttons = [
        [Button.inline("Next"), Button.inline("Any")],
        [Button.inline("Resume")],
        [Button.inline("Pause")],
        [Button.inline("Restart")],
        [Button.inline("Stop")]
        ]
    if hasattr(event, 'data'):
        case = event.data.decode('utf-8').lower()
        temp = await event.edit("...")
    else:
        case = event.raw_text.lower()[1:]
        temp = await event.respond("...")
    if case == 'start|join':
        await groupcall.start()
    elif case == 'stop':
        await groupcall.stop()
    elif case == 'resume':
        await groupcall.play_pause(True)
    elif case == 'pause':
        await groupcall.play_pause()
    elif case == 'replay':
        await groupcall.restart()
    await temp.edit(f"Successfully {case}ed ",
        buttons=buttons
    
    )
    
        
    
    




user.run_until_disconnected()