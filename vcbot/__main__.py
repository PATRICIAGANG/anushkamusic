
import asyncio

import traceback
import logging
import random

from vcbot.util import clear
from telethon import events
from telethon import Button
from telethon.tl.types import InputWebDocument
from vcbot import *
from vcbot.config import Config as VAR
from vcbot.youtube import fetch_stream , search, playlist #redio_v, download
from telethon.tl.custom import InlineBuilder as Builder
from pytube import YouTube
from pytgcalls import GroupCallFactory

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
        self.groupcall = None

        

    async def stop(self):
        logging.debug("Requested stop")
        if self.groupcall:
            await self.groupcall.stop()
            logging.debug(f"Stopped groupcall")
            self.groupcall = None
            return
        
    @property
    def is_connected(self):
        if not self.groupcall:
            return False
        if self.groupcall.is_connected:
            return True

        return False

    async def start(self, id):
        logging.debug("Requested Start")
        if not self.groupcall:
            self.groupcall = factory.get_group_call()
            # self.first_time = False
        if self.groupcall:
            if self.groupcall.is_connected:
                await self.groupcall.stop()  
        await self.groupcall.start(id)
        logging.debug("stop groupcall")

    async def start_video(self, source: str, with_audio=True, repeat=False, enable_experimental_lip_sync=False):
        if self.groupcall:
            # await self.start(id)
            logging.debug('started video')
            await self.groupcall.start_video(source , with_audio, repeat, enable_experimental_lip_sync)

    async def start_audio(self, source: str, repeat=True):
        logging.debug("start audio")
        if not self.groupcall:
            return
        await self.groupcall.start_audio(source, repeat)
        

    async def play_pause(self, play=False):
        if not self.groupcall:
            return
        if self.is_connected:
            if play:
                self.groupcall.resume_playout()
            else:
                self.groupcall.pause_playout()
    
    async def restart(self):
        if not self.groupcall:
            return
        if self.is_connected:
            self.groupcall.restart_playout()



groupcall = Factory()


def admin(func):
    async def runner(event):
        if hasattr(event, 'data'):
            try:

                sender = await event.get_sender()
                if sender.id in VAR.ADMINS:
                    return await func(event)
                else:
                    pass
            except (ValueError, TypeError):
                await event.answer("NoneType: Retry")
        else:
            return await func(event)
    return runner

def notimeout(func):
    async def runner(event, *args, **kwargs):
        try:
            return await func(event, *args, **kwargs)
        except asyncio.TimeoutError:
            return await event.respond("**TimeoutError**: failed to connect")
        except Exception:
            return await event.respond(traceback.format_exc())
    return runner
        
