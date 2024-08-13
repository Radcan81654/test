import os
import zipfile
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
from telegram import Update, BotCommand, MenuButtonCommands  # pyhton3需要升级到 3.7版本以上
from telegram.ext import Updater, ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from httpx import Timeout
from telegram.request import HTTPXRequest

ARIA2_RPC_IP = "http://57.154.66.147"  # 替换为你的 Aria2 服务器地址
ARIA2_RPC_PORT = 6800
ARIA2_RPC_SECRET = "mysecret"  # 替换为你的 Aria2 RPC 密钥
BOT_TOKEN = "7327334035:AAFn8lBKph9MYJSL5C6jtYV5vHFHvfBfi3A"
TORRENTS_TMP_DIR = "/home/ubuntu/bot_torrents"  # 定义种子文件会被下载到这个中间路径
FILE_SIZE_LIMIT = 524288000  # 500m      #2147483648  # 2gb的字节数
WRITETIME_OUT = 1200.0
CONNECTTIME_OUT = 1200.0
READTIME_OUT = 1200.0

#########################################
mc = aria2p.Client(
    host=ARIA2_RPC_IP,
    port=ARIA2_RPC_PORT,
    secret=ARIA2_RPC_SECRET
)
aria2 = aria2p.API(mc)


########################################3

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message when the bot is started."""
    await update.message.reply_text('Hello! Send me a BT seed file / link ')


async def get_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get the chat ID of the current group."""
    return update.effective_chat.id


###########################################################################
# 文件发送模块

async def split_file(file_path, part_size):
    """将大文件分割成多个小于等于 part_size 的压缩包"""
    file_size = os.path.getsize(file_path)
    base_filename = os.path.basename(file_path)
    part_number = 1
    parts = []

    async with aiofiles.open(file_path, 'rb') as src_file:
        while True:
            chunk = await src_file.read(part_size)
            if not chunk:
                break
            part_filename = f"{base_filename}.part{part_number}.zip"
            parts.append(part_filename)
            with zipfile.ZipFile(part_filename, 'w', zipfile.ZIP_DEFLATED) as part_file:
                part_file.writestr(base_filename, chunk)
            part_number += 1

    return parts


async def send_module(update: Update, context: ContextTypes.DEFAULT_TYPE, download: Download):
    downloaded_filename = os.path.join(download.dir, download.name)
    file_size = os.path.getsize(downloaded_filename)
    chat_id = update.effective_chat.id

    big_file_limit = 45 * 1024 * 1024  # 45 MB

    try:
        if file_size <= big_file_limit:
            # 使用标准的 open 函数而不是 aiofiles
            with open(downloaded_filename, 'rb') as file:
                await context.bot.send_document(chat_id=chat_id, document=file)
        else:
            part_size = big_file_limit - (1 * 1024 * 1024)
            parts = await split_file(downloaded_filename, part_size)

            for part in parts:
                with open(part, 'rb') as file:
                    await context.bot.send_document(chat_id=chat_id, document=file)
                os.remove(part)  # 发送后删除压缩包

            await context.bot.send_message(chat_id=chat_id, text="File sent successfully")
    except NetworkError as e:
        await context.bot.send_message(chat_id=chat_id, text=f"Failed sending: {str(e)}")


# 示例使用
# application = Application.builder().token('YOUR_TELEGRAM_BOT_TOKEN').build()
# await send_file(application.bot, chat_id=123456789, downloaded_filename='path/to/downloaded_filename')


async def my_is_complete(update: Update, context: ContextTypes.DEFAULT_TYPE, download: Download):
    id = download.gid
    sts = mc.tell_status(id, ['status'])
    print(sts)
    if sts['status'] == 'complete':
        return True
    return False


