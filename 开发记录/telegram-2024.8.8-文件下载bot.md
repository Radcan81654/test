# 第一周任务

[TOC]

## 2024.8.8

主要任务为完成文件下载bot，熟悉aria2p类

### 已知可靠信息

- [Telegram Bot API 文档](https://core.telegram.org/bots/api)
- [python-telegram-bot 文档](https://python-telegram-bot.readthedocs.io/en/stable/),[函数的详细使用说明](https://docs.python-telegram-bot.org/en/stable/telegram.bot.html)，`telegram` 模块是底层 API 的直接封装，而 `telegram.ext` 提供了更高层次的功能
- [词汇表](https://core.telegram.org/tdlib/getting-started)
- **use this token to access the http api:**7327334035:AAFn8lBKph9MYJSL5C6jtYV5vHFHvfBfi3A
- 

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
remove – Remove a download.##删除正在进行的下载任务
res_or_raise – Return the result of the response, or raise an error with code and message.
response_as_exception – Transform the response as a ClientException instance and return it.
save_session – Save the current session to a file.
stop_listening – Stop listening to notifications..
tell_status – Tell status of a download.#####################

```

API类则需要Client类进行初始化

```python
API(client: Client | None = None)
add – Add a download (guess its type).
add_magnet – Add a download with a Magnet URI.
add_metalink – Add a download with a Metalink file.
add_torrent – Add a download with a torrent file (usually .torrent extension).
add_uris – Add a download with a URL (or more).
autopurge – Purge completed, removed or failed downloads from the queue.
copy_files – Copy downloaded files to another directory.
get_download – Get a Download object thanks to its GID.
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
pause – Pause the given (active) downloads.
pause_all – Pause all (active) downloads.
purge – Purge completed, removed or failed downloads from the queue.
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

chaigpt使用的示例代码：

```python
import os
import logging
import asyncio
import json
import requests
from typing import Dict, Any
import aria2p
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
#######################bot会话没问题，问题全部在aria2p上
# Configuration
ARIA2_RPC_URL = "http://123.56.166.61"
ARIA2_RPC_SECRET = "lgd.chalice.taobao"
BOT_TOKEN = "7327334035:AAFn8lBKph9MYJSL5C6jtYV5vHFHvfBfi3A"
DOWNLOAD_DIR = "/root/aria2/backup_files"

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)


# Initialize Aria2 client with debug information
class DebugClient(aria2p.Client):
    def post(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # 添加调试信息
            print("Request payload:", json.dumps(payload))
            response = requests.post(self.server, data=json.dumps(payload), timeout=self.timeout)
            print("Response status code:", response.status_code)
            print("Response text:", response.text)  # 打印原始响应

            response.raise_for_status()  # 确保我们在状态码错误时抛出异常
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Request to Aria2 failed: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON response: {e}")
            raise


aria2 = aria2p.API(
    DebugClient(
        host=ARIA2_RPC_URL,
        secret=ARIA2_RPC_SECRET
    )
)

# Ensure the download directory exists
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message when the bot is started."""
    await update.message.reply_text('Hello! Send me a BT seed file or link.')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text('Help!')


async def download_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle file downloads."""
    document = update.message.document

    if document:
        # Get the file
        file = await context.bot.get_file(document.file_id)
        file_path = os.path.join(DOWNLOAD_DIR, document.file_name)
        await file.download_to_drive(file_path)

        try:
            # Add download to Aria2
            download = aria2.add_torrent(file_path, options={"dir": DOWNLOAD_DIR})
            # Reply to the user with the download status
            await update.message.reply_text(f"Started downloading: {document.file_name}\nGID: {download.gid}")

            # Check the status of the download
            while not aria2.get_download(download.gid).is_complete:
                await asyncio.sleep(5)  # wait for 5 seconds before checking again

            # Send the downloaded file back to the user
            await context.bot.send_document(chat_id=update.message.chat_id, document=open(file_path, 'rb'))

        except Exception as e:
            logger.error(f"Error adding torrent: {e}")
            await update.message.reply_text(f"Failed to start downloading: {document.file_name}")

#下载链接：
async def download_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle link downloads."""
    url = update.message.text

    try:
        # Add download to Aria2
        print(f"Adding URI: {url}")
        download = aria2.add_uris([url], options={"dir": DOWNLOAD_DIR})
        print(f"Download GID: {download.gid}")
        # Reply to the user with the download status
        await update.message.reply_text(f"Started downloading: {url}\nGID: {download.gid}")

        # Check the status of the download
        while not aria2.get_download(download.gid).is_complete:
            await asyncio.sleep(5)  # wait for 5 seconds before checking again

        # Get the file path
        file_path = os.path.join(DOWNLOAD_DIR, download.files[0].name)

        # Send the downloaded file back to the user
        await context.bot.send_document(chat_id=update.message.chat_id, document=open(file_path, 'rb'))

    except Exception as e:
        logger.error(f"Error adding URI: {e}")
        await update.message.reply_text(f"Failed to start downloading: {url}")


def main() -> None:
    """Run the bot."""
    application = Application.builder().token(BOT_TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_command))

    # on non-command messages - check for ads
    application.add_handler(MessageHandler(filters.Document.ALL, download_file))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_link))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()


```

