# 第2周任务

[TOC]

## 2024.8.9

主要任务为完成文件下载bot，熟悉aria2p类

### 已知可靠信息

- [Telegram Bot API 文档](https://core.telegram.org/bots/api)
- [python-telegram-bot 文档](https://docs.python-telegram-bot.org/en/stable/inclusions/bot_methods.html),[函数的详细使用说明](https://docs.python-telegram-bot.org/en/stable/telegram.bot.html)，`telegram` 模块是底层 API 的直接封装，而 `telegram.ext` 提供了更高层次的功能
- [telegram词汇表](https://core.telegram.org/tdlib/getting-started)
- [aria2p说明文档链接](https://pawamoy.github.io/aria2p/reference/aria2p/)
- [pandasql说明文档](https://github.com/yhat/pandasql)
- **use this token to access the http api:**7327334035:AAFn8lBKph9MYJSL5C6jtYV5vHFHvfBfi3A
- ~~在阿里云服务器上运行clash的脚本，只需要修改环境变量：https://github.com/wnlen/clash-for-linux~~

---





### 关于aria2p

由于aria2p已经优化了内存消耗磁盘消耗，我们不需要手动"节约磁盘空间","控制消耗内存",这些方面就可以先不去了解

Client用于最开始的初始化

![image-20240809093531835](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240809093531835.png)

```python
#aria2p.client.Client
Client(
    host: str = DEFAULT_HOST,####chatgpt的示例代码这里写错了
    port: int = DEFAULT_PORT,
    secret: str = "",
    timeout: float = DEFAULT_TIMEOUT,
)
#aria2p.client methods:
add_metalink – Add a Metalink download.
add_torrent – Add a BitTorrent download.######下载".torrent" file
add_uri – Add a new download.########把一个链接添加到下载队列
change_global_option – Change the global options dynamically.
change_uri – Remove the URIs in del_uris from and appends the URIs in add_uris to download denoted by gid.
force_pause – Force pause a download.
force_pause_all – Force pause all active/waiting downloads.
force_remove – Force remove a download.
force_shutdown – Force shutdown aria2.
get_files – Return file list of a download.###########################
get_global_option – Return the global options.
get_global_stat – Return global statistics such as the overall download and upload speeds.
get_option – Return options of a download.
get_params – Build the list of parameters.
get_payload – Build a payload.
get_peers – Return peers list of a download.
get_servers – Return servers currently connected for a download.
get_session_info – Return session information.
get_uris – Return URIs used in a download.#########查看哪些url下载过文件了
get_version – Return aria2 version and the list of enabled features.
list_methods – Return the available RPC methods.
list_notifications – Return all the available RPC notifications.
listen_to_notifications – Start listening to aria2 notifications via WebSocket.
multicall – Call multiple methods in a single request.
multicall2 – Call multiple methods in one request.
post – Send a POST request to the server
res_or_raise – Return the result of the response, or raise an error with code and message.
response_as_exception – Transform the response as a ClientException instance and return it.
save_session – Save the current session to a file.
stop_listening – Stop listening to notifications..
tell_status – Tell status of a download.#####################

```

API类则需要Client类进行初始化

![image-20240809093547151](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240809093547151.png)

```python
API(client: Client | None = None)
add – Add a download (guess its type).########不仅可以处理URI，还可以处理磁力链接和种子文件
add_magnet – Add a download with a Magnet URI.
add_metalink – Add a download with a Metalink file.
add_torrent – Add a download with a torrent file (usually .torrent extension).
add_uris – Add a download with a URL (or more).
autopurge – Purge completed, removed or failed downloads from the queue.
copy_files – Copy downloaded files to another directory.
get_download – Get a Download object thanks to its GID.################
get_downloads – Get a list of Download object thanks to their GIDs.
get_global_options – Get the global options.
get_options – Get options for each of the given downloads.
get_stats – Get the stats of the remote aria2c process.
listen_to_notifications – Start listening to aria2 notifications via WebSocket.
move – Move a download in the queue, relatively to its current position.
move_down – Move a download down in the queue.
move_files – Move downloaded files to another directory.
move_to – Move a download in the queue, with absolute positioning.
move_to_bottom – Move a download to the bottom of the queue.
move_to_top – Move a download to the top of the queue.
move_up – Move a download up in the queue.
parse_input_file – Parse a file with URIs or an aria2c input file.
remove – Remove the given downloads from the list.
remove_all – Remove all downloads from the list.
remove_files – Remove downloaded files.
resume – Resume (unpause) the given downloads.
resume_all – Resume (unpause) all downloads.
retry_downloads – Resume failed downloads from where they left off with new GIDs.
search – Not implemented.
set_global_options – Set global options.
set_options – Set options for specific downloads.
split_input_file – Helper to split downloads in an input file.
stop_listening – Stop listening to notifications.
```

关于api类中add函数的返回值download类：

![image-20240809125238996](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240809125238996.png)





![image-20240809123244139](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240809123244139.png)





2024.8.9 14:15已经完成了下载文件部分的代码：

发现即使安装了梯子，下载有时也会出现错误，所以考虑加入一个下载时间限制，或者优化一下逻辑，避免资源浪费

![image-20240809141542642](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240809141542642.png)





---

## 环境搭建

### 关于虚拟环境

要在一个单独的虚拟环境中运行上述Python代码，可以按照以下步骤操作：

1. **创建虚拟环境**

首先，在您的项目目录下创建一个虚拟环境。

```bash
python3 -m venv myenv
```

`myenv` 是虚拟环境的名称，您可以更改为您喜欢的名称。

**2. 激活虚拟环境**

创建虚拟环境后，您需要激活它。

- **在Linux或macOS上**，运行以下命令：

  ```bash
  source py39_env/bin/activate
  ```

  只要激活了环境，无论是否进入主目录，程序都是在虚拟环境中运行的，怎么折腾都不会影响主环境，下次激活的时候之前在这个虚拟环境中做出的改动也会被重新加载


激活虚拟环境后，您的终端提示符会发生变化，表示您现在处于该虚拟环境中。

**3. 升级Python版本（如果需要）**

如果您的系统默认的Python版本低于3.7，您需要确保使用Python 3.7或更高版本来创建虚拟环境。您可以通过以下方式指定Python版本（假设已经安装了Python 3.7）：

```bash
python3.7 -m venv myenv
```

**4. 安装所需的Python模块**

激活虚拟环境后，您可以使用 `pip` 来安装所需的Python模块。

```bash
pip install aria2p python-telegram-bot
```

**5. 运行您的Python代码**

确保您已经激活了虚拟环境，然后运行您的Python代码。

```bash
python your_script.py
```

`your_script.py` 是您的Python脚本的名称。

**6. 退出虚拟环境**

完成工作后，您可以通过以下命令退出虚拟环境：

```bash
deactivate
```

这样，您就可以在一个单独的虚拟环境中运行您的Python代码了。

### **通过安装管理脚本一键安装aria2**

https://github.com/P3TERX/aria2.sh

![image-20240808175313989](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240808175313989.png)

![image-20240808175440562](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240808175440562.png)

### 自己下载原始版本aria2p

当然，这里是手动下载并安装Docker RPM包的步骤和下载链接。

**手动下载并安装Docker RPM包**

1. **访问Docker RPM包下载页面**：
   访问以下链接找到适合你系统的RPM包：
   - [Docker CE RPM包下载页面](https://download.docker.com/linux/centos/7/x86_64/stable/Packages/)

2. **下载所需的RPM包**：
   你需要下载以下三个文件（确保选择最新版本,下面的只是例子）：

   - containerd.io:
     ```sh
     wget https://download.docker.com/linux/centos/7/x86_64/stable/Packages/containerd.io-1.4.9-3.1.el7.x86_64.rpm
     ```
   - docker-ce-cli:
     ```sh
     wget https://download.docker.com/linux/centos/7/x86_64/stable/Packages/docker-ce-cli-20.10.8-3.el7.x86_64.rpm
     ```
   - docker-ce:
     ```sh
     wget https://download.docker.com/linux/centos/7/x86_64/stable/Packages/docker-ce-20.10.8-3.el7.x86_64.rpm
     ```

3. **安装下载的RPM包**：
   运行以下命令以安装这些RPM包(顺序不能改)：
   
   ```sh
   sudo yum install -y ./containerd.io-1.4.9-3.1.el7.x86_64.rpm
   sudo yum install -y ./docker-ce-cli-20.10.8-3.el7.x86_64.rpm
   sudo yum install -y ./docker-ce-20.10.8-3.el7.x86_64.rpm
   ```
   
4. **启动Docker**：
   ```sh
   sudo systemctl start docker
   sudo systemctl enable docker
   ```

5. **验证Docker安装**：
   运行以下命令查看Docker版本：
   ```sh
   docker --version
   ```

   以及：
   ```sh
   docker version
   ```

**安装Docker Compose**

1. **下载Docker Compose二进制文件**：
   
   ```sh
   sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   ```
   
2. **赋予执行权限**：
   ```sh
   sudo chmod +x /usr/local/bin/docker-compose
   sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose
   docker-compose --version
   ```

**创建 Docker Compose 文件**：
创建一个目录用于存放 Aria2 的配置文件和 Docker Compose 文件，例如 `aria2` 目录：

```sh
mkdir aria2
cd aria2
```

在该目录中创建 `docker-compose.yml` 文件：

![image-20240808150929186](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240808150929186.png)

其中RPC_SECRET就是自己的token

运行时发现报错：

![image-20240808153435613](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240808153435613.png)

拉取docker镜像超时的解决办法：

访问[容器镜像服务 (aliyun.com)](https://cr.console.aliyun.com/cn-hangzhou/instances/mirrors)，获取到加速链接：https://i9k2a8m7.mirror.aliyuncs.com



![image-20240808153315639](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240808153315639.png)

获取链接后在命令行中运行如下命令：

```sh
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json <<-'EOF'
{
  "registry-mirrors": ["https://i9k2a8m7.mirror.aliyuncs.com"]
}
EOF

```

一切配置妥当以后：

![image-20240808155625234](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240808155625234.png)

目前存在的报错信息：



![image-20240808160851056](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240808160851056.png)



---

## 文件下载bot

**需求**

用户向telegram bot发送bt种子文件或者链接，bot将文件下载后返回给用户

思路：

bot先接受用户传入的链接

bot将用户传入的链接交给aria2p

bot将下载好的文件发送给对应的会话

### 8.11-8.12期间阿里云2c2g/高配服务器交替测试得以发现错误使用正确接口



8.9 15:25左右时的代码版本(阿里云)，问题出在通知上：![image-20240809160120482](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240809160120482.png)



```python
#######测试发现这个版本的代码就可以完成下载任务，但是由于不明原因进度报告会出现问题，
import os
import logging
import asyncio
import json
import requests
from typing import Dict, Any
import aria2p
import time
from telegram import Update#pyhton3需要升级到 3.7版本以上
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
ARIA2_RPC_IP = "http://123.56.166.61"
ARIA2_RPC_PORT = 6800
ARIA2_RPC_SECRET = "lgd.chalice.taobao"
BOT_TOKEN = "7327334035:AAFn8lBKph9MYJSL5C6jtYV5vHFHvfBfi3A"
TORRENTS_TMP_DIR="/root/bot_torrents"#定义种子文件会被下载到这个中间路径
DOWNLOAD_DIR = "/root/downloads"#根据(磁力)链接/种子文件下载好的文件默认存放的目录
FILE_SIZE_LIMIT=2147483648 #2gb的字节数
#最大允许的下载时间，超过的话就自动停止
MAX_LOOP_TIME =100#最多通知多少次
PROCESS_TIME= 10#每次通知的间隔时间
#添加一个cancel命令用户手动停止
#添加一个shut up命令停止通知


aria2 = aria2p.API(
    aria2p.Client(
        host=ARIA2_RPC_IP,  # 替换为你的 Aria2 服务器地址
        port=ARIA2_RPC_PORT,
        secret=ARIA2_RPC_SECRET  # 替换为你的 Aria2 RPC 密钥
    )
)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message.text

    if message.startswith("http://") or message.startswith("https://"):
        # 处理 URI
        download = aria2.add(message)[0]#此处返回被创建出来的文件,理论上可以添加多个
        await update.message.reply_text(f"Added URI download: {download.name}")
        #然后考虑在这个部分增加提醒，以及发送文件的步骤
        if(download.total_length>=FILE_SIZE_LIMIT):
            download.remove_force()
            print("I cant send u files that over 2gb,sry")

        while(1):
            if(download.status=='active'):
                print(download.progress_string())
            if(download.status=='error'):
                print('download error')
                break
            if(download.status=='waiting'):
                print('waiting for download')
            if(download.status=='complete'):
                print('download finished')
                break
            if(download.status=='paused'):
                print('download paused')
            if(download.status=='removed'):
                print('download removed')
                break
            time.sleep(5)

    elif message.startswith("magnet:"):
        # 处理磁力链接
        download = aria2.add(message)
        await update.message.reply_text(f"Added Magnet download: {download.name}")
    elif update.message.document and update.message.document.file_name.endswith(".torrent"):
        # 处理种子文件
        file = await context.bot.get_file(update.message.document.file_id)
        file_path = f"{TORRENTS_TMP_DIR}/{update.message.document.file_name}"
        await file.download_to_drive(file_path)#把种子文件保存到本地路径
        download = aria2.add_torrent(file_path)#下载文件
        await update.message.reply_text(f"Added Torrent download: {download.name}")
        
    else:
        await update.message.reply_text("Unrecognized link or file. Please send a valid URI, magnet link, or torrent file.")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message when the bot is started."""
    await update.message.reply_text('Hello! Send me a BT seed file / link ')



def main() -> None:
    """Run the bot."""
    application = Application.builder().token(BOT_TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler('start', start))
    
    # on non-command messages - check for ads
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))#检测发送信息
    application.add_handler(MessageHandler(filters.Document.ALL, handle_message))#检测用户发送文件

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()

```

修改代码后发现虽然一直报0%，一直active，但是实际上文件已经都下载好了

![image-20240809170041731](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240809170041731.png)

中间就一直写一直改，我的代码最后就这样：

```python
import os
import asyncio
from aria2p.downloads import Download
import aria2p
from telegram import Update  # pyhton3需要升级到 3.7版本以上
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

ARIA2_RPC_IP = "http://57.154.66.147"
ARIA2_RPC_PORT = 6800
ARIA2_RPC_SECRET = "lgd.chalice.taobao"
BOT_TOKEN = "7327334035:AAFn8lBKph9MYJSL5C6jtYV5vHFHvfBfi3A"
TORRENTS_TMP_DIR = "/home/ubuntu/bot_torrents"  # 定义种子文件会被下载到这个中间路径
DOWNLOAD_DIR = "/home/ubuntu/downloads"  # 根据(磁力)链接/种子文件下载好的文件默认存放的目录
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
```

然后就换到在新服务器上重新搭建环境测试了：

新环境的配置如下）：

![image-20240811181956100](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240811181956100.png)

写了一个简短的test_module发现新服务器上连add函数都会失败：

![image-20240811192255281](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240811192255281.png)



**让ai为现有代码增加日志记录，然后根据这份代码的日志信息该原来的代码**

换了一个简单的密码(lgd.chalice.taobao->mysecret)以后和aria2建立的连接认证成功：

![image-20240811213425842](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240811213425842.png)

中间使用了

```bash
curl -X POST -d '{"jsonrpc":"2.0","method":"aria2.getGlobalStat","id":"1","params":["token:mysecret"]}' http://57.154.66.147:6800/jsonrpc
```

来检测服务器到aria2连接是否成功，发现认证失败

**（新环境下aria2这边始终认证失败，换了简单的密钥才得以解决问题)**

**8.12早11点完成的最终配置如下：**

![image-20240812112412558](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240812112412558.png)



然后我把用于**检测bug的可以输出日志的代码**换回**修改过的原版本代码**，发现已经可以初步完成项目目标了：

(后来发现这是建立在bug之上的，而且前提就是网速足够快，**新服务器下载文件的速度太快了，通过2种服务器交替测试才解决了问题**)

![image-20240811214849535](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240811214849535.png)



```python
#本质上此错误的，但是在种种巧合之下(网速和我写的判断条件)可以完成任务的代码：
import os
import asyncio
from aria2p.downloads import Download
import aria2p
from telegram import Update  # pyhton3需要升级到 3.7版本以上
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

ARIA2_RPC_IP = "http://57.154.66.147"
ARIA2_RPC_PORT = 6800
ARIA2_RPC_SECRET = "mysecret"
BOT_TOKEN = "7327334035:AAFn8lBKph9MYJSL5C6jtYV5vHFHvfBfi3A"
TORRENTS_TMP_DIR = "/home/ubuntu/bot_torrents"  # 定义种子文件会被下载到这个中间路径
DOWNLOAD_DIR = "/home/ubuntu/downloads"  # 根据(磁力)链接/种子文件下载好的文件默认存放的目录
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
    ##问题是一方面得确实下载完，另一方面最好检测一下大小是不是能对上，对的上的话就可以发了
    target_id = update.message.chat_id
    download_file_path = os.path.join(DOWNLOAD_DIR, download.name)  # 确保是实例属性


    await context.bot.send_document(chat_id=target_id, document=open(download_file_path, 'rb'))


# 最终执行的模块
async def my_is_complete(update: Update,context: ContextTypes.DEFAULT_TYPE,download: Download):

    download_file_path = os.path.join(DOWNLOAD_DIR, download.name)
    if not os.path.exists(download_file_path):
        return False
    #download.complete和download.progress似乎永远不会更新
    #错误的但是能运行,应该写成download才是对的，但是本质上这个不会动态更新，写错的方法使其一直是complete状态，但是超快的网速(2s下完github上一个1gb的压缩包)弥补了这一点，换成个下载速度更慢的网站上就不对劲了
    if (Download.is_complete and os.path.getsize(download_file_path)!=0):
        return True

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
        if await my_is_complete(update,context,download):
            await update.message.reply_text("Download complete")
            print(f'download.total_length:{download.total_length}')
            print(f'download.complete_length:{download.completed_length}')
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
```





**发现即使是下载完成了,两个变量依然是0，add返回的download就是静态的，不会实时更新**，能下载能上传是因为网速太快了，至此正式把download.complete的棺材板钉死

![image-20240812101606382](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240812101606382.png)

**其实还有一个细节，在阿里云环境下一边下载一边ll下载目录，能看到.aria文件，用于记录这个东西的下载进程，用于实现断点续传等功能**

**可是在新服务器下每次下载都只有下载好的文件，这个时候我就应该反应过来了**



考虑重新采用以下接口反复更新状态：

![image-20240812101818911](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240812101818911.png)





![image-20240812102200068](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240812102200068.png)







最后成功搞定了一个可以动态获取下载任务状态的版本，

![image-20240812104534632](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240812104534632.png)



上传失败发现是telegram的服务器问题导致了timeerror，这个问题需要后续调研：

![image-20240812104558820](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240812104558820.png)

```python
#修改后可以正确获得状态的代码：
import os
import asyncio
from aria2p.downloads import Download
import aria2p
from telegram import Update  # pyhton3需要升级到 3.7版本以上
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

ARIA2_RPC_IP = "http://57.154.66.147"
ARIA2_RPC_PORT = 6800
ARIA2_RPC_SECRET = "mysecret"
BOT_TOKEN = "7327334035:AAFn8lBKph9MYJSL5C6jtYV5vHFHvfBfi3A"
TORRENTS_TMP_DIR = "/home/ubuntu/bot_torrents"  # 定义种子文件会被下载到这个中间路径
DOWNLOAD_DIR = "/home/ubuntu/downloads"  # 根据(磁力)链接/种子文件下载好的文件默认存放的目录
FILE_SIZE_LIMIT = 2147483648  # 2gb的字节数
# 最大允许的下载时间，超过的话就自动停止


aria2 = aria2p.API(
    aria2p.Client(
        host=ARIA2_RPC_IP,  # 替换为你的 Aria2 服务器地址
        port=ARIA2_RPC_PORT,
        secret=ARIA2_RPC_SECRET  # 替换为你的 Aria2 RPC 密钥
    )
)

async def my_is_complete(update: Update,context: ContextTypes.DEFAULT_TYPE,download: Download):

    download_file_path = os.path.join(DOWNLOAD_DIR, download.name)
    if not os.path.exists(download_file_path):
        return False
    
    return download.is_complete

async def get_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get the chat ID of the current group."""
    return update.effective_chat.id


###########################################################################
# 文件发送模块
async def send_module(update: Update, context: ContextTypes.DEFAULT_TYPE, download: Download):
    ##问题是一方面得确实下载完，另一方面最好检测一下大小是不是能对上，对的上的话就可以发了
    target_id = update.message.chat_id
    download_file_path = os.path.join(DOWNLOAD_DIR, download.name)  # 确保是实例属性
    await context.bot.send_document(chat_id=target_id, document=open(download_file_path, 'rb'))


async def report_module(update: Update, context: ContextTypes.DEFAULT_TYPE, download: Download):
    
    if (await my_is_complete(update,context,download))==False:
        print(download.progress)
    if(download.progress>=0.8):
        await update.message.reply_text(f"Download progress:{download.progress_string}")
    elif(download.progress>=0.5):
        await update.message.reply_text(f"Download progress:{download.progress_string}")
    elif(download.progress>=0.2):
        await update.message.reply_text(f"Download progress:{download.progress_string}")

        
###########################################################################
# 最终执行的模块


async def the_module(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message.text
    download=None
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
        
    ###########文件下载中，无法完成消息通知
    #await report_module(update,context,download)
    #while True:
        #if await my_is_complete(update,context,download)==False:
            #await report_module(update,context,download)
        #else:
            #break
        #await asyncio.sleep(5)
    ##################################################



    while True:
        if await my_is_complete(update,context,download):
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


```





### 完成进度查询的report_moudle

~~这个module可能后续会删掉，通知方式改为用户直接调用来获取命令通知~~，**换成/progress调用的话拿不到gid**

report_module则是status出现错误的时候提醒用户重试

考虑用接口里的这两个成员，Download类里面都是int类型,这个类里面是

![image-20240812130318505](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240812130318505.png)

![image-20240812135952634](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240812135952634.png)

1gb太小，考虑一会放宽download_module里面的条件限制，然后找一些特别大的东西下载

---

#### 给bot添加一个简单的小界面

考虑用和BotFather一样的布局，有menu，有提示信息：

![image-20240812140951235](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240812140951235.png)

使用以下方式实现：



![image-20240812140920959](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240812140920959.png)

初步想增加的函数：

**刚需：help用来显示帮助信息**

**拓展：status用来获取当前下载的状态，并提示status在error或其他意外状态时提醒用户重试，**

**retry则是线remove掉失败的download之后重新下载**，~~aria2p这个库里面还有能控制download在下载队列里面相对位置的函数，考虑冲会员优先下载~~



中间改chatgpt代码的时候发现虽然代码一直报错，但是bot那边还是出现了一个可用的command菜单，感觉挺合理的，毕竟bot不运行的时候菜单还是得接着显示，但是又过了一会（中间改了好几次代码）发现菜单消失了，感觉这个东西也是有一个"寿命"的

先弄这三个：

```python
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message when the bot is started."""
    await update.message.reply_text('Hello! Send me a BT seed file / link ')

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a help message when the bot is asked for help."""
    await update.message.reply_text('Hello! Send me a BT seed file / link ,I will send you their corresponding files, the upper limit is 500M')

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

```

然后发现设置command menu的时候，那些函数也是异步的，感觉还得再封装一个模块塞进去：

![image-20240813024412022](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240813024412022.png)

直接访问官方的docs，写得更详细[相关链接](https://core.telegram.org/bots/api#botcommandscope)



**对于python-telegram-bot这种封装程度比较高的库，为了防止运行模块变为异步，避免多线程+异步的这种又难调试又难懂又难改的方式，一些不得不传参（比如说这次的set_my_commands函数）的函数，还是直接调用原来的api**

回档代码的时候发现菜单又间歇性的出现和消失，感觉menu也会有延迟生效，当时的代码里面我还没有使用接口来初始化menu：

![image-20240813025646345](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240813025646345.png)



---

### 调研一下关于telegram服务器那边的报错

```bash
(py39_env) ubuntu@telebot:~/file_download_bot$ python3.9 ./file_download_bot.py 
{'status': 'complete'}
No error handlers are registered, logging exception.
Traceback (most recent call last):
  File "/home/ubuntu/py39_env/lib/python3.9/site-packages/httpx/_transports/default.py", line 69, in map_httpcore_exceptions
    yield
  File "/home/ubuntu/py39_env/lib/python3.9/site-packages/httpx/_transports/default.py", line 373, in handle_async_request
    resp = await self._pool.handle_async_request(req)
  File "/home/ubuntu/py39_env/lib/python3.9/site-packages/httpcore/_async/connection_pool.py", line 216, in handle_async_request
    raise exc from None
  File "/home/ubuntu/py39_env/lib/python3.9/site-packages/httpcore/_async/connection_pool.py", line 196, in handle_async_request
  *****************************************************************************
    response = await connection.handle_async_request(
  File "/home/ubuntu/py39_env/lib/python3.9/site-packages/httpcore/_async/connection.py", line 101, in handle_async_request
    return await self._connection.handle_async_request(request)
  File "/home/ubuntu/py39_env/lib/python3.9/site-packages/httpcore/_async/http11.py", line 143, in handle_async_request
  *****根据分割线以内的内容严重怀疑是connection方面的问题
  *****************************************************************************
    raise exc
  File "/home/ubuntu/py39_env/lib/python3.9/site-packages/httpcore/_async/http11.py", line 113, in handle_async_request
    ) = await self._receive_response_headers(**kwargs)
  File "/home/ubuntu/py39_env/lib/python3.9/site-packages/httpcore/_async/http11.py", line 186, in _receive_response_headers
    event = await self._receive_event(timeout=timeout)
  File "/home/ubuntu/py39_env/lib/python3.9/site-packages/httpcore/_async/http11.py", line 224, in _receive_event
    data = await self._network_stream.read(
  File "/home/ubuntu/py39_env/lib/python3.9/site-packages/httpcore/_backends/anyio.py", line 37, in read
    return b""
  File "/usr/lib/python3.9/contextlib.py", line 137, in __exit__
    self.gen.throw(typ, value, traceback)
  File "/home/ubuntu/py39_env/lib/python3.9/site-packages/httpcore/_exceptions.py", line 14, in map_exceptions
    raise to_exc(exc) from exc
httpcore.ReadTimeout

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/home/ubuntu/py39_env/lib/python3.9/site-packages/telegram/request/_httpxrequest.py", line 276, in do_request
    res = await self._client.request(
  File "/home/ubuntu/py39_env/lib/python3.9/site-packages/httpx/_client.py", line 1574, in request
    return await self.send(request, auth=auth, follow_redirects=follow_redirects)
  File "/home/ubuntu/py39_env/lib/python3.9/site-packages/httpx/_client.py", line 1661, in send
    response = await self._send_handling_auth(
  File "/home/ubuntu/py39_env/lib/python3.9/site-packages/httpx/_client.py", line 1689, in _send_handling_auth
    response = await self._send_handling_redirects(
  File "/home/ubuntu/py39_env/lib/python3.9/site-packages/httpx/_client.py", line 1726, in _send_handling_redirects
    response = await self._send_single_request(request)
  File "/home/ubuntu/py39_env/lib/python3.9/site-packages/httpx/_client.py", line 1763, in _send_single_request
    response = await transport.handle_async_request(request)
  File "/home/ubuntu/py39_env/lib/python3.9/site-packages/httpx/_transports/default.py", line 373, in handle_async_request
    resp = await self._pool.handle_async_request(req)
  File "/usr/lib/python3.9/contextlib.py", line 137, in __exit__
    self.gen.throw(typ, value, traceback)
  File "/home/ubuntu/py39_env/lib/python3.9/site-packages/httpx/_transports/default.py", line 86, in map_httpcore_exceptions
    raise mapped_exc(message) from exc
httpx.ReadTimeout

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/home/ubuntu/py39_env/lib/python3.9/site-packages/telegram/ext/_application.py", line 1335, in process_update
    await coroutine
  File "/home/ubuntu/py39_env/lib/python3.9/site-packages/telegram/ext/_handlers/basehandler.py", line 157, in handle_update
    return await self.callback(update, context)
  File "/home/ubuntu/file_download_bot/./file_download_bot.py", line 110, in the_module
    await send_module(update, context, dl)
  File "/home/ubuntu/file_download_bot/./file_download_bot.py", line 47, in send_module
    await context.bot.send_document(chat_id=target_id, document=open(download_file_path, 'rb'))
  File "/home/ubuntu/py39_env/lib/python3.9/site-packages/telegram/ext/_extbot.py", line 2641, in send_document
    return await super().send_document(
  File "/home/ubuntu/py39_env/lib/python3.9/site-packages/telegram/_bot.py", line 1708, in send_document
    return await self._send_message(
  File "/home/ubuntu/py39_env/lib/python3.9/site-packages/telegram/ext/_extbot.py", line 610, in _send_message
    result = await super()._send_message(
  File "/home/ubuntu/py39_env/lib/python3.9/site-packages/telegram/_bot.py", line 744, in _send_message
    result = await self._post(
  File "/home/ubuntu/py39_env/lib/python3.9/site-packages/telegram/_bot.py", line 622, in _post
    return await self._do_post(
  File "/home/ubuntu/py39_env/lib/python3.9/site-packages/telegram/ext/_extbot.py", line 355, in _do_post
    return await super()._do_post(
  File "/home/ubuntu/py39_env/lib/python3.9/site-packages/telegram/_bot.py", line 651, in _do_post
    result = await request.post(
  File "/home/ubuntu/py39_env/lib/python3.9/site-packages/telegram/request/_baserequest.py", line 200, in post
    result = await self._request_wrapper(
  File "/home/ubuntu/py39_env/lib/python3.9/site-packages/telegram/request/_baserequest.py", line 342, in _request_wrapper
    raise exc
  File "/home/ubuntu/py39_env/lib/python3.9/site-packages/telegram/request/_baserequest.py", line 332, in _request_wrapper
    code, payload = await self.do_request(
  File "/home/ubuntu/py39_env/lib/python3.9/site-packages/telegram/request/_httpxrequest.py", line 293, in do_request
    raise TimedOut from err
telegram.error.TimedOut: Timed out
```



初步怀疑是set_document这个接口，目前已知的信息是，context.bot.send_document函数本身不支持断点续传，当使用这个方法发送文件时，整个文件会被一次性上传和发送。如果在发送过程中发生中断，必须重新开始发送整个文件：

好奇的点是为什么用户发文件没事，bot发文件为什么失灵，重点应该不在set_content这个函数，bot初始化条件少了，或者其他部分还是有问题

```python
ApplicationBuilder()链式初始化也用过了，但是没有起效
```









然后尝试以下这种方法:

```python
import httpx
from telegram.request import HTTPXRequest
from telegram.ext import ApplicationBuilder

# 设置超时和其他参数
timeout = httpx.Timeout(connect=CONNECTTIME_OUT, write=WRITETIME_OUT, read=READTIME_OUT, pool=None)
client = httpx.Client(timeout=timeout)

# 创建 HTTPXRequest 对象
request = HTTPXRequest(http_version="1.1", client=client)

# 配置 Application 对象
application = ApplicationBuilder().token(BOT_TOKEN).request(request).build()

```

ai的具体初始化还是不对，得多按照下图手搓

![image-20240812182412823](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240812182412823.png)

**除了我已经初始化过的read/write/connect_timeout ,还有media_write_timeout这个变量我还没初始化过，由于我掐着秒表测了两次程序从"用户输入指令"到"terminal出现报错"的这段时间，一次是35秒，一次是28秒，很让我怀疑这个"20" 的缺省值**

果然对了,改了之后报错显示的内容变成了readerror:

![image-20240812183534301](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240812183534301.png)

然后我把其他超时时间也设置成3分钟了，但是报的还是httpx:ReadError

这个时候chatgpt建议我把httpversion版本换成2

改完之后发现只是时间到了：

![image-20240812185107664](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240812185107664.png)

直接加到20分钟

后来发现不能上传大文件只是一个特性，这里考虑用原生接口

![image-20240812202458889](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240812202458889.png)

```chatgpt
**根据 Telegram 的核心文档 `upload.saveBigFilePart` 函数的说明，当上传的文件大小超过 512 MB（即 536,870,912 字节）时，会触发 `FILE_PART_TOO_BIG` 错误。**

**这意味着每个文件分块的大小不得超过 512 MB。如果你尝试上传的单个文件分块大于这个限制，就会遇到该错误。因此，在上传大文件时，需要确保每个分块的大小在允许的范围内。**

**你可以参考 [Telegram Core 文档](https://core.telegram.org/method/upload.saveBigFilePart) 了解更多关于此函数的详细信息。**
```

***结论就是自己有点依赖chatgpt了，而且光看示例代码的话会忽略函数中这个缺省参数，更精密的操作就做不到了，最好还是看一遍文档看它有没有胡说八道，上面这段话就有问题，怎么找也没找到他所说的512MB***

一通修改以后：

```python
import os
import zipfile
import aiofiles
from telegram import Bot
from telegram.error import NetworkError
import asyncio
import aria2p.client
from aria2p.downloads import Download
import aria2p
import time
import httpx
from telegram import Update,BotCommand  # pyhton3需要升级到 3.7版本以上
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from httpx import Timeout
from telegram.request import HTTPXRequest
ARIA2_RPC_IP = "http://57.154.66.147"# 替换为你的 Aria2 服务器地址
ARIA2_RPC_PORT = 6800
ARIA2_RPC_SECRET = "mysecret"# 替换为你的 Aria2 RPC 密钥
BOT_TOKEN = "7327334035:AAFn8lBKph9MYJSL5C6jtYV5vHFHvfBfi3A"
TORRENTS_TMP_DIR = "/home/ubuntu/bot_torrents"  # 定义种子文件会被下载到这个中间路径
FILE_SIZE_LIMIT = 524288000 #500m      #2147483648  # 2gb的字节数
WRITETIME_OUT=1200.0
CONNECTTIME_OUT=1200.0
READTIME_OUT=1200.0


#########################################
mc=aria2p.Client(
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












async def my_is_complete(update: Update,context: ContextTypes.DEFAULT_TYPE,download: Download):
    id=download.gid
    sts=mc.tell_status(id,['status'])
    print(sts)
    if sts['status']=='complete':
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

async def report_module(update: Update, context: ContextTypes.DEFAULT_TYPE,download:Download) -> None:
    while await my_is_complete(update,context,download):
        pl=mc.tell_status(download.gid,['totalLength','completedLength'])
        output=int(pl['completedLength'])/int(pl['totalLength'])
        print(output)
        if(output==1.0):
            break
        elif(output>=0.8):
            await update.message.reply_text(f"Download progress: {output}")
        elif(output>=0.6):
            await update.message.reply_text(f"Download progress: {output}")
        elif(output>=0.4):
            await update.message.reply_text(f"Download progress: {output}")
        elif(output>=0.2):
            await update.message.reply_text(f"Download progress: {output}")
    await asyncio.sleep(5)

    







#最终需要使用的部分
async def the_module(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    dl=await download_module(update,context)
    await report_module(update,context,dl)
    await send_module(update, context, dl)
            



def main() -> None:
    """Run the bot."""
    application = ApplicationBuilder().token(BOT_TOKEN).media_write_timeout(300.0).build()#可用的版本
    
    
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



```



![image-20240812220203197](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240812220203197.png)

感觉只能改一下然后以50M的单位传了，之前拿80+M的文件测试的时候也是“即使文件过来了，但是服务器那边的终端也会有报错”，真就是服务器的网速连光都可以超越

一个文件压20来个压缩包感觉很难受,而且这个东西放在一起很乱：



![image-20240812232355979](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240812232355979.png)

考虑加一个cancel指令用来清除当前下载的中间文件，然后把下载的文件也移除，发现可以通过**在下载是更新上下文数据**来判断**当前会话下载的文件的gid**是啥：

![image-20240813005322770](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240813005322770.png)







---



#### send_moudle的新实现：



上传的部分只能用偏原生的类来封装了,准备传一个chat_id,传一个文件名，以下是chatgpt的示例代码：

```python
#上传单个文件
import os
from telegram import Bot
from telegram.error import NetworkError



def send_file(bot: Bot, chat_id: int, downloaded_filename: str):
    # 获取文件大小
    file_size = os.path.getsize(downloaded_filename)
    # 文件大小限制
    small_file_limit = 50 * 1024 * 1024  # 50 MB
    big_file_limit = 512 * 1024 * 1024   # 512 MB
    
    try:
        if file_size <= small_file_limit:
            # 使用 send_document 发送小于等于 50 MB 的文件
            with open(downloaded_filename, 'rb') as file:
                bot.send_document(chat_id=chat_id, document=file)
        elif file_size <= big_file_limit:
            # 使用 send_document 分块发送大于 50 MB 但小于等于 512 MB 的文件
            with open(downloaded_filename, 'rb') as file:
                bot.send_document(chat_id=chat_id, document=file)
        else:
            # 文件太大，无法发送
            bot.send_message(chat_id=chat_id, text="文件太大，无法通过 Telegram 发送。")
    except NetworkError as e:
        bot.send_message(chat_id=chat_id, text=f"发送文件时出错: {str(e)}")

# 示例使用
# bot = Bot(token='YOUR_TELEGRAM_BOT_TOKEN')
# send_file(bot, chat_id=123456789, downloaded_filename='path/to/downloaded_filename')

```



分割并上传parts：

```python
import os
import zipfile
import aiofiles
from telegram import Bot
from telegram.error import NetworkError
from telegram.ext import Application



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

async def send_file(bot: Bot, chat_id: int, downloaded_filename: str):
    # 获取文件大小
    file_size = os.path.getsize(downloaded_filename)
    
    # 文件大小限制
    small_file_limit = 50 * 1024 * 1024  # 50 MB
    big_file_limit = 512 * 1024 * 1024   # 512 MB
    
    try:
        if file_size <= small_file_limit:
            # 使用 send_document 发送小于等于 50 MB 的文件
            async with aiofiles.open(downloaded_filename, 'rb') as file:
                await bot.send_document(chat_id=chat_id, document=file)
        elif file_size <= big_file_limit:
            # 使用 send_document 分块发送大于 50 MB 但小于等于 512 MB 的文件
            async with aiofiles.open(downloaded_filename, 'rb') as file:
                await bot.send_document(chat_id=chat_id, document=file)
        else:
            # 文件太大，分割并发送
            part_size = big_file_limit - (1 * 1024 * 1024)  # 为安全起见，略小于 512 MB
            parts = await split_file(downloaded_filename, part_size)
            
            for part in parts:
                async with aiofiles.open(part, 'rb') as file:
                    await bot.send_document(chat_id=chat_id, document=file)
                os.remove(part)  # 发送后删除压缩包

            await bot.send_message(chat_id=chat_id, text="文件已分割并成功发送。")
    except NetworkError as e:
        await bot.send_message(chat_id=chat_id, text=f"发送文件时出错: {str(e)}")

# 示例使用
# application = Application.builder().token('YOUR_TELEGRAM_BOT_TOKEN').build()
# await send_file(application.bot, chat_id=123456789, downloaded_filename='path/to/downloaded_filename')


```









---





### 去盗版电影网站上找磁力链接进行更多场景的测试

#### 用于测试的网站

https://www.bttjia.com/video/32020ySiShi3/

http://bt.sosoba.org/article/5612.html













### 为程序增加pd sql数据库

#### 什么是pd sql

`pd sql` 通常是指在使用 `pandas` 库时，利用 SQL 风格的查询来处理数据。这通常涉及使用 `pandas` 的方法来处理数据框（DataFrame），而这些方法与 SQL 查询非常相似。这种方法可以帮助那些熟悉 SQL 的用户在使用 `pandas` 时更加直观地操作数据。

**示例：**

在 `pandas` 中，你可以使用 SQL 风格的操作来处理数据框。例如：

1. **`SELECT` 查询**：
   - 在 SQL 中，你可能会使用 `SELECT` 语句来选择表中的某些列。
   - 在 `pandas` 中，你可以使用 DataFrame 的索引来完成类似的操作：
   ```python
   import pandas as pd
   
   # 假设你有一个 DataFrame df
   df = pd.DataFrame({
       'name': ['Alice', 'Bob', 'Charlie'],
       'age': [25, 30, 35]
   })
   
   # SQL 风格的查询
   # SELECT name FROM df WHERE age > 25
   result = df[df['age'] > 25]['name']
   print(result)
   ```

2. **`JOIN` 查询**：
   
   - 在 SQL 中，你可能会使用 `JOIN` 来合并两个表。
   - 在 `pandas` 中，你可以使用 `merge` 方法：
   ```python
   df1 = pd.DataFrame({
       'id': [1, 2, 3],
       'name': ['Alice', 'Bob', 'Charlie']
   })
   
   df2 = pd.DataFrame({
       'id': [1, 2, 4],
       'score': [85, 90, 95]
   })
   
   # SQL 风格的查询
   # SELECT * FROM df1 JOIN df2 ON df1.id = df2.id
   merged_df = pd.merge(df1, df2, on='id')
   print(merged_df)
   ```

**使用 `pandasql` 库：**

还有一个专门的库叫做 `pandasql`，它允许你直接在 `pandas` 的 DataFrame 上运行 SQL 查询。这对于那些更熟悉 SQL 而不是 Python 操作数据框的人非常有用。

```python
#我觉得应该用这个
import pandas as pd
import pandasql as psql

df = pd.DataFrame({
    'name': ['Alice', 'Bob', 'Charlie'],
    'age': [25, 30, 35]
})

# 使用 pandasql 来运行 SQL 查询
query = "SELECT name FROM df WHERE age > 25"
result = psql.sqldf(query, locals())
print(result)
```

**总结**

- **`pd sql`**: 通常是指在 `pandas` 中使用 SQL 风格的操作。
- **`pandasql`**: 是一个可以直接在 `pandas` DataFrame 上运行 SQL 查询的库，非常适合那些更熟悉 SQL 语法的人。

---

### pandasql和mysql的区别

`pandasql` 和 `MySQL` 是两种不同的工具，尽管它们都涉及到数据查询和操作，但它们的应用场景和功能特性有显著的区别。

**1. 定义与用途**

- **`pandasql`**:
  - `pandasql` 是一个 Python 库，它允许你使用 SQL 查询语法在 `pandas` DataFrame 上执行操作。它特别适合那些习惯于 SQL 语法但希望在 Python 环境下处理数据的用户。`pandasql` 在后台使用 `SQLite` 引擎来解析和执行查询。
  - 用途：用于在 Python 环境中，针对小型到中型数据集快速执行 SQL 风格的查询。

- **`MySQL`**:
  - `MySQL` 是一个关系型数据库管理系统 (RDBMS)，用于存储和管理大型结构化数据。它支持 SQL 语言，允许用户创建、读取、更新和删除数据库中的数据，并能够处理大量并发用户请求。
  - 用途：广泛用于 web 应用程序和企业级环境中，处理大规模数据管理和复杂的查询。

**2. 架构与性能**

- **`pandasql`**:
  - 作为一个 Python 库，它主要用于内存中的数据操作，并不涉及实际的数据存储或持久化。它依赖 `pandas` 处理数据，适合数据规模相对较小的情况（通常几百万行以内）。
  - 性能：受限于内存，适合单机环境下的快速原型开发和数据分析。

- **`MySQL`**:
  - 是一个完整的数据库管理系统，支持数据的持久化存储，并能够在服务器端处理大规模的数据。它支持复杂的事务管理、并发控制和优化。
  - 性能：设计用于处理海量数据，并能够在多个用户和应用程序之间高效并发运行。

**3. 使用场景**

- **`pandasql`**:
  - 适合使用 `pandas` 进行数据分析时，希望以 SQL 语法查询数据的场景。例如，数据科学家或分析师可以用 `pandasql` 快速在 Python 环境下执行 SQL 查询，而不需要设置数据库。
  - 适合处理临时数据集、分析数据、数据清洗等。

- **`MySQL`**:
  - 适合需要持久化存储、管理大规模数据的应用场景。例如，web 应用程序、企业信息系统等需要一个可靠的后端数据库来存储和管理用户数据、交易记录等。
  - 适合需要高可用性、高并发性的生产环境。

**4. 易用性与灵活性**

- **`pandasql`**:
  - 易用性：对于熟悉 SQL 但不熟悉 `pandas` 的用户，`pandasql` 提供了一个友好的过渡工具。但它在功能上受限于 `pandas` 和内存的容量。
  - 灵活性：非常适合快速分析和小规模数据处理。

- **`MySQL`**:
  - 易用性：要求用户熟悉 SQL 语法和数据库管理，适合更复杂的应用场景。
  - 灵活性：非常强大，支持事务、存储过程、触发器、索引等高级功能。

**总结**

- **`pandasql`** 是一个简便的工具，主要用于在 Python 环境下对内存中的数据进行 SQL 风格的查询，适合小规模数据分析。
- **`MySQL`** 是一个功能强大的关系型数据库管理系统，适合处理大规模数据并支持复杂的数据库操作，广泛用于生产环境。

你可以选择使用哪个工具，取决于你的具体需求和应用场景。

---

#### 为服务器搭建pd sql环境

要在 Python 3.9 环境下使用 `pandasql` 库，您可以按照以下步骤进行操作：

**1. 安装 `pandasql` 库**

首先，确保您已经安装了 `pandasql` 库。您可以使用 `pip` 来安装：

```bash
pip install pandasql
```

2. **在 Python 脚本或交互式环境中导入 `pandasql`**

安装完成后，您可以在 Python 代码中导入 `pandasql` 并使用它。

**3. 使用 `pandasql` 运行 SQL 查询**

以下是一个简单的示例，展示如何在 `pandas` DataFrame 上使用 SQL 查询：

```python
import pandas as pd
import pandasql as psql

# 创建一个示例 DataFrame
df = pd.DataFrame({
    'name': ['Alice', 'Bob', 'Charlie'],
    'age': [25, 30, 35]
})

# 定义一个 SQL 查询
query = "SELECT name FROM df WHERE age > 25"

# 使用 pandasql 执行查询
result = psql.sqldf(query, locals())

# 输出结果
print(result)
```

代码解释

- **`import pandas as pd`**: 导入 `pandas` 库，用于创建和操作 DataFrame。
- **`import pandasql as psql`**: 导入 `pandasql` 库，用于在 DataFrame 上执行 SQL 查询。
- **`pandasql.sqldf(query, locals())`**: 使用 `sqldf` 函数来执行 SQL 查询。`query` 是您的 SQL 语句，`locals()` 将当前的本地变量传递给 `sqldf`，以便在查询中使用 `df`。

**4. 检查 Python 版本**

确保您当前的环境是在 Python 3.9 下运行的，可以使用以下命令来检查：

```bash
python3.9 --version
```

**5. 测试运行**

确保代码正常运行并返回正确的查询结果。

这样，您就可以在 Python 3.9 环境下使用 `pandasql` 库来对 `pandas` DataFrame 进行 SQL 查询了。

---



#### 具体在程序里的应用

数据库用来存储下载文件的路径，文件名，大小，和md5值(可惜的是aria2p这个类没法获取下载文件的md5值)

如果用户提供的文件的md5值和数据库内已有文件的md5值相同的话就直接发送这个文件

##### 根据下载文件的md5值建数据库：

通常情况下，要获取文件的 MD5 值，你需要下载整个文件，因为 MD5 值是基于文件的全部内容计算的。然而，有些情况例外：

**1. 服务器提供的 MD5 校验值**

   - 有些下载服务器会在文件的下载页面上直接提供文件的 MD5 值，供用户在下载后验证文件完整性。
   - 你可以在下载页面或通过请求文件的元数据来获取这个 MD5 值。如果服务器在响应头中提供了 `Content-MD5` 字段，你可以通过 HEAD 请求获取它。

   例如：

   ```python
   import requests

   url = 'https://example.com/path/to/file'

   response = requests.head(url)
   md5_hash = response.headers.get('Content-MD5')

   if md5_hash:
       print(f"MD5: {md5_hash}")
   else:
       print("MD5 hash not provided by the server.")
   ```

**2. 通过 API 获取 MD5 值**

   - 有些文件存储服务或下载平台可能提供 API 来查询文件的详细信息，包括 MD5 值。

**3. 使用特定下载工具**

   - 一些下载工具（如 `wget` 或 `curl`）在下载文件时可以同时获取文件的校验值，但它们通常仍然需要至少部分下载文件。

在大多数情况下，你需要下载文件才能计算其 MD5 值。除非服务器在响应头中提供了 `Content-MD5`，或者服务器提供了文件的校验信息，否则无法在不下载文件的情况下计算出其 MD5 值。

---

##### magnet与.torrent(下载文件可以存放在一张表里面，info_hash做主键)

**InfoHash** 是在 BitTorrent 协议中用于标识种子文件或磁力链接（Magnet Link）的一个唯一哈希值。它是通过对 `.torrent` 文件中的 `info` 字段内容进行 SHA-1 哈希计算生成的。

万幸的是**Download类里面还可以****返回BT的infohash**![image-20240812144917962](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240812144917962.png)

**InfoHash 的作用**

1. **唯一标识**: 每个 `.torrent` 文件或磁力链接都有一个对应的 InfoHash，作为该文件的唯一标识符。即使不同的 `.torrent` 文件指向同样的文件或文件集，它们的 InfoHash 也会相同，只要 `info` 字段内容一致。
   
2. **连接对等节点**: 在 P2P 网络中，InfoHash 用于查找其他拥有相同文件的对等节点。通过 DHT 网络或 Tracker 服务器，BitTorrent 客户端可以使用 InfoHash 连接到这些对等节点，并开始下载文件。

3. **磁力链接**: 磁力链接的核心就是 InfoHash。磁力链接中通常会包含一个 `xt` 参数，例如 `xt=urn:btih:<infohash>`，这就是文件的 InfoHash。客户端使用这个 InfoHash 来搜索文件资源。

**生成 InfoHash 的过程**

1. **`info` 字段**: 在 `.torrent` 文件中，`info` 字段包含了文件的元数据信息，例如文件名、大小、分块信息等。
2. **SHA-1 哈希**: 对 `info` 字段的数据进行 SHA-1 哈希运算，得到一个 20 字节（160 位）的哈希值，这就是 InfoHash。

要从一个磁力链接（magnet link）中获取 InfoHash 而无需下载文件，你可以直接从磁力链接的结构中提取 InfoHash。磁力链接通常包含一个 `xt` 参数，这个参数包含了文件的 InfoHash。下面是详细的步骤：

**磁力链接的结构**

一个典型的磁力链接格式如下：

```
magnet:?xt=urn:btih:<info_hash>&dn=<display_name>&tr=<tracker_url>
```

- **`xt=urn:btih:<info_hash>`**: `btih` 表示 BitTorrent InfoHash，这是你要提取的部分。
- **`dn=<display_name>`**: （可选）文件或文件夹的名称。
- **`tr=<tracker_url>`**: （可选）跟踪服务器的 URL。

**使用 Python 提取 InfoHash**

你可以使用以下 Python 代码来提取磁力链接中的 InfoHash：

```python
import re

def extract_infohash(magnet_link):
    match = re.search(r'btih:([a-fA-F0-9]+)', magnet_link)
    if match:
        return match.group(1)
    return None

# 示例磁力链接
magnet_link = 'magnet:?xt=urn:btih:1234567890abcdef1234567890abcdef12345678&dn=example&tr=http://tracker.example.com/announce'

# 提取 InfoHash
infohash = extract_infohash(magnet_link)
print(f'InfoHash: {infohash}')
```

- **`re.search(r'btih:([a-fA-F0-9]+)', magnet_link)`**: 这是一个正则表达式，用于在磁力链接中查找 `btih:` 后面跟随的 InfoHash。
- **`match.group(1)`**: 如果找到了匹配的内容，`group(1)` 会返回 InfoHash。
- 不需要下载文件就可以直接从磁力链接中提取 InfoHash

---