@bot.on(events.NewMessage(from_users=VAR.ADMINS, pattern="/uptime"))
async def uptime(event):
    td = datetime.now() - INIT_TIME
    seconds = td.seconds
    days = td.days
    hours = (seconds//3600)%60
    minutes = (seconds//60)%60
    seconds = seconds % 60
    await event.respond(f"days: {days}, hours: {hours}, minutes: {minutes}, seconds: {seconds}")
    

@bot.on(events.NewMessage(from_users=VAR.ADMINS, pattern='/isconn'))
async def isconn(e):
    await e.respond(file='app.log')
    if groupcall.is_connected:
        await e.reply("yes")
    else:
        await e.reply("No")

# @bot.on(events.NewMessage(from_users=VAR.ADMINS, pattern='isconn'))
# async def gitpull(e):
#     txt = os.popen("git pull").read()
#     await e.respond(txt)
 
@bot.on(events.CallbackQuery(pattern="Next|Any"))
@bot.on(events.NewMessage(from_users=VAR.ADMINS, pattern="/next|/any"))
@admin
# @stopifstarted
async def switch(event):
    
    # await groupcall.groupcall.pause_playout()   
    # group_call = factory.get_group_call()
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
        yt = YouTube(url)
        await temp.edit(f"**Name**: [{yt.title}]({yt.watch_url})",
            buttons = [
                [Button.inline("Play", '/play ' + yt.video_id)],
                [Button.inline("Next"), Button.inline("Any")],
                [Button.inline("Resume")],
                [Button.inline("Pause")],
                # [Button.inline("Restart")],
                [Button.inline("Stop")]
            ]
            )
    else:
        await temp.edit("Empty queue")
 

@admin
async def play(event, only_audio: bool =False, beta: bool=False):

    temp = await event.respond("Starting...")
    if hasattr(event, 'data'):
        await temp.delete()
        temp = await event.edit("starting...")
        if isinstance(temp, bool):
            temp = await event.respond("starting...")
        url= event.pattern_match.group(1)
        url = "https://www.youtube.com/watch?v=" + url.decode('utf-8')
        
    else:
        url= event.pattern_match.group(1)
    # await groupcall.stop()

    try:
        # await groupcall.stop()
        await groupcall.start(event.chat_id)
    except asyncio.TimeoutError:
        await temp.edit("**Error**: Failed to connect voice call")
        return

    # if os.path.exists(f"./downloads/{message.file.name}"):
    # await cmd(f"rm './downloads/*'")
    clear()
    if url:
        # audio = True
        video_audio, title, Error = await fetch_stream(url, only_audio)
        if Error:
            await temp.edit(Error)
            return
        if not video_audio:
            await event.respond("**Error**:  Can't fetch data")
            return

        await temp.edit("starting video+audio...")
        if not video_audio:
            await temp.edit("can't decode")
            return
        else:
            try:
                # await groupcall.start_audio(audio)
                # await groupcall.start_video(video, with_audio=False)
                if not only_audio:
                    await groupcall.start_video(video_audio, enable_experimental_lip_sync=beta)
                else:
                    await groupcall.start_audio(video_audio)
            except RuntimeError as e:
                await temp.edit(f"{e}")
                return

            await temp.edit(f"**Currently Playing**: [{title}]({url})",
            buttons = [
                [Button.inline("Next"), Button.inline("Any")],
                [Button.inline("Resume")],
                [Button.inline("Pause")],
                # [Button.inline("Restart")],
                [Button.inline("Stop")]
            ]
            )
    else:
        await temp.edit("Empty queue")
 
@bot.on(events.CallbackQuery(pattern="/play (.+)"))
@bot.on(events.NewMessage(from_users=VAR.ADMINS, pattern=".play (.+)"))
async def play_video(event):
    await play(event)

@bot.on(events.CallbackQuery(pattern="/aplay (.+)"))
@bot.on(events.NewMessage(from_users=VAR.ADMINS, pattern=".aplay (.+)"))
async def play_audio(event):
    await play(event, only_audio=True)

@bot.on(events.CallbackQuery(pattern="/bplay (.+)"))
@bot.on(events.NewMessage(from_users=VAR.ADMINS, pattern="/bplay (.+)"))
async def play_beta(event):
    await play(event, beta=True)

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
        if not i['duration']:
            # if i['duration'].count(':') > 2:
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
    try:

        result = await playlist(url)
    except Exception:
        await event.reply("Failed to fetch url")
        return
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
        # [Button.inline("Restart")],
        [Button.inline("Stop")]
        ]
    if hasattr(event, 'data'):
        case = event.data.decode('utf-8').lower()
        # temp = await event.edit("...")
    else:
        case = event.raw_text.lower()[1:]
        temp = await event.respond("...")
    if case == 'start|join':
        await groupcall.start()
        case = case + 'ed'
    elif case == 'stop':
        if groupcall.is_connected:
            await groupcall.stop()
        case = case + 'ped'

    elif case == 'resume':
        await groupcall.play_pause(True)
        case = case + 'd'
    elif case == 'pause':
        await groupcall.play_pause()
        case = case + 'd'
    elif case == 'replay':
        await groupcall.restart()
        case = case + 'ed'
    if hasattr(event, 'data'):
        await event.answer(f"Successfully {case}ed")
        return

    await temp.edit(f"Successfully {case}",
        buttons=buttons
    
    )

@bot.on(events.NewMessage(from_users=VAR.ADMINS, pattern="^.stream\s?(.+)?"))   
async def stream(event):
    url = None
    if event.is_reply:
        message = await event.get_reply_message()
        url = message.raw_text
    else:
        url = event.pattern_match.group(1)

    if url:
        temp = await event.respond("connecting..")
        try:
            await groupcall.start(event.chat_id)
        except asyncio.TimeoutError:
            await temp.edit("**Error**: Failed to connect voice call")
            return
        await temp.edit("Connected: Starting Video")
        try:
            await groupcall.start_video(url)
        except Exception:
            await temp.edit("Failed to start video")
            return

        await temp.edit(
            "Playing... ",
            buttons = [
                [Button.inline("Next"), Button.inline("Any")],
                [Button.inline("Resume")],
                [Button.inline("Pause")],
                # [Button.inline("Restart")],
                [Button.inline("Stop")]
            ]
        )




    
    
@bot.on(events.NewMessage(from_users=VAR.ADMINS, pattern="^.fstream", func=lambda e: e.is_reply))
async def fstream(event):
    message = await event.get_reply_message()
    if not message.file or not message.video:
        await message.reply("No file detected")
        return
    if message.file.size > 2e+8 :
        await message.reply("File too big")
        return
    # if os.path.exists(f"./downloads/{message.file.name}"):
    #     await cmd(f"rm './downloads/{message.file.name}'")
    # await cmd("rm './downloads/*")
    await groupcall.stop()
    clear()
    async with bot.action(event.chat_id, 'record-video') as action:
        loc = await message.download_media("./downloads", progress_callback=action.progress)

    try:
        await groupcall.start(event.chat_id)
    except asyncio.TimeoutError:
        await event.respond("**Error**: Failed to connect voice call")
        # await cmd(f"rm '{loc}'")
        clear()
        return
    try:
        await groupcall.start_video(loc)
        await message.reply(f"**Playing**: {message.file.name}",
        buttons = [
            [Button.inline("Next"), Button.inline("Any")],
            [Button.inline("Resume")],
            [Button.inline("Pause")],
            # [Button.inline("Restart")],
            [Button.inline("Stop")]
            ]
        )
    except Exception:
        await message.reply(traceback.format_exc())




bot.loop.create_task(bot.send_message(VAR.ADMINS[0], "Restarted"))
user.run_until_disconnected()
