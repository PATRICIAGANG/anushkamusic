import asyncio
import logging
try:
    from vcbot.asynccmd import cmd
except ImportError:
    from asynccmd import cmd
from pytube import YouTube
from youtubesearchpython.__future__ import VideosSearch, Playlist
import re, glob
# from pprint import pp
from youtube_dl import YoutubeDL
from youtube_dl.utils import ExtractorError


async def cmd_dl(yt, url):
    url_ = yt.video_id
    url = "https://www.youtube.com/watch?v=" + url_
    logging.info("starting yt-dl")
    x = await asyncio.wait_for(cmd(f'youtube-dl -f "best[height<=480]" "{url}" -o "./downloads/{url_}.%(ext)s" --no-continue'), timeout=30) #
    if not x:
        return
    logging.info("stopped yt-dl")
    return glob.glob('./downloads/'+ url_+"*")[0]

async def download(url):
    if not url:
        return
    yt = YouTube(url)
    return await cmd_dl(yt, url), yt.title

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
    
async def fetch_stream(url: str):
    params = {"verbose": True, "format": "best[height>?480]/best", "noplaylist": True, "nocontinue": True}
    yt = YoutubeDL(params)# [ext=m4a]
    try:
        info = yt.extract_info(url, download=False)
        info["display_id"]
        return info['url'], info['title'], None
    except ExtractorError:
        return None, None, "ExtractorError: Invalid url"
    except (KeyError, Exception):
        try:
            yt = YouTube(url)
            command = f'youtube-dl -f "best[height>?480]/best" "{url}" -o "./downloads/{yt.video_id}.%(ext)s" --no-continue --no-playlist --verbose'
            await asyncio.wait_for(cmd(command), timeout=30)
            path = glob.glob('./downloads/'+ yt.video_id +"*")
            return path[0] if path else None, yt.title, None
        except asyncio.TimeoutError:
            return None, None, "TimeoutError: Can't wait too long for download"
        except Exception as e:
            return None, None, str(e)


        


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
