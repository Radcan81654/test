# 第一周任务



[TOC]





## 2024.8.5

主要任务为探索telegram的bot和小程序,从father_bot这里申请bot

目标是弄清全部的说明文档和示例代码

### 前置知识

#### import asyncio

---

#### import telegram

---



#### 关于Web开发：css，html，JavaScript



---



### 关于bots

小程序的功能和群组管理的功能可以同时集成到同一个bot里面

---

#### 关于申请bot/自定义bot的功能

**use this token to access the http api:**

7327334035:AAFn8lBKph9MYJSL5C6jtYV5vHFHvfBfi3A

##### 简单示例

创建了一个名为`radcan_test_bot`的Telegram Bot后，你可以通过编程为它添加各种功能。以下是一些常见且实用的功能示例：

1. **自动回复**：
   - 你可以编写代码让Bot根据关键词或特定命令自动回复用户消息。例如，用户输入`/start`时，Bot可以发送欢迎信息。

2. **信息推送**：
   - 你的Bot可以定时或实时推送信息给用户，比如新闻更新、天气预报、股市行情等。

3. **管理群组**：
   - Bot可以用来管理群组，例如自动踢出违规用户、设置群规、自动回答常见问题等。

4. **任务提醒**：
   - 提供待办事项或任务提醒功能，用户可以通过Bot设置提醒时间，Bot会在指定时间发送提醒信息。

5. **信息查询**：
   - 实现各种信息查询功能，比如查询天气、翻译文字、搜索电影信息等。

6. **互动小游戏**：
   - 你可以开发一些简单的互动小游戏，例如猜谜、数学题等，让用户在聊天时可以娱乐一下。

7. **文件处理**：
   - Bot可以帮助用户处理文件，例如将图片转换为PDF、压缩文件、翻译文档等。

8. **用户反馈**：
   - 收集用户反馈和意见，Bot可以记录用户输入的反馈信息并发送到你的邮箱或存储在数据库中。

9. **集成第三方服务**：
   - 你可以将Bot与其他API或服务集成，例如连接到你的CRM系统、数据库、支付平台等，实现更多复杂的功能。

**实现这些功能的基础步骤：**

1. **创建并配置Bot**：
   - 使用`@BotFather`创建Bot并获取API Token。

2. **编写代码**：
   - 使用Python（推荐使用`python-telegram-bot`库）、Node.js、Go等编程语言编写Bot逻辑。

3. **部署和运行**：
   - 将你的代码部署到服务器上并保持运行，可以使用Heroku、AWS、VPS等平台。

**示例代码（Python）：**

```python
#Update: 代表从Telegram服务器收到的更新（消息、命令等）。
#Updater: 用于与Telegram服务器进行通信，并管理更新的处理。
#CommandHandler: 处理命令消息（例如/start）。
#MessageHandler: 处理普通消息（例如用户发送的文本消息）。
#Filters: 用于过滤特定类型的消息。
#CallbackContext: 提供回调函数所需的上下文信息
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# 定义/start命令处理函数
#update: Update这种写法是类型注解的一部分。它用来指明函数参数update的类型是Update
#这里的“->Node”表示这个函数不返回任何值
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Welcome to radcan_test_bot!')

# 定义文本消息处理函数
def echo(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(update.message.text)

def main() -> None:
    # 创建Updater并传入Bot的API Token
    updater = Updater("YOUR_API_TOKEN")

    # 获取调度器以注册处理程序
    dispatcher = updater.dispatcher

    # 注册/start命令的处理函数
    dispatcher.add_handler(CommandHandler("start", start))

    # 注册文本消息处理函数
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # 启动Bot
    updater.start_polling()

    # 运行直到按Ctrl-C
    updater.idle()

if __name__ == '__main__':
    main()
```



这段示例代码创建了一个简单的Telegram Bot，具备以下两个功能：

1. **响应`/start`命令**：
   - 当用户向Bot发送`/start`命令时，Bot会回复一条消息“Welcome to radcan_test_bot!”。
   
