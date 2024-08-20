import os
import zipfile
import threading
import aiofiles
from telegram import Bot
from pyrogram import Client
from telegram.error import NetworkError
import asyncio
import aria2p.client
from aria2p.downloads import Download
import aria2p
from queue import Queue
import time
import httpx
from telegram import Update, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import shutil
import bencodepy
import subprocess
import hashlib

ARIA2_RPC_IP = "http://57.154.66.147"  # 替换为你的 Aria2 服务器地址
ARIA2_RPC_PORT = 6800
ARIA2_RPC_SECRET = "mysecret"  # 替换为你的 Aria2 RPC 密钥
BOT_TOKEN = "7327334035:AAFn8lBKph9MYJSL5C6jtYV5vHFHvfBfi3A"
TORRENTS_TMP_DIR = "/home/ubuntu/bot_torrents"  # 定义种子文件会被下载到这个中间路径
TMP_BUNDLE_DIR = '/home/ubuntu/tmp_bund'
BIG_FILE_LIMIT = 2*1024*1024*1024  # 2GB

API_ID = '22556263'
API_HASH = '1a470fb798c07cb0ad5c8c69485bdd18'

ALLOWED_USER_IDS = [7281421323]  # 替换为实际的用户ID列表



mc = aria2p.Client(
    host=ARIA2_RPC_IP,
    port=ARIA2_RPC_PORT,
    secret=ARIA2_RPC_SECRET
)
aria2 = aria2p.API(mc)

rbot = Bot(token=BOT_TOKEN)



async def check_user_permission(update: Update) -> bool:
    user_id = update.effective_user.id
    if user_id in ALLOWED_USER_IDS:
        return True
    await update.message.reply_text("You are not authorized to use this bot.")
    return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_user_permission(update):
        return
    commands = [
        BotCommand("start", "Start the bot"),
        BotCommand("progress", "Check download progress"),
        BotCommand("get_chat_id", "Get the chat ID of the current chat.")
    ]
    await rbot.set_my_commands(commands)
    await update.message.reply_text('Hello! Send me a BT seed file / link.')



