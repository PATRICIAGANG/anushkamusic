import asyncio
import logging

async def cmd(cmd):
    logging.debug([cmd])
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    stderr, stdout = await proc.communicate()
    logging.debug(f'[{cmd!r} exited with {proc.returncode}]')
    
    if proc.returncode == 0:
        logging.info(f'[stdout]\n{stdout.decode()}')
        return stdout.decode() 

    if stdout:
        logging.info(f'[stdout]\n{stdout.decode()}')
        return stdout.decode()
    if stderr:
        logging.error(f'[stderr]\n{stderr.decode()}')
        return False
