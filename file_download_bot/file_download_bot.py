import os
import asyncio
from aria2p.downloads import Download
import aria2p
from telegram import Update  # pyhton3需要升级到 3.7版本以上
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

ARIA2_RPC_IP = "http://123.56.166.61"
ARIA2_RPC_PORT = 6800
ARIA2_RPC_SECRET = "lgd.chalice.taobao"
BOT_TOKEN = "7327334035:AAFn8lBKph9MYJSL5C6jtYV5vHFHvfBfi3A"
TORRENTS_TMP_DIR = "/root/bot_torrents"  # 定义种子文件会被下载到这个中间路径
DOWNLOAD_DIR = "/root/downloads"  # 根据(磁力)链接/种子文件下载好的文件默认存放的目录
FILE_SIZE_LIMIT = 2147483648  # 2gb的字节数
# 最大允许的下载时间，超过的话就自动停止


aria2 = aria2p.API(
    aria2p.Client(
        host=ARIA2_RPC_IP,  # 替换为你的 Aria2 服务器地址
        port=ARIA2_RPC_PORT,
        secret=ARIA2_RPC_SECRET  # 替换为你的 Aria2 RPC 密钥
    )
)


async def get_name(downloads: Download):
    return Download.name


# async def get_status(downloads:Download ):
# Download.

async def get_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get the chat ID of the current group."""
    return update.effective_chat.id


###########################################################################
# 文件发送模块
async def send_module(update: Update, context: ContextTypes.DEFAULT_TYPE, download: Download):
    target_id = update.message.chat_id
    download_file_path = os.path.join(DOWNLOAD_DIR, download.name)  # 确保是实例属性
    await context.bot.send_document(chat_id=target_id, document=open(download_file_path, 'rb'))


#########################################################################
# 消息通知模块
# async def report_module(update: Update, context: ContextTypes.DEFAULT_TYPE):

###########################################################################
# 最终执行的模块
async def my_is_complete(downloads: Download):
    return Download.is_complete


async def the_module(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
    ###########文件下载中，以下部分开始考虑消息通知与文件发送

    while True:
        if await my_is_complete(download):
            await update.message.reply_text("Download complete")
            await send_module(update, context, download)
            break
        await asyncio.sleep(5)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message when the bot is started."""
    await update.message.reply_text('Hello! Send me a BT seed file / link ')


def main() -> None:
    """Run the bot."""
    application = Application.builder().token(BOT_TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler('start', start))

    # on non-command messages - check for ads
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, the_module))  # 检测发送信息
    application.add_handler(MessageHandler(filters.Document.ALL, the_module))  # 检测用户发送文件

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()