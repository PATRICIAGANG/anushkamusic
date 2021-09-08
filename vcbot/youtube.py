import asyncio
import logging
import secrets
try:
    from vcbot.asynccmd import cmd, ErrorInAsyncCmd
except ImportError:
    from asynccmd import cmd, ErrorInAsyncCmd
from pytube import YouTube
from youtubesearchpython.__future__ import VideosSearch, Playlist
import re, glob
# from pprint import pp
from youtube_dl import YoutubeDL
from youtube_dl.utils import ExtractorError
from asyncio import AbstractEventLoop



async def download_cmd_ytdl(url: str, format: str):
    try:
        id_ = secrets.token_hex(20)
        try:
            title = await cmd(f'youtube-dl -e "{url}"')
        except ErrorInAsyncCmd:
            title = "unknown"
        command = f'youtube-dl -f "{format}" "{url}" -o "./downloads/{id_}.%(ext)s" --no-continue --no-playlist --verbose'
        await asyncio.wait_for(cmd(command), timeout=30)
        path = glob.glob(f'./downloads/{id_}*')
        return path[0] if path else None, title, None

    except asyncio.TimeoutError:
            return None, None, "TimeoutError: Can't wait too long for download"
    except ErrorInAsyncCmd as e:
        return None, None, str(e)
    except Exception as e:
        return None, None, str(e)

async def download_ytdl(url: str, format: str = "best", loop: AbstractEventLoop = asyncio.get_event_loop()):
    id_ = secrets.token_hex(20)
    params= {"verbose": True, "format": format, "noplaylist": True, "continue_dl": False, 'outtmpl': "hello.%(ext)s"}
    yt = YoutubeDL(params)
    try:
        info = await loop.run_in_executor(None, lambda : yt.extract_info(url))
        return f"./downloads/{id_}.{info['ext']}", info['title'], None
    except ExtractorError as e:
        return None, None, str(e)
    except Exception as e:
        return None, None, str(e)
    
    
async def fetch_ytdl(url: str, format: str = "best", loop: AbstractEventLoop = asyncio.get_event_loop()):
    params= {"verbose": True, "format": format, "noplaylist": True, "continue_dl": False}
    try:
        yt = YoutubeDL(params)
        info = await loop.run_in_executor(None, lambda : yt.extract_info(url, download=False))
        # info["display_id"]
        return info['url'], info['title'], None
    except ExtractorError:
        return None, None, "ExtractorError: Invalid url"
    except Exception as e:
        return None, None, str(e)

    


    

async def redio_v(url: str):
    """
    video, audio, title
    
    """
    yt_ = YouTube(url)
    # yt = YoutubeDL({"format": "bestaudio"})
    yt = YoutubeDL({"format": "best[height<=480]"})# [ext=m4a]
    x = yt.extract_info(yt_.watch_url, download=False)
    rtype = x['requested_formats']
    return rtype[0]['url'], rtype[1]['url'], yt_.title
    
async def fetch_stream(url: str, only_audio=False):
    params = {"verbose": True, "format": "", "noplaylist": True, "nocontinue": True}
    if not only_audio:
        # params['format'] = "best[height>=?480]/best"
        # params['format'] = "best[height<=?480]/best"
        # params['format'] = "best[height=?720]/best"
        params['format'] = "best[height=?720]/best[height=?480]/best"
        # params['format'] = "best"
    else:
        params['format'] = "bestaudio"

    return await fetch_ytdl(url, params['format'])
            
            
            
        


        


async def search(query: str):
    result = VideosSearch(query, limit=20)
    result = (await result.next())
    
    if result:
        for i in result['result']:
            yield i
    return
async def playlist(url: str):
    result = await Playlist.getVideos(url)
    if result:
        if not result['videos']:
            return
        return [i['link'] for i in result['videos']]

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    # asyncio.run(download("https://music.youtube.com/watch?v=KjBYB_zFYUc&list=RDAMVMKjBYB_zFYUc"))
    # asyncio.run(search("kishore kumar"))
    x = asyncio.run(redio_v("https://www.youtube.com/watch?v=b4KdawFO6o8"))
    print(x)
