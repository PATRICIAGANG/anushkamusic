# Vcbot which does nothing
**A bot which can play video and audio**

## Configuration  
```bash
git clone https://github.com/animeshxd/vcbot.git
cd vcbot/
# add below configuration

#runwith
python -m vcbot
```
**Modify `vcbot/config.py`**
- ADD **[API_ID, API_HASH](https://my.telegram.org/auth)**
- ADD **[TELETHON SESSION STRING]()**
- ADD **[BOT_TOKEN](https://t.me/BotFather)**
- ADD **ALLOWED USERS** (integer) in ADMINS list
## Commands
 - `.start` - start/join Vc
 - `.join` - start/join Vc
 - `/next` - Get Next Video from List
 - `/any` - Get Any Video From List
 - `/play <youtube_url>` - Play from youtube url
 - `.fstream` - Play from replied video, gif, image
 - `/add <youtube_url>` - Add video in List
 - `/addlist <youtube_playlist>` - Add Playlist video in List
 - `.resume` - Resume paused video
 - `.pause` - Pause running video
 - `.stop` - Stop running video

# Requirements:
- [Python3](https://www.python.org/downloads)
- [requirements.txt](https://github.com/animeshxd/vcbot/blob/master/requirements.txt)
- 2GB RAM VPS (Windows/Linux/Mac)

## Credit ❤
**Lonami** for **[Telethon](https://github.com/LonamiWebs/Telethon)**  
**MarshalX** for **[pytgcalls](https://github.com/MarshalX/tgcalls)** 