async def progress(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_user_permission(update):
        return
    cid = update.effective_chat.id
    pgid = context.user_data.get('download_gid')
    try:
        active_downloads = aria2.get_downloads()
        for dl in active_downloads:
            if dl.gid == pgid:
                pl = mc.tell_status(pgid, ['totalLength', 'completedLength'])
                output = int(pl['completedLength']) / int(pl['totalLength'])
                await update.message.reply_text(f"Download progress: {round(output * 100, 2)}%")
    except Exception as e:
        await update.message.reply_text(f"Failed to check progress: {str(e)}")



async def get_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    await update.message.reply_text(f'This group chat ID is: {chat_id}')



async def my_is_complete(update: Update, context: ContextTypes.DEFAULT_TYPE, download: Download):
    try:
        id = download.gid
        sts = mc.tell_status(id, ['status', 'totalLength', 'completedLength'])
        print(f'download.name,status-{download.name}:{sts}')
        
        if sts['status'] == 'error' and sts['totalLength'] == sts['completedLength']:
            return 'complete'
        
        await asyncio.sleep(3)
        return sts['status']
        
    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Error checking download status: {str(e)}")
        raise

async def report_module(update: Update, context: ContextTypes.DEFAULT_TYPE, download: Download):
    try:
        judge = [0, 0, 0, 0, 0]
        while await my_is_complete(update, context, download) == 'active':
            pl = mc.tell_status(download.gid, ['totalLength', 'completedLength'])
            await asyncio.sleep(3)
            output = 0
            if int(pl['totalLength']) != 0:
                output = int(pl['completedLength']) / int(pl['totalLength'])
            print(output)
            if output == 1.0:
                break
            elif output >= 0.8 and judge[4] == 0:
                judge[4] = 1
                await update.message.reply_text(f"Download progress: {round(output * 100, 2)}%")
            elif output >= 0.6 and judge[3] == 0:
                judge[3] = 1
                await update.message.reply_text(f"Download progress: {round(output * 100, 2)}%")
            elif output >= 0.4 and judge[2] == 0:
                judge[2] = 1
                await update.message.reply_text(f"Download progress: {round(output * 100, 2)}%")
            elif output >= 0.2 and judge[1] == 0:
                judge[1] = 1
                await update.message.reply_text(f"Download progress: {round(output * 100, 2)}%")
        await asyncio.sleep(5)
        if await my_is_complete(update, context, download) == 'error':
            await update.message.reply_text(f"Download error: {download.name}")
            return 'error'
        if await my_is_complete(update, context, download) == 'complete':
            print(f'{download.dir}/{download.name}')
            await update.message.reply_text(f"Download complete: {download.name}")

    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Error in report module: {str(e)}")
        raise




async def handle_magnet_download(update: Update, context: ContextTypes.DEFAULT_TYPE, download: Download):
    try:
        if download.is_metadata:
            # 获取下载的目录或文件路径
            await update.message.reply_text("Downloading metadata...")
            while not download.is_complete:
                await asyncio.sleep(1)
                download.update()
            if download.followed_by_ids:
                real_download_gid = download.followed_by_ids[0]
                real_download = aria2.get_download(real_download_gid)
                context.user_data['download_gid'] = real_download.gid

                await update.message.reply_text(f"Metadata downloaded. Starting actual download: {real_download.name}")
                download_status = await my_is_complete(update, context, real_download)

                if download_status == 'error':
                    active_downloads = aria2.get_downloads()
                    completed_download = None
                    for dl in active_downloads:
                        if dl.status=='complete':
                            if dl.gid==download.gid:
                                continue
                            if download.info_hash==dl.info_hash:
                                completed_download=dl
                                break
                            if completed_download:
                                break

                    ##当存在可绑定已有任务的情况
                    if completed_download:
                        download.remove()
                        print(completed_download.is_metadata)#不成功时是false，成功时True
                        if completed_download.is_metadata:
                            real_complete_downloadid = completed_download.followed_by_ids[0]
                            real_complete_download = aria2.get_download(real_complete_downloadid)



                            context.user_data['download_gid'] = real_complete_download.gid
                            await update.message.reply_text( f"Found an existing active download for {real_complete_download}. " f"Binding current request to this download.")
                            asyncio.create_task(report_module(update, context, real_complete_download))
                        else:
                            context.user_data['download_gid'] = completed_download.gid
                            await update.message.reply_text( f"Found an existing active download for {completed_download}. " f"Binding current request to this download.")
                            asyncio.create_task(report_module(update, context, completed_download))

                    else:
                        await update.message.reply_text("Download.status==error.")
                else:
                    asyncio.create_task(report_module(update, context, real_download))
            else:
                await update.message.reply_text("Failed to retrieve real download after metadata.")
        else:
            await update.message.reply_text(f"Starting download: {download.name}")
            asyncio.create_task(report_module(update, context, download))
    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Error in handling magnet download: {str(e)}")
        raise




async def download_module(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_user_permission(update):
        return  # 如果用户没有权限，退出函数
    try:
        message = update.message.text
        if message and (message.startswith("http://") or message.startswith("https://")):
            dl_list = aria2.add(message)
            download = dl_list[0] 
            context.user_data['download_gid'] = download.gid
            await update.message.reply_text(f"Added URI download: {download.name}")
            asyncio.create_task(report_module(update, context, download))


        elif message and message.startswith("magnet:"):
            context.user_data['magnet_uri'] = message  # 存储磁力链接
            download = aria2.add_magnet(message)
            context.user_data['download_gid'] = download.gid
            await handle_magnet_download(update, context, download)

        elif update.message.document and update.message.document.file_name.endswith(".torrent"):
            file = await context.bot.get_file(update.message.document.file_id)
            file_path = f"{TORRENTS_TMP_DIR}/{update.message.document.file_name}"
            await file.download_to_drive(file_path)
            download = aria2.add_torrent(file_path)
            context.user_data['download_gid'] = download.gid
            await handle_magnet_download(update, context, download)
        else:
            await update.message.reply_text("Unrecognized link or file. Please send a valid URI, magnet link, or torrent file.")
    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Error in download module: {str(e)}")
        raise






def main() -> None:
    try:
        application = ApplicationBuilder().token(BOT_TOKEN).media_write_timeout(300.0).read_timeout(
            300.0).write_timeout(300.0).build()
        application.add_handler(CommandHandler('start', start))
        application.add_handler(CommandHandler('progress', progress))
        application.add_handler(CommandHandler('get_chat_id', get_chat_id))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_module))
        application.add_handler(MessageHandler(filters.Document.ALL, download_module))
        
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        print(f"Failed to start the bot: {str(e)}")

if __name__ == '__main__':
    main()
