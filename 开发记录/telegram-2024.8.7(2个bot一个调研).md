# 第一周任务

[TOC]

## 2024.8.6

主要任务为探索telegram的bot和小程序,从father_bot这里申请bot

主要参考示例代码

### 已知可靠信息

- [Telegram Bot API 文档](https://core.telegram.org/bots/api)
- [python-telegram-bot 文档](https://python-telegram-bot.readthedocs.io/en/stable/),[函数的详细使用说明](https://docs.python-telegram-bot.org/en/stable/telegram.bot.html)，`telegram` 模块是底层 API 的直接封装，而 `telegram.ext` 提供了更高层次的功能
- [词汇表](https://core.telegram.org/tdlib/getting-started)

### 关于bots

小程序的功能和群组管理的功能可以同时集成到同一个bot里面

---

#### 关于申请bot/自定义bot的功能

**use this token to access the http api:**

7327334035:AAFn8lBKph9MYJSL5C6jtYV5vHFHvfBfi3A

### 初步的一些想法/想要实现的功能



#### ~~1.漂流瓶~~

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

#### 3.消息转发/过滤

```python
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
```

实现效果：

src_chat:

![image-20240807103911254](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240807103911254.png)

target_chat:

![image-20240807105529576](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240807105529576.png)

#### 4.bot伪装

主要是模仿人类用户的行为和活动

1. **延迟响应**：添加随机延迟以模拟人类打字时间。
2. **随机化消息**：使用多个消息模板随机选择回复，增加对话的自然性。
3. **文本处理**：使用正则表达式和文本分析提高对话的灵活性。

目前找到的论文主要都是关于机器人检测的，对bot伪装这方面的内容也很少

现有的Twitter机器人检测方法主要分为三类：基于特征的、基于文本的和基于图的

**目前bot伪装的关键是使机器人的行动看起来更像人类用户**：

- 新型机器人越来越多地**从真实用户那里窃取文本内容**，这种方式在2024.5月的一篇论文内被定义为“传统方法无法检测的新型bot”[链接](chrome-extension://efaidnbmnnnibpcajpcglclefindmkaj/https://arxiv.org/pdf/2405.11225)

- 机器人通过模仿人类用户的行为和活动来伪装自己，尤其是在重大事件期间，如选举前的社交媒体活动

- 机器人通过冒名顶替真实用户，特别是在社交媒体平台上，利用与真实用户相似的资料和行为来伪装自己

- 增加和真实用户的互动，"现有的基于图的 Twitter 机器人检测方法达到了当前最佳性能，但它们都基于同质性假设，即认为具有相同标签的用户更有可能相互关注/成为好友，这**使得 Twitter 机器人可以通过follow关注大量真实用户来伪装自己"**

- 2023.6提出的HOFA框架假设机器人窃取的文本全部来自于它关注的用户，并基于这一点提出了更高的机器人检测方法，所以我**推测消息转发可以用来帮助伪装bot获取真实用户发送的信息**，参考文献：**[HOFA: Twitter Bot Detection with Homophily-Oriented Augmentation and Frequency Adaptive Attention](https://dx.doi.org/10.48550/arXiv.2306.12870)** 

- 动态行为和快速变化：如果一个机器人发现某种行为模式容易被检测到，它可以改变其行为以逃避检测：[2023.4论文链接](chrome-extension://efaidnbmnnnibpcajpcglclefindmkaj/https://arxiv.org/pdf/2304.06280)

  

  

---

要获取有关bot伪装（或bot欺骗）方面的资料，可以访问以下几类网站：

1. **技术和安全博客**：许多技术博客和安全博客会讨论bot伪装的技术和策略。例如：
   - [Krebs on Security](https://krebsonsecurity.com)
   - [Threatpost](https://threatpost.com)
   - [Dark Reading](https://www.darkreading.com)

2. **网络安全公司**：很多网络安全公司会发布有关bot伪装的白皮书、研究报告和博客文章。例如：
   - [Cloudflare](https://www.cloudflare.com/learning/ddos/bots/)
   - [Imperva](https://www.imperva.com/learn/application-security/bots/)
   - [Akamai](https://www.akamai.com/us/en/solutions/security/bot-management/)

3. **学术资源**：可以查阅学术论文和研究，以获取有关bot伪装的深入分析。例如：
   - [Google Scholar](https://scholar.google.com)
   - [IEEE Xplore](https://ieeexplore.ieee.org)
   - [arXiv](https://arxiv.org)

4. **网络安全社区和论坛**：这些平台上常常会讨论各种安全话题，包括bot伪装。
   - [Stack Exchange (Information Security)](https://security.stackexchange.com)
   - [Reddit (r/netsec)](https://www.reddit.com/r/netsec/)

这些资源可以帮助你深入了解bot伪装的技术细节和防御策略。

以下是一些最近的资料和资源，涉及bot伪装和相关主题：

1. **《The Anatomy of a Botnet: A Detailed Analysis of the World's Largest Botnet》**  
   - 这篇文章深入分析了大型botnet的结构和伪装技术。  
   - [阅读链接](https://www.darkreading.com/perimeter-security/the-anatomy-of-a-botnet-a-detailed-analysis-of-the-worlds-largest-botnet/d/d-id/1330811)

2. **《2024 State of Bot Mitigation Report》**  
   - 由企业发布的最新报告，涵盖了bot伪装的现状及防御技术。  
   - [阅读链接](https://www.imperva.com/resources/state-of-bot-mitigation-report-2024/)

3. **《Bot Management: The Complete Guide》**  
   - 介绍了bot管理的各个方面，包括伪装技术和检测方法。  
   - [阅读链接](https://www.cloudflare.com/learning/bots/bot-management/)

4. **《Evolving Bot Threats and Countermeasures》**  
   - 研究了最新的bot威胁及其对策。  
   - [阅读链接](https://www.akamai.com/us/en/resources/evolving-bot-threats-and-countermeasures.jsp)

5. **《How Bots Are Evolving and How to Stay Ahead of Them》**  
   - 探讨了bot技术的发展及其对策。  
   - [阅读链接](https://www.threatpost.com/how-bots-are-evolving-and-how-to-stay-ahead-of-them/)

这些资源提供了有关bot伪装和检测的最新信息和技术。

