# 前言

使用飞书，telegram所提供的接口时拥有相似的使用流程：

创建自定义bot/应用->获取token->赋予权限->熟悉说明文档

本文将从飞书的文本采集，telegram的anti-ad bot和forward_msg bot项目的编写过程中总结可复用的经验 

[飞书表格的信息采集](https://github.com/Radcan81654/test/tree/main/new_dtc)

[群组管理与消息转发bot](https://github.com/Radcan81654/test/tree/main/my_telegram_bot)

---

# 飞书,telegram,etc API调用指南

//为响应要求，后续会增加更多示例截图



[TOC]

## 关于官方说明文档

如果官方说明文档中提供了开发流程概述，可以通过里面的内容规划流程：

![image-20240807141612844](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240807141612844.png)

### 了解词汇表

了解词汇表的目的在于预防对接口参数的误判

比如飞书中**电子表格**在文档中被称为**spreadsheet**，而**电子表格中的多个表单**被称为**工作表(sheet)**，提前理清词汇表的内容和不同概念的关系可以避免混淆

[飞书词汇表](https://open.feishu.cn/document/server-docs/docs/docs-overview)

---

### 整理所需接口

建议两种方法结合使用

举一个例子：

**示例需求**：

1. 技术采集飞书表格 [生财文章列表(持续更新)](https://iqzeljuzeco.feishu.cn/sheets/N5Wts8V9Wh3gXJtyxPvcDbMZnJc)

2. 将步骤一采集信息自动保存在飞书表格的新的页面，新的页面有以下几点要求：
    A. 表格字段有：编号、更新日志、文章摘要、文章链接、文章关键字(标签)，其中文章摘要和标签可以使用openai的api获取
    B. 支持自动更新，当原表格有更新的时候自动更新当前表格

---

#### 手动整理

根据需求从飞书的官方API中手动搜寻所需接口，**相对麻烦**，这种方法**受限于开发者在文档中的表述**，以及文档阅读者的信息过滤能力

[飞书服务端API列表](https://open.feishu.cn/document/server-docs/api-call-guide/server-api-list)

**理由：**

> 由于在短时间内**对开发文档**了解程度**了解不够**，加上**接口的命名方式**也可能都我们产生**误导**：
>
> 我们自己**手动寻找的接口不一定是最符合项目需求**的，在写代码和测试代码的过程中可能需要一直**尝试/寻找新的接口**

比如在想办法获取工作表token时，你可能会看见以下3个接口：

[查询工作表 - 服务端 API - 开发文档 - 飞书开放平台 (feishu.cn)](https://open.feishu.cn/document/server-docs/docs/sheets-v3/spreadsheet-sheet/get?appId=cli_a6109595397dd00c)

[获取工作表 - 服务端 API - 开发文档 - 飞书开放平台 (feishu.cn)](https://open.feishu.cn/document/server-docs/docs/sheets-v3/spreadsheet-sheet/query?appId=cli_a6109595397dd00c)

[获取文件夹中的文件清单 - 服务端 API - 开发文档 - 飞书开放平台 (feishu.cn)](https://open.feishu.cn/document/server-docs/docs/drive-v1/folder/list?appId=cli_a6109595397dd00c)

而这就需要逐个了解以上3个接口来选择出最符合需求的那一个



---

除此之外

由于API文档不是同一个人写的，所以在不同的接口说明里，他们对于相同的事物的表述方式也可能会有差异：

[获取授权登录授权码 - 服务端 API - 开发文档 - 飞书开放平台 (feishu.cn)](https://open.feishu.cn/document/common-capabilities/sso/api/obtain-oauth-code)



在“获取授权登录授权码”这个接口中，文档的编写者使用了类似python中f-string的方式来标识需要我们自行替换的参数：

![image-20240807145106890](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240807145106890.png)



其中**{APPID}**这样的部分都需要被我们**整个替换**，包括大括号：

![image-20240807145249813](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240807145249813.png)

而且开发者将这些我们需要自主替换的部分称为“**查询参数**”：

![image-20240807145546615](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240807145546615.png)

[获取工作表 - 服务端 API - 开发文档 - 飞书开放平台 (feishu.cn)](https://open.feishu.cn/document/server-docs/docs/sheets-v3/spreadsheet-sheet/query?appId=cli_a6109595397dd00c)

但是在“**获取工作表**”这个接口的表达方式却是下面这样的：

![image-20240807145407831](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240807145407831.png)

对“需要自主替换的参数”的称呼也变了，变成了“路径参数”：

![image-20240807145721453](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240807145721453.png)

虽然是**一样的东西**但是**表述方式不同**，而且这个接口没有请求体示例，所以会有一些误导性



---

#### 使用chatgpt整理

好处是搭建环境的部分跟着chatgpt基本不会出错，坏处是chatgpt可能会在写代码时使用**旧版本中的接口**

建议

- 增加提示词，要求chatgpt“向控制台中输出日志记录”，如果发现其使用了“不存在的接口”，方便后续手动修改

- 使用chatgpt写一些场景简单的**可用**代码作为示例，了解含义后照葫芦画瓢

- 参考官方示例代码

  

---

## 通用的前置流程

### 获取token

步骤一般不会特别繁琐，比如飞书API要求应用在**操作工作表之前**先获得**user_access_token**

**获取user_access_token的流程：**

1.使用接口获取app_access_token

2.用户点击链接后授权，随后应用获取到登陆预授权码

3.将app_access_token和app_access_token传递给接口，获取user_access_token

**像上面这样的流程，直接交给chatgpt完成代码也不会有问题**

---

### 开放权限

**以飞书举例**

为应用申请权限需要在控制台内进行操作：

![image-20240807153615947](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240807153615947.png)

**注意修改权限后，需要发布应用版本才可以使修改生效**



**以telegram的群组管理bot举例**

功能是“在群组成员发送广告信息时将其移出群组”，所以需要先为bot增加管理员权限

---

## 必要时考虑对API封装过的第三方库

### telegram相关

这里有一个对telegram API封装了的库：[python-telegram-bot 文档](https://python-telegram-bot.readthedocs.io/en/stable/)

对于群组管理和消息转发这两个bot来说有些大材小用

### 飞书相关

[songquanpeng/one-api: OpenAI 接口管理 & 分发系统，支持 Azure、Anthropic Claude、Google PaLM 2 & Gemini、智谱 ChatGLM、百度文心一言、讯飞星火认知、阿里通义千问、360 智脑以及腾讯混元，可用于二次分发管理 key，仅单可执行文件，已打包好 Docker 镜像，一键部署，开箱即用. OpenAI key management & redistribution system, using a single API for all LLMs, and features an English UI. (github.com)](https://github.com/songquanpeng/one-api)

使用One API可以使app在国内调用Open AI API：



## 







