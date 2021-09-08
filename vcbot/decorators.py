import traceback
import asyncio
from config import Config as VAR
def admin(func):
    async def runner(event, *args, **kargs):
        if hasattr(event, 'data'):
            try:

                sender = await event.get_sender()
                if sender.id in VAR.ADMINS:
                    return await func(event, *args, **kargs)
                else:
                    pass
            except (ValueError, TypeError):
                await event.answer("NoneType: Retry")
        else:
            return await func(event, *args, **kargs)
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
