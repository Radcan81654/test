import os
import zipfile
import threading
import aiofiles
from telegram import Bot
from telegram.error import NetworkError
import asyncio
import aria2p.client
from aria2p.downloads import Download
import aria2p
from queue import Queue
import time
import httpx
from telegram import Update, BotCommand, MenuButtonCommands
from telegram.ext import Updater, ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from httpx import Timeout
from telegram.request import HTTPXRequest

ARIA2_RPC_IP = "http://57.154.66.147"  # 替换为你的 Aria2 服务器地址
ARIA2_RPC_PORT = 6800
ARIA2_RPC_SECRET = "mysecret"  # 替换为你的 Aria2 RPC 密钥
BOT_TOKEN = "7327334035:AAFn8lBKph9MYJSL5C6jtYV5vHFHvfBfi3A"
TORRENTS_TMP_DIR = "/home/ubuntu/bot_torrents"  # 定义种子文件会被下载到这个中间路径
TMP_BUNDLE_DIR = '/home/ubuntu/tmp_bund'
#FILE_SIZE_LIMIT = 524288000  # 500M
FILE_SIZE_LIMIT = 500000000000  # 500M

WRITETIME_OUT = 300.0
CONNECTTIME_OUT = 300.0
READTIME_OUT = 300.0

mc = aria2p.Client(
    host=ARIA2_RPC_IP,
    port=ARIA2_RPC_PORT,
    secret=ARIA2_RPC_SECRET
)
aria2 = aria2p.API(mc)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message when the bot is started."""
    await update.message.reply_text('Hello! Send me a BT seed file / link ')
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message when the bot is started."""
    await update.message.reply_text('I will download the file for you and send it to this chat. \nDue to platform limitations, I can only send it in parts of less than 100MB each.\nI will download the file for you and send it to this chat. Due to platform limitations, I can only send it in parts of less than 100MB each\nIf the progress is proceeding normally, I will send you progress updates. If the download fails, you will also receive a notification') 


