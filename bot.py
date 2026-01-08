import plugins.monkey_patch
import sys
import glob
import importlib
from pathlib import Path
from pyrogram import Client, idle, __version__
from pyrogram.raw.all import layer
import time
from pyrogram.errors import FloodWait
import asyncio
from datetime import date, datetime
import pytz
from aiohttp import web
from database.ia_filterdb import Media, Media2
from database.users_chats_db import db
from info import *
from utils import temp
from Script import script
from plugins import web_server, check_expired_premium, keep_alive
from dreamxbotz.Bot import dreamxbotz
from dreamxbotz.util.keepalive import ping_server
from dreamxbotz.Bot.clients import initialize_clients
from PIL import Image
Image.MAX_IMAGE_PIXELS = 500_000_000

import logging
import logging.config

# Logging Setup
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("pymongo").setLevel(logging.WARNING)

botStartTime = time.time()
ppath = "plugins/*.py"
files = glob.glob(ppath)

async def dreamxbotz_start():
    print('\n\nInitalizing DreamxBotz...')
    
    # 1. Start Bot Client
    await dreamxbotz.start()
    
    # 2. Setup Bot Info
    me = await dreamxbotz.get_me()
    temp.ME = me.id
    temp.U_NAME = me.username
    temp.B_NAME = me.first_name
    temp.B_LINK = me.mention
    dreamxbotz.username = '@' + me.username
    
    # 3. Initialize Multi-Clients (For Streaming/Cloning)
    await initialize_clients()
    
    # 4. Load Plugins
    for name in files:
        with open(name) as a:
            patt = Path(a.name)
            plugin_name = patt.stem
            import_path = f"plugins.{plugin_name}"
            importlib.import_module(import_path)
            print(f"DreamxBotz Imported => {plugin_name}")

    # 5. Database & Background Tasks
    if ON_HEROKU:
        asyncio.create_task(ping_server()) 
    
    b_users, b_chats = await db.get_banned()
    temp.BANNED_USERS = b_users
    temp.BANNED_CHATS = b_chats
    await Media.ensure_indexes()
    
    if MULTIPLE_DB:
        await Media2.ensure_indexes()
        print("Multiple Database Mode On.")
    
    # Start Premium Expiry Task
    asyncio.create_task(check_expired_premium(dreamxbotz))
    
    logging.info(f"{me.first_name} (v{__version__}) started on {me.username}.")
    
    # 6. Web Server for Streaming (Render Fix)
    app = web.AppRunner(await web_server())
    await app.setup()
    bind_address = "0.0.0.0"
    # Port variable info.py se aayega
    await web.TCPSite(app, bind_address, PORT).start()
    print(f"Web Server started on port {PORT}")

    # 7. Keep Alive & Idle
    asyncio.create_task(keep_alive())
    
    # Send Restart Message
    tz = pytz.timezone('Asia/Kolkata')
    now = datetime.now(tz)
    time_str = now.strftime("%H:%M:%S %p")
    await dreamxbotz.send_message(chat_id=LOG_CHANNEL, text=script.RESTART_TXT.format(temp.B_LINK, date.today(), time_str))
    
    await idle()

if __name__ == '__main__':
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(dreamxbotz_start())
    except KeyboardInterrupt:
        logging.info('Service Stopped Bye 👋')
    except FloodWait as e:
        time.sleep(e.value)
    except Exception as e:
        logging.error(f"Fatal Error: {e}")
