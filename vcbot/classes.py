import logging
import random
from pytgcalls.group_call_factory import GroupCallFactory

class Factory:
    def __init__(self, factory: GroupCallFactory) -> None:
        self.groupcall = None
        self.factory = factory

        

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
        await self.stop()
        if not self.groupcall:
            self.groupcall = self.factory.get_group_call()
            # self.first_time = False
 
        await self.groupcall.start(id)
        logging.debug("stop groupcall")

    async def start_video(self, source: str, with_audio=True, repeat=False, enable_experimental_lip_sync=False):
        if self.groupcall:
            # await self.start(id)
            logging.debug('started video')
            await self.groupcall.start_video(source , with_audio, repeat, enable_experimental_lip_sync)

    async def start_audio(self, source: str, repeat=False):
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