async def get_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get the chat ID of the current group."""
    return update.effective_chat.id


async def split_file(file_path, part_size, output_dir):
    file_size = os.path.getsize(file_path)
    base_filename = os.path.basename(file_path)
    part_number = 1
    parts = []

    os.makedirs(output_dir, exist_ok=True)

    async with aiofiles.open(file_path, 'rb') as src_file:
        while True:
            chunk = await src_file.read(part_size)
            if not chunk:
                break
            part_filename = f"{base_filename}.part{part_number}.zip"
            part_path = os.path.join(output_dir, part_filename)
            parts.append(part_path)
            with zipfile.ZipFile(part_path, 'w', zipfile.ZIP_DEFLATED) as part_file:
                part_file.writestr(base_filename, chunk)
            part_number += 1
    return parts

async def send_module(update: Update, context: ContextTypes.DEFAULT_TYPE, download: Download, output_dir: str):
    try:
        downloaded_filename = os.path.join(download.dir, download.name)
        chat_id = update.effective_chat.id

        if os.path.isdir(downloaded_filename):
            # 如果是目录，压缩整个目录
            zip_filename = f"{download.name}.zip"
            zip_filepath = os.path.join(output_dir, zip_filename)
            with zipfile.ZipFile(zip_filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(downloaded_filename):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, start=downloaded_filename)
                        zipf.write(file_path, arcname=arcname)
            # 发送压缩后的文件
            zip_filesize=os.path.getsize(zip_filename)
            big_file_limit = 45 * 1024 * 1024  # 45 MB
            if zip_filesize<=big_file_limit:
                with open(zip_filename,'rb') as file:
                    await context.bot.send_document(chat_id=chat_id, document=file)
            else:
                part_size = big_file_limit - (1 * 1024 * 1024)
                parts=await split_file(zip_filename,part_size,output_dir)
                for part in parts:
                    with open(part, 'rb') as file:
                        await context.bot.send_document(chat_id=chat_id, document=file)
                    os.remove(part)
                await context.bot.send_message(chat_id=chat_id, text="File sent successfully")

        else:
            # 如果是文件，直接发送或拆分后发送
            file_size = os.path.getsize(downloaded_filename)
            big_file_limit = 45 * 1024 * 1024  # 45 MB

            if file_size <= big_file_limit:
                with open(downloaded_filename, 'rb') as file:
                    await context.bot.send_document(chat_id=chat_id, document=file)
            else:
                part_size = big_file_limit - (1 * 1024 * 1024)
                parts = await split_file(downloaded_filename, part_size, output_dir)
                for part in parts:
                    with open(part, 'rb') as file:
                        await context.bot.send_document(chat_id=chat_id, document=file)
                    os.remove(part)

            await context.bot.send_message(chat_id=chat_id, text="File sent successfully")
    except NetworkError as e:
        await context.bot.send_message(chat_id=chat_id, text=f"Failed sending: {str(e)}")
    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"An error occurred: {str(e)}")






async def my_is_complete(update: Update, context: ContextTypes.DEFAULT_TYPE, download: Download):
    try:
        id = download.gid
        sts = mc.tell_status(id, ['status'])
        print(sts)
        return sts['status'] 
        
    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id,text=f"Error checking download status: {str(e)}")
        raise


async def download_module(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Download:
    try:
        message = update.message.text
        
        if message and (message.startswith("http://") or message.startswith("https://")):
            download = aria2.add(message)[0]
            context.user_data['download_gid'] = download.gid
            await update.message.reply_text(f"Added URI download: {download.name}")

        elif message and (message.startswith("magnet:")):
            download = aria2.add(message)[0]
            context.user_data['download_gid'] = download.gid
            await update.message.reply_text(f"Added Magnet download: {download.name}")

        elif update.message.document and update.message.document.file_name.endswith(".torrent"):
            file = await context.bot.get_file(update.message.document.file_id)
            file_path = f"{TORRENTS_TMP_DIR}/{update.message.document.file_name}"
            await file.download_to_drive(file_path)
            download = aria2.add_torrent(file_path)
            context.user_data['download_gid'] = download.gid
            await update.message.reply_text(f"Added Torrent download: {download.name}")

        else:
            await update.message.reply_text(
                "Unrecognized link or file. Please send a valid URI, magnet link, or torrent file.")
            return
        return download
    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Error in download module: {str(e)}")
        raise


async def report_module(update: Update, context: ContextTypes.DEFAULT_TYPE, download: Download) :
    try:
        judge=[0,0,0,0]
        while await my_is_complete(update, context, download)=='active':
            pl = mc.tell_status(download.gid, ['totalLength', 'completedLength'])
            output = int(pl['completedLength']) / int(pl['totalLength'])
            
            print(output)
            if output == 1.0:
                break
            elif output >= 0.8 and judge[4]==0:
                judge[4]=1
                await update.message.reply_text(f"Download progress: {round(output*100,2)}%")
            elif output >= 0.6 and judge[3]==0:
                judge[3]=1
                await update.message.reply_text(f"Download progress: {round(output*100,2)}%")
            elif output >= 0.4 and judge[2]==0:
                judge[2]=1
                await update.message.reply_text(f"Download progress: {round(output*100,2)}%")
            elif output >= 0.2 and judge[1]==0:
                judge[1]=1
                await update.message.reply_text(f"Download progress: {round(output*100,2)}%")
        await asyncio.sleep(3)
        if await my_is_complete(update, context, download)=='error':
            await update.message.reply_text(f"Download error")
            return 'error'
        if await my_is_complete(update, context, download)=='complete':
            await update.message.reply_text(f"Download complete")
    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Error in report module: {str(e)}")
        raise


async def the_module(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        dl = await download_module(update, context)
        flag=await report_module(update, context, dl)
        if flag=='complete':
            await send_module(update, context, dl, TMP_BUNDLE_DIR)
    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Error in the main module: {str(e)}")



async def set_menu_button(bot: Bot) -> None:
    await bot.set_chat_menu_button(menu_button=MenuButtonCommands())


#####################################################################################################
# 把事件循环加入到现有逻辑里面的话，产生的报错根本不是(我+chatgpt)能解决的
# 在另一个线程中运行异步任务
def run_async_task(loop, bot):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(set_menu_button(bot))


##########################################################################################################

def main() -> None:
    try:
        application = ApplicationBuilder().token(BOT_TOKEN).media_write_timeout(300.0).read_timeout(
            READTIME_OUT).write_timeout(WRITETIME_OUT).build()
        application.add_handler(CommandHandler('start', start))
        application.add_handler(CommandHandler('help', start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, the_module))
        application.add_handler(MessageHandler(filters.Document.ALL, the_module))

        loop = asyncio.new_event_loop()
        threading.Thread(target=run_async_task, args=(loop, application.bot)).start()

        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        print(f"Failed to start the bot: {str(e)}")


if __name__ == '__main__':
    main()