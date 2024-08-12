import os
import asyncio
import aria2p.client
from aria2p.downloads import Download
import aria2p
import time
import httpx
from telegram import Update, BotCommand  # pyhton3需要升级到 3.7版本以上
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from httpx import Timeout
from telegram.request import HTTPXRequest

ARIA2_RPC_IP = "http://57.154.66.147"  # 替换为你的 Aria2 服务器地址
ARIA2_RPC_PORT = 6800
ARIA2_RPC_SECRET = "mysecret"  # 替换为你的 Aria2 RPC 密钥
BOT_TOKEN = "7327334035:AAFn8lBKph9MYJSL5C6jtYV5vHFHvfBfi3A"
TORRENTS_TMP_DIR = "/home/ubuntu/bot_torrents"  # 定义种子文件会被下载到这个中间路径
DOWNLOAD_DIR = "/home/ubuntu/downloads"  # 根据(磁力)链接/种子文件下载好的文件默认存放的目录
FILE_SIZE_LIMIT = 2147483648  # 2gb的字节数
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


async def send_module(update: Update, context: ContextTypes.DEFAULT_TYPE, download: Download):
    ##问题是一方面得确实下载完，另一方面最好检测一下大小是不是能对上，对的上的话就可以发了
    while await my_is_complete(update, context, download):
        await update.message.reply_text("Download complete")
        target_id = update.message.chat_id
        download_file_path = os.path.join(DOWNLOAD_DIR, download.name)  # 确保是实例属性
        await context.bot.send_document(chat_id=target_id, document=open(download_file_path, 'rb'))
        break
    # 新的问题是发送文件的时间目前来看远远大于下载文件所花费的时间
    await asyncio.sleep(5)


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
        await update.message.reply_text(f"Added URI download: {download.name}")

    elif message.startswith("magnet:"):
        # 处理磁力链接
        download = aria2.add(message)[0]
        await update.message.reply_text(f"Added Magnet download: {download.name}")

    elif update.message.document and update.message.document.file_name.endswith(".torrent"):
        # 处理种子文件
        file = await context.bot.get_file(update.message.document.file_id)
        file_path = f"{TORRENTS_TMP_DIR}/{update.message.document.file_name}"
        await file.download_to_drive(file_path)  # 把种子文件保存到本地路径
        download = aria2.add_torrent(file_path)  # 下载文件
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


def main() -> None:
    """Run the bot."""
    # application = ApplicationBuilder().token(BOT_TOKEN).build()#可用的版本
    ########################################################################
    # 测试
    # 设置超时和其他参数

    # 创建 HTTPXRequest 对象
    # media_write_timeout=300.0#时间根本没够用
    # http_version='1.1'时报错为raise NetworkError(f"httpx.{err.__class__.__name__}: {err}") from err telegram.error.NetworkError: httpx.ReadError:
    # http_version='2'时报错为telegram.error.NetworkError: httpx.RemoteProtocolError: <ConnectionTerminated error_code:ErrorCodes.NO_ERROR, last_stream_id:3, additional_data:None>
    request = HTTPXRequest(http_version='1.1', media_write_timeout=1200.0, read_timeout=READTIME_OUT,
                           write_timeout=WRITETIME_OUT, connect_timeout=CONNECTTIME_OUT)

    # 配置 Application 对象
    application = ApplicationBuilder().token(BOT_TOKEN).request(request).build()

    ##########################################
    # on different commands - answer in Telegram
    application.add_handler(CommandHandler('start', start))

    # on non-command messages - check for ads
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, the_module))  # 检测发送信息
    application.add_handler(MessageHandler(filters.Document.ALL, the_module))  # 检测用户发送文件

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
