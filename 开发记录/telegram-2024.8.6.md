# 第一周任务



[TOC]

## 2024.8.6

主要任务为探索telegram的bot和小程序,从father_bot这里申请bot

主要参考示例代码

### 已知可靠信息

- [Telegram Bot API 文档](https://core.telegram.org/bots/api)
- [python-telegram-bot 文档](https://python-telegram-bot.readthedocs.io/en/stable/)

### 关于bots

小程序的功能和群组管理的功能可以同时集成到同一个bot里面

---

#### 关于申请bot/自定义bot的功能

**use this token to access the http api:**

7327334035:AAFn8lBKph9MYJSL5C6jtYV5vHFHvfBfi3A

### 初步的一些想法/想要实现的功能



#### ~~1.漂流瓶~~

```python

import json
import logging
import random
import mysql.connector
from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler

# Telegram Bot Token
TOKEN = "YOUR_API_TOKEN"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# MySQL database connection
db_config = {
    'user': 'your_mysql_user',
    'password': 'your_mysql_password',
    'host': 'your_mysql_host',
    'database': 'your_database_name'
}

conn = mysql.connector.connect(**db_config)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS bottles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT,
    message TEXT,
    photo LONGBLOB
)''')
c.execute('''CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY
)''')
conn.commit()

# Define constants for ConversationHandler states
CHOOSING, TYPING_REPLY = range(2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message and display inline keyboard for drift bottle feature."""
    keyboard = [
        [
            InlineKeyboardButton("漂流瓶功能说明", callback_data='explain_bottle'),
            InlineKeyboardButton("发送漂流瓶", callback_data='send_bottle'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("欢迎使用漂流瓶Bot！请选择一个选项:", reply_markup=reply_markup)
    
    # Register user if not already in database
    user_id = update.message.from_user.id
    c.execute('''INSERT IGNORE INTO users (user_id) VALUES (%s)''', (user_id,))
    conn.commit()

async def explain_bottle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Explain the drift bottle feature."""
    query = update.callback_query
    await query.answer()
    explanation = (
        "漂流瓶功能允许你向群组中的其他成员发送匿名信息或图片。"
        "你可以私信我一段文字或图片作为漂流瓶，而这个漂流瓶会被群组内的其他随机成员接收。"
    )
    await query.edit_message_text(text=explanation)

async def send_bottle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Prompt the user to send a drift bottle."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="请私信我你想发送的漂流瓶内容（文字或图片）。")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming messages (text or photo) and store them as drift bottles."""
    user_id = update.message.from_user.id
    if update.message.chat.type == 'private':
        if update.message.text:
            c.execute("INSERT INTO bottles (user_id, message, photo) VALUES (%s, %s, %s)", 
                      (user_id, update.message.text, None))
        elif update.message.photo:
            file_info = await context.bot.get_file(update.message.photo[-1].file_id)
            downloaded_file = await file_info.download_as_bytearray()
            c.execute("INSERT INTO bottles (user_id, message, photo) VALUES (%s, %s, %s)", 
                      (user_id, None, downloaded_file))
        conn.commit()
        await update.message.reply_text("你的漂流瓶已放入大海，等待被捡起。")
        await distribute_bottle(user_id, context)

async def distribute_bottle(sender_id: int, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Distribute a random drift bottle to a random user who is not the sender."""
    c.execute("SELECT id, user_id, message, photo FROM bottles ORDER BY RAND() LIMIT 1")
    bottle = c.fetchone()
    if bottle:
        c.execute("SELECT user_id FROM users WHERE user_id != %s ORDER BY RAND() LIMIT 1", (sender_id,))
        recipient = c.fetchone()
        if recipient:
            recipient_id = recipient[0]
            if bottle[3]:  # If it's a photo
                await context.bot.send_photo(recipient_id, bottle[3], caption="你捡到一个漂流瓶！")
            else:
                await context.bot.send_message(recipient_id, f"你捡到一个漂流瓶：\n{bottle[2]}")
            c.execute("DELETE FROM bottles WHERE id = %s", (bottle[0],))
            conn.commit()

async def example_color_picker(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message with a button that opens the web app."""
    await update.message.reply_text(
        "Please press the button below to choose a color via the WebApp.",
        reply_markup=ReplyKeyboardMarkup.from_button(
            KeyboardButton(
                text="Open the color picker!",
                web_app=WebAppInfo(url="https://python-telegram-bot.org/static/webappbot"),
            )
        ),
    )

async def web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Print the received data and remove the button."""
    data = json.loads(update.effective_message.web_app_data.data)
    await update.message.reply_html(
        text=(
            f"You selected the color with the HEX value <code>{data['hex']}</code>. The "
            f"corresponding RGB value is <code>{tuple(data['rgb'].values())}</code>."
        ),
        reply_markup=ReplyKeyboardRemove(),
    )

def main() -> None:
    """Start the bot."""
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(explain_bottle, pattern='explain_bottle'))
    application.add_handler(CallbackQueryHandler(send_bottle, pattern='send_bottle'))
    application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data))
    application.add_handler(MessageHandler(filters.ALL, handle_message))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()

```



#### 2.踢出发送广告信息的用户

```python
#CommandHandler用于处理以斜杠开头的命令（例如/start，/help等）。它根据用户输入的命令触发相应的回调函数
#ContextTypes提供上下文对象的类型注释，帮助在回调函数中访问上下文数据。这些上下文对象包含消息、用户、聊天等信息
#MessageHandler用于处理所有类型的消息（文本消息、照片、视频等），根据消息内容和过滤条件触发相应的回调函数
#ConversationHandler用于管理复杂的对话流程，允许在多个步骤之间维护对话状态。它支持处理一系列的消息和命令，并在不同状态之间切换
#CallbackQueryHandler用于处理由inline keyboard按钮触发的回调查询。当用户点击inline keyboard按钮时，Bot会接收到一个callback_query，该处理器负责处理这些回调查询。
# 定义广告检测函数
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
#两种监测信息的方式，一种是根据正则表达式的匹配，另一种是看关键词的出现次数
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

    # 踢人新接口
    await context.bot.ban_chat_member(chat_id, user_id)

    # Send a message to the group
    await update.message.reply_text(f"User {update.message.from_user.mention_html()} has been kicked for sending ads.", parse_mode='HTML')

def main() -> None:
    """Run the bot."""
    #初始化bot通用写法
    application = Application.builder().token(TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler('start', start))

    # on non-command messages - check for ads
    #& 是按位与操作符，用于将两个过滤器组合在一起。组合后的过滤器将捕捉所有文本消息，但排除命令消息
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_message))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
```

![image-20240806173403062](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240806173403062.png)

#### 消息转发/过滤

要使用 `python-telegram-bot` 库完成消息转发和过滤，你可以按照以下步骤进行：

---

示例代码

```python
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, CallbackContext

# 转发消息的函数
async def forward_message(update: Update, context: CallbackContext):
    target_chat_id = 'TARGET_CHAT_ID'  # 目标聊天 ID
    await update.message.forward(chat_id=target_chat_id)

# 主函数，设置机器人
def main():
    # 初始化应用
    app = ApplicationBuilder().token('YOUR_BOT_TOKEN').build()

    # 设置消息处理器，只转发文本消息
    text_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, forward_message)
    app.add_handler(text_handler)

    # 启动机器人
    app.run_polling()

if __name__ == '__main__':
    main()
```

详细解释

1. **初始化和配置机器人**：
   ```python
   app = ApplicationBuilder().token('YOUR_BOT_TOKEN').build()
   ```
   - 使用 `ApplicationBuilder` 配置机器人，并传入你的机器人令牌。

2. **处理消息**：
   ```python
   text_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, forward_message)
   app.add_handler(text_handler)
   ```
   - 使用 `MessageHandler` 创建一个消息处理器，只处理文本消息并排除命令。
   - 将处理器添加到应用程序中。

3. **转发消息**：
   ```python
   async def forward_message(update: Update, context: CallbackContext):
       target_chat_id = 'TARGET_CHAT_ID'
       await update.message.forward(chat_id=target_chat_id)
   ```
   - 定义一个异步函数 `forward_message`，将消息转发到目标聊天 ID。

4. **运行机器人**：
   ```python
   app.run_polling()
   ```
   - 使用 `run_polling` 方法启动机器人，以轮询模式接收消息。

通过这种方式，你可以创建一个简单的 Telegram 机器人，自动转发并过滤特定类型的消息。

---

### 前置知识

#### 关于一些比较流行的miniapp

游戏类bot居多，还包括一些工具类bot，比如群投票bot和支付工具相关bot,经过搜索后发现已有的mini app/bot和目前**群组内漂流瓶**这个想法重合度不高，比如说目前比较火热的这个项目本质上是炒作自家的虚拟货币的：

![image-20240806142257439](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240806142257439.png)

![image-20240806141137889](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240806141137889.png)

token：7356323008:AAF3mVrJSOyn4Hy7170E4Sp0vmFqoZwpl18

**参照示例代码和商店中的运行结果：**

聊天框左侧按钮：

![image-20240806112742187](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240806112742187.png)

#### 关于WebApp开发：css，html，JavaScript



---

#### 一些简单的示例代码



官网示例代码webappbot创建了一个简单的Telegram Bot，具备以下两个功能：

1. **响应`/example_color_picker`命令**：
   - 当用户向Bot发送`/start`命令时，Bot会回复一条消息“Welcome to radcan_test_bot!”。
2. **打开网页调色板并返回色号**

```python
import json
import logging
#前三者用于对webapp中inlinekeyboard的定义，展示和消除
from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, ConversationHandler,filters
TOKEN="7327334035:AAFn8lBKph9MYJSL5C6jtYV5vHFHvfBfi3A"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def example_color_picker(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message with a button that opens a the web app."""
    await update.message.reply_text(
        "Please press the button below to choose a color via the WebApp.",
        reply_markup=ReplyKeyboardMarkup.from_button(
            KeyboardButton(
                text="Open the color picker!",
                # WebAppInfo 是 telegram 模块中的一个类，用于定义 Telegram Web 应用（WebApp）的相关信息。
                # 它主要用于创建内联按钮，当用户点击按钮时，可以打开一个指定的 Web 应用
                # 这个url指的就是开发者自定义的WebApp,不使用云服务器的话就必须在本地搭建服务器
                web_app=WebAppInfo(url="https://python-telegram-bot.org/static/webappbot"),
            )
        ),
    )
#考虑换成其他app/编写自定义app
async def web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Print the received data and remove the button."""
    # Here we use `json.loads`, since the WebApp sends the data JSON serialized string
    # (see webappbot.html)
    data = json.loads(update.effective_message.web_app_data.data)
    await update.message.reply_html(
        text=(
            f"You selected the color with the HEX value <code>{data['hex']}</code>. The "
            f"corresponding RGB value is <code>{tuple(data['rgb'].values())}</code>."
        ),
        reply_markup=ReplyKeyboardRemove(),
    )


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("example_color_picker", example_color_picker))
    #StatusUpdate表示是一个“与状态更新相关的过滤器”
    #WEB_APP_DATA 是一个具体的过滤器，匹配来自 Web 应用的数据消息
    #web_app_data是一个回调函数，当消息满足过滤器条件时调用此函数。
    application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
```



**具体运行效果**

1. **启动Bot**：
   - 运行脚本后，Bot将开始轮询来自Telegram服务器的更新。

2. **用户交互**：

   - 用户向Bot发送`/start`命令：
     ```text
     /start
     ```
     - **Bot的回复**：
       ```text
       Please press the button below to choose a color via the WebApp
       ```

   - 用户选择调色板
     
   - ![image-20240806095812278](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240806095812278.png)
     
     - **Bot的回复**：
       
       ```text
       You selected the color with the HEX value #ff5a54. The corresponding RGB value is (255, 90, 84).
       ```

**逐步操作说明**

1. **创建并配置Bot**：
   - 使用`@BotFather`在Telegram中创建一个新的Bot并获取API Token。
2. **编写代码**：
3. **运行代码**：
4. **与Bot互动**：
   - 打开Telegram应用，找到你的Bot（通过你在`@BotFather`创建时获得的用户名）。
   - 向Bot发送/example_color_picker命令和文本消息，观察Bot的响应。



##### **注意事项**

- #### **API Token**：确保用你在`@BotFather`获取的实际API Token替换`"YOUR_API_TOKEN"`。
- **依赖安装**：确保已安装`python-telegram-bot`库，可以使用以下命令安装：
  
  ```bash
  pip install python-telegram-bot
  ```

通过这些步骤，你可以成功运行这个示例代码，并体验其功能。

为了在本地Windows电脑上搭建服务器并运行使用MySQL的漂流瓶Telegram Bot，你需要进行以下步骤：

#### 安装和配置MySQL

安装MySQL

1. **下载MySQL**：
   - 从MySQL官方网站下载MySQL安装包：https://dev.mysql.com/downloads/installer/
2. **安装MySQL**：
   - 按照安装向导进行安装，记住设置的root用户密码。
3. **配置MySQL**：
   - 使用MySQL Workbench或命令行客户端连接到MySQL服务器。

创建数据库和表

使用MySQL Workbench或命令行客户端创建数据库和表：

```sql
CREATE DATABASE drift_bottle_db;
USE drift_bottle_db;

CREATE TABLE IF NOT EXISTS bottles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT,
    message TEXT,
    photo LONGBLOB
);

CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY
);
```

2. 设置Python开发环境

安装Python

1. **下载Python**：
   - 从Python官方网站下载Python：https://www.python.org/downloads/
2. **安装Python**：
   - 安装Python时，确保选中“Add Python to PATH”选项。

创建虚拟环境

1. **创建虚拟环境**：
   ```bash
   python -m venv venv
   ```
2. **激活虚拟环境**：
   - 对于Windows：
     ```bash
     venv\Scripts\activate
     ```

安装依赖包

1. **安装依赖包**：
   ```bash
   pip install python-telegram-bot mysql-connector-python
   ```

3. 修改代码

在代码中，确保MySQL数据库连接配置正确：

```python
# MySQL database connection
db_config = {
    'user': 'your_mysql_user',  # MySQL用户名
    'password': 'your_mysql_password',  # MySQL密码
    'host': 'localhost',  # 数据库服务器地址
    'database': 'drift_bottle_db'  # 数据库名称
}
```

4. 运行Bot

确保所有依赖安装完成并配置正确后，运行Bot：

```bash
python your_bot_script.py
```

总结

1. **安装和配置MySQL**：下载并安装MySQL，创建漂流瓶相关的数据库和表。
2. **设置Python开发环境**：安装Python，创建和激活虚拟环境，安装所需的依赖包。
3. **修改代码**：确保代码中的MySQL配置正确。
4. **运行Bot**：在虚拟环境中运行你的Bot脚本。

通过这些步骤，你可以在本地Windows电脑上搭建并运行使用MySQL的漂流瓶Telegram Bot。

---



### 关于TMA

#### [什么是小程序-文档/开发者社区/小程序SDK/与TON Connect集成](https://docs.ton.org/mandarin/develop/dapps/telegram-apps/)

---

### 第三方库中elegram bot api纯python接口

![image-20240805172836801](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240805172836801.png)

https://github.com/python-telegram-bot/python-telegram-bot?tab=readme-ov-file#working-with-ptb

api简介

https://github.com/python-telegram-bot/python-telegram-bot/wiki/Introduction-to-the-API

除此之外，使用接口前须先熟悉词汇表

[函数的详细使用说明](https://docs.python-telegram-bot.org/en/stable/telegram.bot.html)

---

### Telegram Bot 和 Mini App 的区别与联系

#### **Telegram Bot**

**定义**：

- Telegram Bot 是一种自动化程序，可以通过 Telegram 的 Bot API 与用户进行交互。这些机器人可以处理消息、命令、回调查询、内联查询等。

**功能**：
- **消息处理**：可以接收和发送消息、照片、文件等。
- **命令处理**：可以处理用户输入的命令，例如 `/start`、`/help` 等。
- **回调查询**：处理用户点击内联键盘按钮后的回调事件。
- **定时任务**：通过 JobQueue 设置定时任务。
- **Webhook**：可以配置为使用 Webhook 方式接收更新。

**使用场景**：
- **客户服务**：自动回复常见问题。
- **通知系统**：发送重要通知或警报。
- **游戏**：提供基于文本的游戏体验。
- **支付**：集成支付功能，处理订单和付款。

**Mini App**

**定义**：
- Telegram Mini Apps 是通过 Telegram 内置的 Web App Platform 提供的，允许开发者创建交互式的网页应用，这些应用可以嵌入到 Telegram 聊天中，并与用户的聊天环境无缝集成。

**功能**：
- **交互式界面**：可以创建复杂的用户界面，支持 JavaScript、HTML 和 CSS。
- **深度集成**：与 Telegram 的消息和界面深度集成，可以直接在聊天中使用。
- **用户数据**：通过 `tg-webapp` JavaScript 库，可以访问用户的基本信息和聊天环境。
- **支付和订阅**：可以集成支付系统，处理订阅和购买。

**使用场景**：
- **复杂应用**：如预订系统、在线商店、互动游戏等。
- **增强聊天体验**：通过嵌入式应用提供丰富的互动体验。
- **数据展示**：显示复杂的统计数据、图表和报告。

**联系**

1. **平台和用户基础**：
    - 两者都运行在 Telegram 平台上，并可以利用其庞大的用户基础。
    - 都可以无缝集成到用户的聊天体验中，提供增值服务。

2. **开发者生态**：
    - 开发者可以同时使用 Bot API 和 Web App Platform 来构建功能强大的应用。
    - 可以组合使用，机器人负责后台逻辑处理，Mini App 提供前端交互界面。

3. **交互和通知**：
    - 机器人可以用于通知和消息处理，而 Mini App 则可以用于提供复杂的交互和展示。
    - 机器人可以触发 Mini App，Mini App 可以通过机器人发送消息或更新。

### 

- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Telegram Web Apps](https://core.telegram.org/bots/webapps)

通过合理结合 Telegram Bot 和 Mini App 的功能，可以创建功能强大且用户体验优良的应用。