async def download_module(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Download:
    message = update.message.text
    if message.startswith("http://") or message.startswith("https://"):
        # 处理 URI
        download = aria2.add(message)[0]  # 此处返回被创建出来的文件,理论上可以添加多个
        context.user_data['download_gid'] = download.gid
        await update.message.reply_text(f"Added URI download: {download.name}")

    elif message.startswith("magnet:"):
        # 处理磁力链接
        download = aria2.add(message)[0]
        context.user_data['download_gid'] = download.gid
        await update.message.reply_text(f"Added Magnet download: {download.name}")

    elif update.message.document and update.message.document.file_name.endswith(".torrent"):
        # 处理种子文件
        file = await context.bot.get_file(update.message.document.file_id)
        file_path = f"{TORRENTS_TMP_DIR}/{update.message.document.file_name}"
        await file.download_to_drive(file_path)  # 把种子文件保存到本地路径
        download = aria2.add_torrent(file_path)  # 下载文件
        context.user_data['download_gid'] = download.gid
        await update.message.reply_text(f"Added Torrent download: {download.name}")

    else:
        await update.message.reply_text(
            "Unrecognized link or file. Please send a valid URI, magnet link, or torrent file.")
        # 从这个部分考虑从bot手里发送已有的文件到客户端
        if (download.total_length >= FILE_SIZE_LIMIT):
            download.remove()
            print("I cant send u files that over 2gb,sry")
            return
    return download


async def report_module(update: Update, context: ContextTypes.DEFAULT_TYPE, download: Download) -> None:
    while await my_is_complete(update, context, download):
        pl = mc.tell_status(download.gid, ['totalLength', 'completedLength'])
        output = int(pl['completedLength']) / int(pl['totalLength'])
        print(output)
        if (output == 1.0):
            break
        elif (output >= 0.8):
            await update.message.reply_text(f"Download progress: {output}")
        elif (output >= 0.6):
            await update.message.reply_text(f"Download progress: {output}")
        elif (output >= 0.4):
            await update.message.reply_text(f"Download progress: {output}")
        elif (output >= 0.2):
            await update.message.reply_text(f"Download progress: {output}")
    await asyncio.sleep(5)


# 最终需要使用的部分
async def the_module(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    dl = await download_module(update, context)
    await report_module(update, context, dl)
    await send_module(update, context, dl)


########################################################################3
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message when the bot is started."""
    await update.message.reply_text('Hello! Send me a BT seed file / link ')


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a help message when the bot is asked for help."""
    await update.message.reply_text(
        'Hello! Send me a BT seed file / link ,I will send you their corresponding files, the upper limit is 500M')


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """取消下载并清除中间文件"""
    chat_id = update.effective_chat.id
    try:
        # 获取当前的所有下载任务
        active_downloads = aria2.get_downloads()

        # 遍历所有下载任务并取消
        for download in active_downloads:
            mc.remove(download.gid)
            await update.message.reply_text(f"Download {download.name} has been cancelled.")

        # 清理中间文件
        base_filename = ""
        if update.message.document:
            base_filename = os.path.basename(update.message.document.file_name)
        elif update.message.text:
            base_filename = os.path.basename(update.message.text)

        # 找到并删除所有的part文件
        for part_file in os.listdir('.'):
            if part_file.startswith(base_filename) and part_file.endswith(".zip"):
                os.remove(part_file)
                await update.message.reply_text(f"Removed temporary file: {part_file}")

    except Exception as e:
        await update.message.reply_text(f"Failed to cancel download: {str(e)}")


###################################################
rbot = Bot(token=BOT_TOKEN)
uq = Queue()
updater = Updater(bot=rbot, update_queue=uq)


def set_menu_button():
    # 这个也是异步
    rbot.set_chat_menu_button(menu_button=MenuButtonCommands())


###################
def main() -> None:
    """Run the bot."""
    application = ApplicationBuilder().token(BOT_TOKEN).media_write_timeout(300.0).build()  # 可用的版本

    ##########################################
    # on different commands - answer in Telegram
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', start))
    application.add_handler(CommandHandler('cancel', start))

    # on non-command messages - check for ads
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, the_module))  # 检测发送信息
    application.add_handler(MessageHandler(filters.Document.ALL, the_module))  # 检测用户发送文件
    set_menu_button()
    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()

