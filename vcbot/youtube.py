import asyncio
import logging
try:
    from vcbot.asynccmd import cmd
except ImportError:
    from asynccmd import cmd
from pytube import YouTube
from youtubesearchpython.__future__ import VideosSearch, Playlist
import re, glob
from pprint import pp
from youtube_dl import YoutubeDL
async def cmd_dl(yt, url):
    url_ = yt.video_id
    url = "https://www.youtube.com/watch?v=" + url_
    x = await cmd(f'youtube-dl -f "bestvideo[height<=480]+bestaudio" "{url}" -o "{url_}.%(ext)s" --no-continue')
    if not x:
        return
    return glob.glob(url_+"*")[0]

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
    yt = YoutubeDL({"format": "bestvideo[height<=480]+bestaudio[ext=m4a]"})
    x = yt.extract_info(yt_.watch_url, download=False)
    rtype = x['requested_formats']
    return rtype[0]['url'], rtype[1]['url'], yt_.title
    
    

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
