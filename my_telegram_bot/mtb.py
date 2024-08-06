import logging
import re
from telegram import Update, ChatPermissions
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Bot Token from BotFather
TOKEN = '7327334035:AAFn8lBKph9MYJSL5C6jtYV5vHFHvfBfi3A'

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Define a list of keywords and regular expressions for ad detection
AD_KEYWORDS = ['buy now', 'limited offer', 'exclusive discount', 'promo', 'promotion', 'special offer', 'sale', 'discount', 'deal', 'free shipping', 'act now']
AD_REGEX_PATTERNS = [
    re.compile(r'\b(buy\s+now|limited\s+offer|exclusive\s+discount)\b', re.IGNORECASE),
    re.compile(r'\b(promo|promotion|special\s+offer|sale)\b', re.IGNORECASE),
    re.compile(r'\b(discount|deal|free\s+shipping|act\s+now)\b', re.IGNORECASE)
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message when the bot is started."""
    await update.message.reply_text('Hello! I am an anti-ad bot. I will remove any ads from this group.')

async def check_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Check incoming messages for ads and kick users if ads are found."""
    message_text = update.message.text

    # Check for keywords
    if any(keyword in message_text.lower() for keyword in AD_KEYWORDS):
        await kick_user(update, context)
        return

    # Check for regular expression patterns
    if any(pattern.search(message_text) for pattern in AD_REGEX_PATTERNS):
        await kick_user(update, context)
        return

async def kick_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Kick the user who sent the ad."""
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id

    # Kick the user from the chat
    await context.bot.ban_chat_member(chat_id, user_id)

    # Send a message to the group
    await update.message.reply_text(f"User {update.message.from_user.mention_html()} has been kicked for sending ads.", parse_mode='HTML')

def main() -> None:
    """Run the bot."""
    application = Application.builder().token(TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler('start', start))

    # on non-command messages - check for ads
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_message))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()

