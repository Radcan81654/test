# 第一周任务

[TOC]

## 2024.8.9

主要任务为完成文件下载bot，熟悉aria2p类

### 已知可靠信息

- [Telegram Bot API 文档](https://core.telegram.org/bots/api)
- [python-telegram-bot 文档](https://python-telegram-bot.readthedocs.io/en/stable/),[函数的详细使用说明](https://docs.python-telegram-bot.org/en/stable/telegram.bot.html)，`telegram` 模块是底层 API 的直接封装，而 `telegram.ext` 提供了更高层次的功能
- [词汇表](https://core.telegram.org/tdlib/getting-started)
- **use this token to access the http api:**7327334035:AAFn8lBKph9MYJSL5C6jtYV5vHFHvfBfi3A
- 在阿里云服务器上运行clash的脚本，只需要修改环境变量：https://github.com/wnlen/clash-for-linux

---





### import aria2p

#### 说明文档

脚本安装管理的版本是修改过的：

![image-20240808183503216](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240808183503216.png)

用于管理磁盘空间/着眼于服务器性能的api可以先不考虑

#### [aria2p 使用说明](https://pawamoy.github.io/aria2p/usage/)

[API使用说明](https://pawamoy.github.io/aria2p/reference/aria2p/)

https://pawamoy.github.io/aria2p/reference/aria2p/client/#aria2p.client.Client.add_uri

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

### 通过安装管理脚本一键安装

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

8.9 15:25左右时的代码版本，问题出在通知上：![image-20240809160120482](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240809160120482.png)



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



```python
#chatgpt重写的代码，可以完成“报告进度”同时接收shut_up命令

import os
import asyncio
import aria2p
import time
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

ARIA2_RPC_IP = "http://123.56.166.61"
ARIA2_RPC_PORT = 6800
ARIA2_RPC_SECRET = "lgd.chalice.taobao"
BOT_TOKEN = "7327334035:AAFn8lBKph9MYJSL5C6jtYV5vHFHvfBfi3A"
TORRENTS_TMP_DIR = "/root/bot_torrents"
DOWNLOAD_DIR = "/root/downloads"
FILE_SIZE_LIMIT = 2147483648  # 2GB

aria2 = aria2p.API(
    aria2p.Client(
        host=ARIA2_RPC_IP,
        port=ARIA2_RPC_PORT,
        secret=ARIA2_RPC_SECRET
    )
)

# Global variables to control downloads and reporting
current_download = None
reporting_enabled = True
cancel_requested = False

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message.text

    if message.startswith("http://") or message.startswith("https://") or message.startswith("magnet:"):
        # 处理 URI 和磁力链接
        current_download = aria2.add(message)[0]  # 只处理单个下载
        await update.message.reply_text(f"Added download: {current_download.name}")

        if current_download.total_length >= FILE_SIZE_LIMIT:
            current_download.remove_force()
            await update.message.reply_text("I can't send files over 2GB. Download has been cancelled.")
            current_download = None
            return

        while current_download and current_download.status != 'complete' and current_download.status != 'error' and current_download.status != 'removed':
            print(f'cancel_request:{cancel_requested}')
            print(f'current_download.status:{current_download.status}')
            if cancel_requested:
                current_download.remove_force()
                await update.message.reply_text(f"Download {current_download.name} has been cancelled.")
                current_download = None
                cancel_requested = False
                return
            print(f'reporting_enabled:{reporting_enabled}')
            if reporting_enabled:
                await update.message.reply_text(f"Download progress: {current_download.progress_string()}")
            
            #这部分出了问题，ai说这段时间里面数据是更新不了的
            
            await asyncio.sleep(30)

        if current_download:
            if current_download.status == 'complete':
                await update.message.reply_text('Download finished')
            elif current_download.status == 'error':
                await update.message.reply_text('Download error')
            current_download = None

    elif update.message.document and update.message.document.file_name.endswith(".torrent"):
        # 处理种子文件
        file = await context.bot.get_file(update.message.document.file_id)
        file_path = f"{TORRENTS_TMP_DIR}/{update.message.document.file_name}"
        await file.download_to_drive(file_path)
        current_download = aria2.add_torrent(file_path)[0]
        await update.message.reply_text(f"Added Torrent download: {current_download.name}")
    else:
        await update.message.reply_text("Unrecognized link or file. Please send a valid URI, magnet link, or torrent file.")


async def cancel_download(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if current_download:
        cancel_requested = True
        await update.message.reply_text("Canceling the current download...")
    else:
        await update.message.reply_text("No active download to cancel.")


async def shut_up(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global reporting_enabled
    reporting_enabled = not reporting_enabled
    await update.message.reply_text("Progress reporting has been disabled.")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message when the bot is started."""
    await update.message.reply_text('Hello! Send me a BT seed file / link or use /cancel_download to cancel the current download, /shut_up to stop progress reporting.')


def main() -> None:
    """Run the bot."""
    application = Application.builder().token(BOT_TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('cancel_download', cancel_download))
    application.add_handler(CommandHandler('shut_up', shut_up))

    # Register message handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_message))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()


```

chatgpt:要实现每 30 秒通知一次下载进度，并且在此期间仍然可以处理 `/cancel_download` 和 `/shut_up` 指令，你可以将下载进度的通知部分移到一个独立的异步任务中。这可以通过 `asyncio.create_task` 创建一个并行执行的任务来实现，从而使得主任务和通知任务可以独立运行。
