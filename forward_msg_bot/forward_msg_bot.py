import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Bot Token from BotFather
TOKEN = '7327334035:AAFn8lBKph9MYJSL5C6jtYV5vHFHvfBfi3A'
TARGET_CHAT_ID = '1921762512'
# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('forwarding_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 启动或停止消息转发的函数
async def toggle_forwarding_to(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """切换消息转发状态。"""
    chat_data = context.chat_data

    if chat_data.get('forwarding', False):
        chat_data['forwarding'] = False
        await update.message.reply_text('消息转发已禁用。')
        logger.info("消息转发已禁用")
    else:
        chat_data['forwarding'] = True
        await update.message.reply_text('消息转发已启用。')
        logger.info("消息转发已启用")

# 转发消息的函数
async def forward_message_to(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """将(群组中)收到的消息转发到TARGET_CHAT。"""
    chat_data = context.chat_data

    if chat_data.get('forwarding', False):
        target_chat_id = TARGET_CHAT_ID  # 目标聊天 ID
        logger.info(f"正在将消息从 chat_id={update.effective_chat.id} 转发到 chat_id={target_chat_id}")
        await context.bot.forward_message(chat_id=target_chat_id, from_chat_id=update.effective_chat.id, message_id=update.message.message_id)
    else:
        logger.info("消息转发已禁用")

def main() -> None:
    """运行机器人。"""
    application = Application.builder().token(TOKEN).build()

    # 不同命令的处理器 - 在 Telegram 中响应
    application.add_handler(CommandHandler('toggle_forwarding_to', toggle_forwarding_to))

    # 检查是否启用消息转发
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_message_to))

    # 运行机器人，直到用户按下 Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()