2. **回显用户发送的文本消息**：
   - 当用户发送任何文本消息时，Bot会将该消息原样回复给用户。

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
       Welcome to radcan_test_bot!
       ```

   - 用户发送普通文本消息：
     ```text
     Hello, Bot!
     ```
     - **Bot的回复**：
       ```text
       Hello, Bot!
       ```

**逐步操作说明**

1. **创建并配置Bot**：
   - 使用`@BotFather`在Telegram中创建一个新的Bot并获取API Token。

2. **编写代码**：
   - 将示例代码保存为Python脚本，例如`bot.py`。

3. **运行代码**：
   - 在命令行或终端中运行脚本：
     ```bash
     python bot.py
     ```

4. **与Bot互动**：
   - 打开Telegram应用，找到你的Bot（通过你在`@BotFather`创建时获得的用户名）。
   - 向Bot发送`/start`命令和文本消息，观察Bot的响应。



##### 注意事项

- **API Token**：确保用你在`@BotFather`获取的实际API Token替换`"YOUR_API_TOKEN"`。
- **依赖安装**：确保已安装`python-telegram-bot`库，可以使用以下命令安装：
  
  ```bash
  pip install python-telegram-bot
  ```

通过这些步骤，你可以成功运行这个示例代码，并体验其功能。

---



**资源和学习资料：**

- [Telegram Bot API 文档](https://core.telegram.org/bots/api)
- [python-telegram-bot 文档](https://python-telegram-bot.readthedocs.io/en/stable/)
- [Creating a Telegram Bot using Python](https://medium.com/swlh/creating-a-telegram-bot-using-python-5d174f95c6e6)

通过不断迭代和扩展，可以将你的`radcan_test_bot`变成一个功能强大、用途广泛的Bot，满足不同用户的需求。

---

#### 

---

### 关于TMA

#### [什么是小程序-文档/开发者社区/小程序SDK/与TON Connect集成](https://docs.ton.org/mandarin/develop/dapps/telegram-apps/)

---

### t第三方库中elegram bot api纯python接口

![image-20240805172836801](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240805172836801.png)

https://github.com/python-telegram-bot/python-telegram-bot?tab=readme-ov-file#working-with-ptb

api简介

https://github.com/python-telegram-bot/python-telegram-bot/wiki/Introduction-to-the-API

除此之外，使用接口前须先熟悉词汇表

[函数的详细使用说明](https://docs.python-telegram-bot.org/en/stable/telegram.bot.html)

---

#### 相比PTA的优势

在 `python-telegram-bot` 库中，相较于直接使用纯 Telegram API，有许多函数和类显著提高了开发效率和便利性。以下是一些使用起来更方便的函数和类，以及它们的主要功能和用法示例：

##### 1. `Updater`
- 作用：管理与 Telegram 服务器的连接，并处理消息和命令。
- 示例：

    ```python
    from telegram.ext import Updater
    # 创建一个Updater对象，并使用Telegram Bot API的Token进行初始化
    updater = Updater('YOUR TOKEN', use_context=True)
    # 开始轮询以获取来自Telegram服务器的新消息
    updater.start_polling()
    # 使得程序一直运行，直到手动停止它
    updater.idle()
    ```

##### 2. `Dispatcher`
- 作用：注册消息处理器（handlers）并分发消息。
- 示例：

    ```python
    # 从Updater对象中获取Dispatcher，用于注册消息处理器
    dp = updater.dispatcher
    ```

##### 3. `CommandHandler`
- 作用：处理特定命令消息。
- 示例：

    ```python
    from telegram.ext import CommandHandler
    # 定义一个处理函数，用于处理/start命令
    def start(update, context):
        update.message.reply_text('Hello!')
    # 向Dispatcher添加一个CommandHandler，用于处理/start命令
    dp.add_handler(CommandHandler("start", start))
    ```

##### 4. `MessageHandler`
- 作用：处理非命令消息，根据过滤条件进行处理。

- 示例：

    ```python
    from telegram.ext import MessageHandler, Filters
    # 定义一个名为echo的处理函数，当机器人收到文本消息时，该函数将被调用
    #参数 update 包含所有与消息有关的数据（例如，消息内容、发送者信息等）。
    #参数 context 提供一些有用的上下文数据和辅助函数。
    #函数体中，使用 update 对象的 message 属性获取用户发送的消息，并使用 reply_text 方法回显相同的#文本给用户。
    def echo(update, context):
        # 使用update对象的message属性获取用户发送的消息，并回显相同的文本
        update.message.reply_text(update.message.text)
    # 创建一个MessageHandler对象，用于处理所有的文本消息
    # Filters.text是一个过滤器，只允许文本消息通过该处理器
    #echo 是消息处理函数，当有符合过滤条件的消息时，该函数将被调用。
    #使用 dp.add_handler 方法将 MessageHandler 添加到调度器 dp，使其开始处理消息。
    dp.add_handler(MessageHandler(Filters.text, echo))
    ```

##### 5. `JobQueue` 和 `Job`



- 作用：调度定时任务。
- 示例：

    ```python
    from telegram.ext import JobQueue
    #定义一个名为 callback_alarm 的函数，这是一个定时任务的回调函数。
    #参数 context 提供一些有用的上下文数据和辅助函数。
    #函数体中，使用 context 对象的 bot 属性发送一条消息到指定的聊天ID（由 context.job.context 提供），内容为 "Alarm!"。
    def callback_alarm(context):
        context.bot.send_message(chat_id=context.job.context, text='Alarm!')
    
    jq = updater.job_queue
    #使用 JobQueue 的 run_once 方法添加一个一次性任务。
    #callback_alarm 是任务触发时调用的回调函数。
    #when=10 表示任务将在10秒后执行。
    #context=chat_id 是传递给回调函数的上下文数据，这里是聊天ID
    #jq.run_once(callback_alarm, when=10, context=chat_id)
    ```

##### 6. `CallbackQueryHandler`

[关于回调函数](https://zh.wikipedia.org/wiki/%E5%9B%9E%E8%B0%83%E5%87%BD%E6%95%B0)

**回调查询 (Callback Query)**

**回调查询** 是指用户在 Telegram 机器人中点击了内联键盘（Inline Keyboard）上的按钮之后，机器人收到的一种特殊类型的更新（update）。与常规的消息不同，回调查询并不会像普通文本消息那样发送文本到聊天窗口，而是将点击的事件传递给机器人，以便机器人可以根据用户的操作进行相应的处理。

**回调查询对象 (Callback Query Object)**

**回调查询对象** 是指包含回调查询相关信息的对象。当用户点击内联键盘上的按钮时，Telegram 服务器会生成一个回调查询对象，并将其发送给机器人。这个对象包含了有关回调查询的详细信息，例如用户点击了哪个按钮、用户信息、消息信息等。

回调查询对象的主要属性包括：

- `id`：回调查询的唯一标识符。
- `from`：发起回调查询的用户。
- `message`：包含内联键盘的消息（如果有）。
- `inline_message_id`：内联消息的唯一标识符（如果有）。
- `chat_instance`：唯一标识该回调查询和消息的聊天实例。
- `data`：按钮的回调数据。
- `game_short_name`：按钮的游戏短名称（如果有）

- 作用：处理回调查询（例如来自内联按钮的回调）。
- 示例：

    ```python
    from telegram.ext import CallbackQueryHandler
    # 定义一个处理函数，当收到回调查询时，该函数将被调用
    def button(update, context):
        # 获取回调查询对象
        query = update.callback_query
        # 发送确认响应以关闭加载状态这会告诉 Telegram 服务器，机器人已经成功处理了这个回调查询，并可以关闭加载状态（通常是在按钮点击后显示的旋转加载图标）
        query.answer()
        #使用 query.edit_message_text 方法编辑原始消息的内容，显示用户选择的选项，query.data 包含了用户点击按钮时传递的回调数据，这里将其格式化为一条消息，告诉用户他们选择了什么
        query.edit_message_text(text="Selected option: {}".format(query.data))
    # 创建一个 CallbackQueryHandler 对象，指定处理函数 button使用 dp.add_handler 方法将 CallbackQueryHandler 添加到调度器 dp，使其能够处理回调查询事件。
    dp.add_handler(CallbackQueryHandler(button))
    ```

##### 7. `ConversationHandler`(重点)
- 作用：包含多个会话状态和群组成员发送广告时将其移出群组的功能
- 示例：

    ```python
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
    from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext
    
    # 定义对话状态,状态是可以自定义的，重点在于写出判断这个状态的函数
    #CHOOSING 状态表示用户正在进行选择的阶段。在这个阶段，机器人会提供一些选项供用户选择，以决定接下来的对话方向
    #TYPING_REPLY 状态表示用户正在输入回复的阶段。在这个阶段，用户可以输入文本回复，机器人会根据用户的输入执行相应的操作
    #TYPING_AD 状态表示检测广告信息的阶段。在这个阶段，机器人会监控用户发送的消息，检查是否包含广告关键词
    CHOOSING, TYPING_REPLY, TYPING_AD = range(3)
    
    
    # 定义开始对话的处理函数
    def start(update: Update, context: CallbackContext) -> int:
        #update.message.reply_text 方法用于向用户发送文本消息
        update.message.reply_text(
            #"Hi! What do you want to know about?" 是发送给用户的欢迎消息
            #reply_markup 参数用于添加内联键盘
            "Hi! What do you want to know about?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Option 1", callback_data='1')],
                [InlineKeyboardButton("Option 2", callback_data='2')]
            ])
        )
        return CHOOSING
    
    # 定义处理选择的函数
    def received_information(update: Update, context: CallbackContext) -> int:
        #update.callback_query 包含了用户点击内联键盘按钮后传递的所有信息，例如用户点击了哪个按钮、回调数据等
        query = update.callback_query
        #query.answer() 方法用于发送一个确认响应，告诉 Telegram 服务器机器人已经成功处理了这个回调查询，这会关闭按钮点击后的加载状态，向用户确认他们的操作已被处理
        query.answer()
        #query.edit_message_text 方法用于编辑原始消息的内容，text=f"Selected option: {query.data}" 表示将消息内容更新为显示用户选择的选项，其中 query.data 包含用户点击按钮时传递的回调数据。
        query.edit_message_text(text=f"Selected option: {query.data}")
        return TYPING_REPLY
    
    # 定义处理广告信息的函数
    # 最好使用正则表达式
    # 最好结合多个关键词
    # 最好考虑上下文
    def detect_ad(update: Update, context: CallbackContext) -> int:
    	message_text = update.message.text.lower()
        # 定义更复杂的广告关键词和模式
        AD_PATTERNS = [
            r'\b(buy\s+now|limited\s+offer|exclusive\s+discount)\b',
            r'\b(promo|promotion|special\s+offer|sale)\b',
            r'\b(discount|deal|free\s+shipping|act\s+now)\b'
        ]
        # 定义更复杂的广告关键词
        AD_KEYWORDS = ['buy', 'discount', 'offer', 'promo', 'sale', 'free']
        # 正则表达式检测广告模式
        for pattern in AD_PATTERNS:
            #re模块提供了正则表达式操作工具
            if re.search(pattern, message_text):
                context.bot.kick_chat_member(update.message.chat.id, update.message.from_user.id)
                update.message.reply_text("You have been removed from the group for sending advertisements.")
                return ConversationHandler.END
        # 多个关键词组合检测
        # message_text.count(keyword) 方法用于统计 keyword 在 message_text 中出现的次数
        # 例如，如果 message_text 为 "buy now and get a discount on your purchase", keyword 为 "buy"，则 message_text.count("buy") 返回 1。
        #等同于以下写法：
        #keyword_count = 0
        #for keyword in AD_KEYWORDS:
        #	keyword_count += message_text.count(keyword)
        keyword_count = sum(message_text.count(keyword) for keyword in AD_KEYWORDS)
        if keyword_count >= 3:  # 阈值可以根据需求调整
            context.bot.kick_chat_member(update.message.chat.id, update.message.from_user.id)
            update.message.reply_text("You have been removed from the group for sending advertisements.")
            return ConversationHandler.END
        return TYPING_AD
    
    # 定义接收信息的处理函数
    def received_reply(update: Update, context: CallbackContext) -> int:
        update.message.reply_text("Thank you for your reply!")
        return ConversationHandler.END
    
    # 定义取消对话的处理函数
    def cancel(update: Update, context: CallbackContext) -> int:
        update.message.reply_text("Conversation canceled.")
        return ConversationHandler.END
    
    def main() -> None:
        # 创建Updater对象，并使用Token进行初始化
        updater = Updater("YOUR TOKEN", use_context=True)
    
        # 从Updater对象中获取Dispatcher
        dp = updater.dispatcher
    
        # 定义一个ConversationHandler，用于管理复杂对话
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start)],  # 入口点
            states={
                CHOOSING: [CallbackQueryHandler(received_information)],  # 选择状态和处理器
                TYPING_REPLY: [MessageHandler(Filters.text & ~Filters.command, received_reply)],  # 回复状态和处理器
                TYPING_AD: [MessageHandler(Filters.text & ~Filters.command, detect_ad)],  # 广告状态和处理器
            },
            fallbacks=[CommandHandler('cancel', cancel)]  # 回退处理器
        )
    
        # 向Dispatcher添加ConversationHandler
        dp.add_handler(conv_handler)
    
        # 启动轮询以获取来自Telegram服务器的新消息
        updater.start_polling()
    
        # 使得程序一直运行，直到手动停止它
        updater.idle()
    
    if __name__ == '__main__':
        main()
    
    ```

##### 8. `InlineQueryHandler`
- 作用：处理内联查询。
- 示例：

    ```python
    from telegram import InlineQueryResultArticle, InputTextMessageContent
    from telegram.ext import InlineQueryHandler
    
    def inlinequery(update, context):
        query = update.inline_query.query
        results = [
            InlineQueryResultArticle(
                id=query.upper(),
                title='Caps',
                input_message_content=InputTextMessageContent(query.upper())
            )
        ]
        update.inline_query.answer(results)
    
    dp.add_handler(InlineQueryHandler(inlinequery))
    ```

##### 9. `Filters`(已经被移除)
- 作用：预定义过滤器，用于简化消息过滤。
- 示例：

    ```python
    # 向Dispatcher添加MessageHandler，处理照片消息
    dp.add_handler(MessageHandler(Filters.photo, photo_handler))
    # 向Dispatcher添加MessageHandler，处理特定MIME类型的文档
    dp.add_handler(MessageHandler(Filters.document.mime_type("image/jpeg"), document_handler))
    ```

##### 10. `ExtBot`
- 作用：提供更多的 Telegram API 功能，如 `send_message`、`send_photo` 等。
- 示例：

    ```python
    #进行这一步之前需要先把bot和相关的chatid准备好
    from telegram import Bot
    # 使用Token创建一个Bot对象
    bot = Bot(token='YOUR TOKEN')
    
    # 使用Bot对象发送消息
    bot.send_message(chat_id='CHAT_ID', text='Hello World')
    ```

通过这些高层次的封装和便利的函数，`python-telegram-bot` 库极大地简化了开发 Telegram 机器人的流程，使得开发者能够更高效地实现功能并处理各种消息和事件。



### bot和mini app的区别和联系

### Telegram Bot 和 Mini App 的区别与联系

#### Telegram Bot

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

#### Mini App

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

**示例**

**结合使用**：

- 一个旅游预订系统：用户可以通过机器人查询旅行信息，机器人提供基础信息后，可以打开一个 Mini App，用户在 Mini App 中选择具体的旅行套餐并完成预订。

### 参考资料

- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Telegram Web Apps](https://core.telegram.org/bots/webapps)

通过合理结合 Telegram Bot 和 Mini App 的功能，可以创建功能强大且用户体验优良的应用。