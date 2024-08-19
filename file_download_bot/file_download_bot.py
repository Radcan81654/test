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

mc = aria2p.Client(
    host=ARIA2_RPC_IP,
    port=ARIA2_RPC_PORT,
    secret=ARIA2_RPC_SECRET
)
aria2 = aria2p.API(mc)

rbot = Bot(token=BOT_TOKEN)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    commands = [
        BotCommand("start", "Start the bot"),
        BotCommand("help", "Get help"),
        BotCommand("progress", "Check download progress"),
        BotCommand("upload_progress", "Check upload progress"),
        BotCommand("get_chat_id", "Get the chat ID of the current chat.")
    ]
    await rbot.set_my_commands(commands)
    await update.message.reply_text('Hello! Send me a BT seed file / link.')

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        'I will download the file for you and send it to this chat. \n'
        'Due to platform limitations, I can only send it in parts of less than 2GB each.\n'
        'I will keep you updated on the progress.'
    )

async def progress(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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

async def upload_progress(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    upload_info = context.user_data.get('upload_progress')
    if upload_info:
        await update.message.reply_text(
            f"Uploading {upload_info['file_name']}: {upload_info['progress']}% completed."
        )
    else:
        await update.message.reply_text("No upload in progress or progress information is not available.")

async def get_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    await update.message.reply_text(f'This group chat ID is: {chat_id}')

async def split_file(file_path, part_size):
    file_size = os.path.getsize(file_path)
    base_filename = os.path.basename(file_path)
    part_number = 1
    parts = []

    os.makedirs(TMP_BUNDLE_DIR, exist_ok=True)

    async with aiofiles.open(file_path, 'rb') as src_file:
        while True:
            chunk = await src_file.read(part_size)
            if not chunk:
                break
            part_filename = f"{base_filename}.part{part_number}.zip"
            part_path = os.path.join(TMP_BUNDLE_DIR, part_filename)
            parts.append(part_path)
            with zipfile.ZipFile(part_path, 'w', zipfile.ZIP_DEFLATED) as part_file:
                part_file.writestr(base_filename, chunk)
            part_number += 1
    return parts

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

            # 存储下载完成后的文件信息到上下文
            context.user_data['download_filecontent'] = os.path.join(download.dir, download.name)
            context.user_data['download_name'] = download.name

            # 立即开始上传下载完成的文件或文件夹
            await send_module(update, context, download)
            return 'complete'
    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Error in report module: {str(e)}")
        raise

async def progress_callback(current, total, chat_id, file_path, context):
    progress_percentage = round(current / total * 100, 2)
    last_reported_progress = context.user_data.get('last_reported_progress', 0)
    context.user_data['upload_progress'] = {
        'file_name': os.path.basename(file_path),
        'progress': progress_percentage
    }

    if (int(progress_percentage) % 20 == 0 and int(progress_percentage) > last_reported_progress) or int(progress_percentage) == 100:
        context.user_data['last_reported_progress'] = int(progress_percentage)
        progress_message = f"Uploading {os.path.basename(file_path)}: {progress_percentage}% completed."
        await rbot.send_message(chat_id=chat_id, text=progress_message)

async def send_file_or_split(app, chat_id, file_path, context):
    try:
        file_size = os.path.getsize(file_path)
        if file_size <= BIG_FILE_LIMIT:
            await app.send_document(chat_id, file_path, progress=progress_callback, progress_args=(chat_id, file_path, context))
        else:
            part_size = BIG_FILE_LIMIT - (1 * 1024 * 1024)
            parts = await split_file(file_path, part_size)
            for part in parts:
                await app.send_document(chat_id, part, progress=progress_callback, progress_args=(chat_id, part, context))
                os.remove(part)
            await app.send_message(chat_id, "All parts sent successfully.")
    except Exception as e:
        await app.send_message(chat_id, f"Failed to send file: {str(e)}")

async def send_module(update: Update, context: ContextTypes.DEFAULT_TYPE, download: Download):
    try:
        chat_id = update.effective_chat.id
        download_filecontent = context.user_data.get('download_filecontent')

        async with Client("my_account", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN, in_memory=True) as app:
            if os.path.isfile(download_filecontent):
                await send_file_or_split(app, chat_id, download_filecontent, context)
            elif os.path.isdir(download_filecontent):
                zip_filename = f"{download_filecontent}.zip"
                shutil.make_archive(download_filecontent, 'zip', download_filecontent)
                await send_file_or_split(app, chat_id, zip_filename, context)
            else:
                await update.message.reply_text(f"{context.user_data['download_name']} sent failed. File not found.")
    except NetworkError as e:
        await update.message.reply_text(f"Failed sending: {str(e)}")
    except Exception as e:
        await update.message.reply_text(f"An error occurred while sending: {str(e)}")

import subprocess

# def delete_with_sudo(path):
#     try:
#         # 使用sudo执行删除命令
#         if os.path.isdir(path):
#             subprocess.run(['sudo', 'rm', '-rf', path], check=True)
#         elif os.path.isfile(path):
#             subprocess.run(['sudo', 'rm', '-f', path], check=True)
#         print(f"Successfully deleted: {path}")
#     except subprocess.CalledProcessError as e:
#         print(f"Failed to delete {path}: {e}")

async def handle_magnet_download(update: Update, context: ContextTypes.DEFAULT_TYPE, download: Download):
    try:
        if download.is_metadata:
            # 获取下载的目录或文件路径
            await update.message.reply_text("Downloading metadata...")
            while not download.is_complete:
                await asyncio.sleep(1)
                download.update()
            # #######################################################
            # # 使用 tell_active 获取所有活动任务
            # active_downloads = mc.tell_active()
            # completed_download = None
            # for dl in active_downloads:
            #     if dl['gid']==download.gid:
            #         continue
            #     if download.info_hash==dl['infoHash']:
            #         completed_download=dl
            #         break
            #     if completed_download:
            #         break

            # ##当存在可绑定已有任务的情况
            # if completed_download:
            #     rm_list=[download.gid]
            #     download.remove()
            #     context.user_data['download_gid'] = completed_download['gid']
            #     await update.message.reply_text( f"Found an existing active download for {completed_download['name']}. " f"Binding current request to this download.")
            #     asyncio.create_task(report_module(update, context, completed_download))
            # #################################################################
            #####正常处理
            if download.followed_by_ids:
                real_download_gid = download.followed_by_ids[0]
                real_download = aria2.get_download(real_download_gid)
                context.user_data['download_gid'] = real_download.gid

                await update.message.reply_text(f"Metadata downloaded. Starting actual download: {real_download.name}")
                #################################################################################################
                # 检查实际下载任务的状态
                ##考虑在删除的部分添加绑定任务的的代码，但这次是寻找status为complete的
                download_status = await my_is_complete(update, context, real_download)

                if download_status == 'error':
                    # real_download_path = os.path.join(real_download.dir, real_download.name)
                    
                    # # 检查并删除已存在的文件或目录
                    # if os.path.exists(real_download_path):
                    #     await update.message.reply_text(f"Download failed with error. Found existing download content for {real_download.name}. Deleting it and retrying...")
                        
                    #     # 使用带有 sudo 权限的删除操作,删出事了，后面重新添加的时候会绑定到已经完成的这个任务上面
                    #     delete_with_sudo(real_download_path)

                    # # 重新添加下载任务
                    # new_download = aria2.add_magnet(context.user_data['magnet_uri'])
                    # context.user_data['download_gid'] = new_download.gid
                    # await handle_magnet_download(update, context, new_download)
                    #######################################################
                    # 使用 tell_active 获取所有活动任务
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

                        real_complete_downloadid = completed_download.followed_by_ids[0]
                        real_complete_download = aria2.get_download(real_complete_downloadid)



                        context.user_data['download_gid'] = real_complete_download.gid
                        await update.message.reply_text( f"Found an existing active download for {real_complete_download}. " f"Binding current request to this download.")
                        asyncio.create_task(report_module(update, context, real_complete_download))

                    #################################################################
                    else:
                        await update.message.reply_text("Download.status==error.")
                ###############################################################################################3
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
    try:
        message = update.message.text
        if message and (message.startswith("http://") or message.startswith("https://")):
            dl_list = aria2.add(message)
            download = dl_list[0] 
            context.user_data['download_gid'] = download.gid
            await update.message.reply_text(f"Added URI download: {download.name}")
            asyncio.create_task(report_module(update, context, download))
            asyncio.create_task(send_module(update, context, download))

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
        application.add_handler(CommandHandler('help', help))
        application.add_handler(CommandHandler('progress', progress))
        application.add_handler(CommandHandler('upload_progress', upload_progress))
        application.add_handler(CommandHandler('get_chat_id', get_chat_id))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_module))
        application.add_handler(MessageHandler(filters.Document.ALL, download_module))
        
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        print(f"Failed to start the bot: {str(e)}")

if __name__ == '__main__':
    main()
