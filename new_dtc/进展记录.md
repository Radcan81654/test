[TOC]

![image-20240730175200166](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240730175200166.png)

![image-20240730175232427](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240730175232427.png)

目前怀疑的点是我目前可能根本就没有把密钥填进去，甚至从一开始就不应该导入openai这个模块，一切提出请求都应该直接先改url后组织报文,测试之后发现自己想的是对的

[API Reference - OpenAI API](https://platform.openai.com/docs/api-reference/making-requests)









####  项目代码



##### Linux端

```python
#关于重定向
#导入Flask类和request对象,Flask类用于创建Flask应用程序实例，request对象用于处理客户端发送的请求
from flask import Flask, request
#创建一个Flask应用程序实例，并将当前模块的名称（__name__）作为参数传递给Flask构造函数。Flask使用这个参数来确定应用程序的根目录，从而找到资源文件。
app = Flask(__name__)
#以下两行代码定义了一个路由和相应的处理函数。当客户端发送一个GET请求到/redirect路径时，Flask将调用handle_redirect函数处理请求
@app.route('/redirect')
def handle_redirect():
    #从请求的查询字符串中获取名为code的参数。如果URL是/redirect?code=12345，那么code变量将被赋值为'12345'。如果code参数不存在，则code变量将是None。
    code = request.args.get('code')
    if code:
        return f'预授权码: {code}'
    else:
        return '未能获取预授权码', 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)


```

```
#关于One API的部署
```





##### Windows端

![image-20240730142330208](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240730142330208.png)![image-20240730142343467](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240730142343467.png)

```python
import requests
import pandas
import openai
import time
import datetime

from urllib.parse import urlparse, parse_qs
APP_ID='cli_a6109595397dd00c'
APP_SECRET='4kvnWi7eSELx5lLyQv7NkgsRJMoBL8yc'
REDIRECT_URI = 'http://123.56.166.61/redirect'  # 云服务器的重定向地址
SRC_SPREADSHEET_TOKEN='RbqqsliPPhYvRUtQgeCcZ5hxnzg'
SRC_SHEET_TITLE='Sheet1'
DST_SHEET_TITLE='Sheet2'
USER_ID='g68857da'
OPENAI_API_BASE='http://localhost:3000'
OPENAI_API_KEY='sk-J5fhnUmY1GeAxq5H3c3102F815174f639b95A012816a526e'
#自定义开始行数
MY_BEGIN=1726
MY_END=1731


#OPENAI_API_BASE='https://aiserver.marsyoo.com/'
#OPENAI_API_KEY='sk-uB4cBeoA8HZLOQ9K62965eD12531414d9d4fDe04Ca81418'



#成功时返回需要的报文，失败时返回-1
#获取user_access_token
def get_access_token(app_id, app_secret):
    url = 'https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal'
    headers = {'Content-Type': 'application/json'}
    payload = {
        'app_id': app_id,
        'app_secret': app_secret
    }
    response = requests.post(url, json=payload, headers=headers)#
    response_data = response.json()
    if response_data['code']!=0:
        return -1
    return response_data['app_access_token']
def get_authorization_url(app_id, redirect_uri):
    url = f"https://open.feishu.cn/open-apis/authen/v1/index?app_id={app_id}&redirect_uri={redirect_uri}&response_type=code&scope=snsapi_userinfo"
    return url

def extract_pre_auth_code(redirected_url):#拿到登陆预授权码
    parsed_url = urlparse(redirected_url)
    query_params = parse_qs(parsed_url.query)
    pre_auth_code = query_params.get('code', [None])[0]
    return pre_auth_code

def get_user_access_token(app_access_token,pre_auth_code):
    url='https://open.feishu.cn/open-apis/authen/v1/access_token'
    headers = {'Authorization':f'Bearer {app_access_token}',
               'Content-Type': 'application/json'}
    payload = {
        'grant_type': 'authorization_code',
        'code': pre_auth_code
    }
    response = requests.post(url, json=payload, headers=headers)  #
    response_data=response.json()
    if response_data['code']!=0:
        return -1
    return response_data['data']['access_token']
##################################################################
#读取[begin行,end行]这个区间内的信息,其中begin从1开始
def get_src_sheet_rows(spreadsheet_token, user_access_token):
    #先想办法提取src_sheet一共有多少行
    url = f"https://open.feishu.cn/open-apis/sheets/v3/spreadsheets/{spreadsheet_token}/sheets/query"
    headers = {
        "Authorization": f"Bearer {user_access_token}",
    }
    rsp = requests.get(url, headers=headers)
    if rsp.json()['code'] != 0:
        print("获取rows失败\n")
        return -1
    sheets_val = rsp.json()['data']['sheets']
    #list = []
    if sheets_val[0]['title'] == SRC_SHEET_TITLE:
        rows=sheets_val[0]['grid_properties']['row_count']
        #list.append(sheets_val[0]['sheet_id'])
        #list.append(sheets_val[1]['sheet_id'])
    else:
        rows = sheets_val[1]['grid_properties']['row_count']
        #list.append(sheets_val[1]['sheet_id'])
        #list.append(sheets_val[0]['sheet_id'])

    return rows

#把读取出来的报文组织成想要的，能直接向chatgpt提问的格式
def organize_data(report):
    organized_data = []
    value_range = report.get('valueRange', {}).get('values', [])

    for entry in value_range:
        for content in entry:
            if isinstance(content, list):
                for item in content:
                    if item.get('type') == 'mention':
                        link = item.get('link', '')
                        text = item.get('text', '')
                        organized_data.append([link, text, '', ''])

    return organized_data
#generate_summary的返回值是可以直接拿出来插入到飞书中的内容
def generate_summary(data):
    #答案是根本不存在api_base这个成员,必须自己重头组织url
    url=f"{OPENAI_API_BASE}/v1/chat/completions"

    #初始化对对OpenAI模型的指示，告诉模型将要处理的内容和任务。这段指示文本是一个引导，帮助模型理解接下来的内容
    prompt = "以下是一些文章的链接和对应标题，请根据链接总结出每个文章的关键词(2个)、摘要(不少于30字)和更新日志,并按照形如[['链接1','关键字a,关键字b','摘要1','更新日志1'],['链接2','关键字c,关键字d','摘要2','更新日志2']]的顺序和格式回答,无有效内容时回答[]\n\n"
    # 遍历 data 列表中的每个 item,将每个 item 中的链接和文本信息追加到 prompt 字符串中
    for item in data:
        prompt += f"链接: {item[0]}\n内容: {item[1]}\n\n"
    headers = {
        'Authorization': f'Bearer {OPENAI_API_KEY}',
        'Content-Type':'application/json'
    }
    payload = {
        "model": "gpt-4o",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    response = requests.post(url, json=payload, headers=headers)
    rsp = response.json()
    content=rsp['choices'][0]['message']['content']

    try:
        content_list=eval(content)
        return content_list
    except (SyntaxError,KeyError):
        #对应一点信息也提取不出来的情况，对应非法区间状态
        return -314


#直接复用了以上三个函数
#使用的接口本质上是对已有表格进行更新，所以必须保证dst_sheet有大于等于src_sheet的行数
def insert_src_sheet(spreadsheet_token, user_access_token,begin,end):
    # 先想办法提取src_sheet一共有多少行
    flag=0
    url = f"https://open.feishu.cn/open-apis/sheets/v3/spreadsheets/{spreadsheet_token}/sheets/query"
    headers = {
        "Authorization": f"Bearer {user_access_token}",
    }
    rsp = requests.get(url, headers=headers)
    if rsp.json()['code'] != 0:
        print("获取rows失败\n")
        return -1
    sheets_val = rsp.json()['data']['sheets']
    list = []
    if sheets_val[0]['title'] == SRC_SHEET_TITLE:
        rows = sheets_val[0]['grid_properties']['row_count']
        list.append(sheets_val[0]['sheet_id'])
        list.append(sheets_val[1]['sheet_id'])
    else:
        rows = sheets_val[1]['grid_properties']['row_count']
        list.append(sheets_val[1]['sheet_id'])
        list.append(sheets_val[0]['sheet_id'])
    # 注意拿到的rows就是行数
    # 开始更新闭区间内的数据
    if begin < 2:
        print("begin非法\n")
        return -1
    #修改的还是局部变量
    #if begin > rows:
        #区间非法
        #return -314

    #if end > rows:
        #end = rows

    #rows很可能是在插入表格时就确定的，清数据不改变rows但是直接用删除选项会改变rows
    #能解释源spreadsheet和副本行数不同的现象
    #结论是rows并不可靠,不如直接看元素
    #################################################
    q = f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values/{list[0]}!B{begin}:B{end}"
    headers = {
        "Authorization": f"Bearer {user_access_token}",
        "Content-Type": "application/json; charset=utf-8"
    }
    w = requests.get(q, headers=headers)
    e = w.json()
    if e['code'] != 0:
        print("读取表格内容失败\n")
        print(e['msg'])
        return -1
    raw_data= e['data']

    ogn_data=organize_data(raw_data)
    content=[]
    content=generate_summary(ogn_data)
    if content==-314:
        return -314
    csz=len(content)
    end = begin + csz
    if(csz==0):
        return -314
    ######################################################################
    # 到这里拿到了两个工作表的id:list[],srcsheet行数rows
    # 以及openai组织好的可以直接插入表格的content
    #print(content)#success
    ##############插入数据以后的部分：
    url=f'https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values'
    headers={
        'Authorization': f'Bearer {user_access_token}',
        'Content-Type': 'application/json; charset=utf-8'
    }

    payload={
        'valueRange':{
            'range':f'{list[1]}!A{begin}:E{end}',
            'values':content
        }
    }
    rsp=requests.put(url, json=payload, headers=headers)
    if rsp.json()['code'] == 0 & end-begin==5:
        print(f'{begin}-{end}行写入成功\n')
        # print(rsp.json())
        return 0
    elif rsp.json()['code']==0&end-begin>0:
        print(f'{begin}-{end}行写入成功\n')
        return end-begin
    elif rsp.json()['code']==0&end-begin==0:
        print(f'{begin}-{end}行写入成功\n')
        return -159
    else:
        print(rsp.json()['msg'])
        #print(rsp)
        return -1
###############################################################################3
#模块直接把src_sheet里的所有内容全部导入到新表格
def moudle_start():
    # 获取 app_access_token
    access_token = get_access_token(APP_ID, APP_SECRET)  # app_access_token
    # 提取预授权码
    authorization_url = get_authorization_url(APP_ID, REDIRECT_URI)
    print(f"请访问以下链接并授权：\n{authorization_url}")
    redirected_url = input("请将授权后重定向的URL粘贴到这里：\n")
    pre_auth_code = extract_pre_auth_code(redirected_url)
    # 获取user_access_token
    user_access_token = get_user_access_token(access_token, pre_auth_code)
    begin = MY_BEGIN
    end = MY_END
    finished=begin-1
    while 1:
        rows = get_src_sheet_rows(SRC_SPREADSHEET_TOKEN, user_access_token)
        #insert_src_sheet函数中设置了对[begin,end]区间的调整
        while begin<rows:
            k = insert_src_sheet(SRC_SPREADSHEET_TOKEN, user_access_token, begin, end)
            if k==0:
                finished=end
                begin=end+1
                end=begin+5
            if k>0:#正在更新的区间[begin,end]中包含边界
                finished=begin+k
                begin=finished+1
                end=begin
            elif k==-314:#有问题,对应的是"区间非法",begin大于有效行数边界的这种情况
                print(f'{begin}-{end}为非法区间')
                begin=finished+1
                end=begin

            elif k==-159:#对应的是经过一次“包含边界的情况”以后，手动调整的end==begin的状态
                finished=begin
                begin=begin+1
                end=end+1
                print(f'{begin}-{end}行内包含无效数据')
            else:
                print(f'[{begin},{end}]区间插入数据失败,正在重新获取user_access_token,请重新授权\n')
                access_token = get_access_token(APP_ID, APP_SECRET)  # app_access_token
                # 提取预授权码
                authorization_url = get_authorization_url(APP_ID, REDIRECT_URI)
                print(f"请访问以下链接并授权：\n{authorization_url}")
                redirected_url = input("请将授权后重定向的URL粘贴到这里：\n")
                pre_auth_code = extract_pre_auth_code(redirected_url)
                # 获取user_access_token
                user_access_token = get_user_access_token(access_token, pre_auth_code)
        #每10s检查一次表格是否需要再次更新
        time.sleep(10)
        print('工作表内容更新完毕')



if __name__ == "__main__":
    moudle_start()
```



---

##### 引入外部库和模块

这四条语句是 Python 中的导入语句，用于引入外部库和模块，这些库和模块提供了特定的功能，以便在你的程序中使用。下面是对每条语句的详细解释：

1. **`import requests`**：
    - 这条语句导入了 `requests` 库，它是一个用于发送 HTTP 请求的第三方库。使用 `requests` 库，你可以轻松地发送 GET、POST 等请求，并处理 HTTP 响应。
    - 示例用途：发送 HTTP GET 请求以从网页获取数据。
    ```python
    response = requests.get('https://api.example.com/data')
    data = response.json()
    ```

2. **`import pandas as pd`**：
    - 这条语句导入了 `pandas` 库，并将其简写为 `pd`。`pandas` 是一个强大的数据处理和分析库，特别擅长处理结构化数据（如表格数据）。
    - 示例用途：创建和操作数据框（DataFrame），读取和写入 CSV、Excel 文件等。
    ```python
    df = pd.read_csv('data.csv')
    print(df.head())
    ```

3. **`import openai`**：
    - 这条语句导入了 `openai` 库，该库提供了与 OpenAI API 交互的功能。使用 `openai` 库，你可以调用 OpenAI 的各种模型（如 GPT-3）来生成文本、完成任务等。
    - 示例用途：生成文本摘要或标签。
    ```python
    openai.api_key = 'your_openai_api_key'
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt="请生成一段介绍Python的文字。",
        max_tokens=100
    )
    print(response.choices[0].text.strip())
    ```

4. **`from datetime import datetime`**：
    - 这条语句从 `datetime` 模块中导入了 `datetime` 类。`datetime` 模块提供了用于处理日期和时间的各种功能。
    - 示例用途：获取当前日期和时间，格式化日期和时间。
    ```python
    current_time = datetime.now()
    print(current_time.strftime("%Y-%m-%d %H:%M:%S"))
    ```

通过导入这些库和模块，你可以在你的 Python 项目中使用它们提供的功能，简化许多任务的实现，例如发送网络请求、处理数据、生成文本和处理日期时间等。

---



# 环境搭建

## 安装第三方库



![image-20240729181932212](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240729181932212.png)

![image-20240729182228482](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240729182228482.png)

## 第三方库的使用

要查询 `openai`、`requests` 和 `pandas` 这些模块的具体使用文档，可以访问它们的官方网站或文档页面。以下是每个模块的详细文档链接和一些基本使用介绍：

### OpenAI

根本没用上

### Requests

#### 官方文档

- [Requests: HTTP for Humans](https://docs.python-requests.org/en/latest/)



```python
import requests

# 发送 GET 请求
response = requests.get('https://api.example.com/data')

# 检查响应状态码
if response.status_code == 200:
    data = response.json()  # 假设返回的是 JSON 数据
    print(data)
else:
    print("请求失败，状态码:", response.status_code)
```



- **Requests**:
  - [Requests 官方文档](https://docs.python-requests.org/en/latest/)
  - [Requests 快速入门](https://docs.python-requests.org/en/latest/user/quickstart/)

  





#### 获取app_access_token![image-20240729183732897](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240729183732897.png)

#### 获取user_access_token

### ![image-20240729194703705](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240729194703705.png)

#### 获取工作表token

![image-20240729212250799](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240729212250799.png)

#### 成功获取到[begin行，end行]内的数据

![image-20240729230246872](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240729230246872.png)

#### 成功组织报文

![image-20240730000845899](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240730000845899.png)

![image-20240730000857680](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240730000857680.png)



---

### 获取组织后的内容

![image-20240730181951368](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240730181951368.png)

加上缩进以后的报文内容：

```json
{
  "id": "chatcmpl-9qgVMVIXjTNNu8bxlkKWPA3PxX7nV",
  "object": "chat.completion",
  "created": 1722343472,
  "model": "gpt-4o-2024-05-13",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "[[https://bh5pm72xfy.feishu.cn/docx/EZkDdfGwxozlkJxndTCcsaUcnWb, 互联网, 经验, '真正有用的内容，其实就那么一两句！我做互联网十几年的经验之谈！', '更新日志：本文在2023年10月10日更新，增加了最新的互联网趋势分析。'],\n[https://oprlej7lc1.feishu.cn/docx/CxCtd6w1Po931NxxIH9cZOZnnPc, 财商, 组局, '财商局：让圈友直呼牛逼，再来一局的组局到底长啥样？？？泉州组局官的复盘', '更新日志：2023年10月11日更新，增加了泉州组局官最新的复盘内容。'],\n[https://dakhb269es.feishu.cn/docx/YWNxdt1z1oY0V3xXFJtcbgLqnPg, 思维导图, 生财, '生财思维课图谱：37张竖屏思维导图，解锁生财新思维', '更新日志：2023年10月12日更新，增加了三张新的思维导图。'],\n[https://balfcirt91j.feishu.cn/docx/WhxFdnUWBovLe3xzM2tcmCHfnhe, 抖音, 短视频, '拆解了30条万赞的抖音同城探店短视频后，我用ChatGPT做了一个同城探店短视频文案助手', '更新日志：2023年10月13日更新，优化了文案助手的功能。'],\n[https://auytvnjzru.feishu.cn/docx/NUpfdpeRpoCZvPxNkUOcCo2JnCh, 文案, 工具, '文案号，如何快速生成精美文章，一秒1000篇，附工具', '更新日志：2023年10月14日更新，增加了新的文案生成工具。'],\n[https://yxn0b6ntbk9.feishu.cn/wiki/B4USwEzoFixuxtkAQoHc4ZNTnOd, 裸辞, 创业, '97年小白裸辞做宠物定制工艺品从零到200万的感悟', '更新日志：2023年10月15日更新，分享了更多创业心路历程。']]"
      },
      "logprobs": null,
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 495,
    "completion_tokens": 551,
    "total_tokens": 1046
  },
  "system_fingerprint": "fp_4e2b2da518"
}


```



![image-20240730205041265](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240730205041265.png)



### 把组织之后的内容插入到目标表格中

这里一方面需要先注意组织出来的数据必须是list，然后进行content=[]这个初始化用来接收对应类型的数据，然后再手动组织报文：

```python
def insert_src_sheet(spreadsheet_token, user_access_token,begin,end):
    # 先想办法提取src_sheet一共有多少行
    flag=0
    url = f"https://open.feishu.cn/open-apis/sheets/v3/spreadsheets/{spreadsheet_token}/sheets/query"
    headers = {
        "Authorization": f"Bearer {user_access_token}",
    }
    rsp = requests.get(url, headers=headers)
    if rsp.json()['code'] != 0:
        print("获取rows失败\n")
        return -1
    sheets_val = rsp.json()['data']['sheets']
    list = []
    if sheets_val[0]['title'] == SRC_SHEET_TITLE:
        rows = sheets_val[0]['grid_properties']['row_count']
        list.append(sheets_val[0]['sheet_id'])
        list.append(sheets_val[1]['sheet_id'])
    else:
        rows = sheets_val[1]['grid_properties']['row_count']
        list.append(sheets_val[1]['sheet_id'])
        list.append(sheets_val[0]['sheet_id'])
    # 注意拿到的rows就是行数
    # 开始更新闭区间内的数据
    if begin < 2:
        print("begin非法\n")
        return -1

    #rows很可能是在插入表格时就确定的，清数据不改变rows但是直接用删除选项会改变rows
    #能解释源spreadsheet和副本行数不同的现象
    #结论是rows并不可靠,不如直接看元素
    #################################################
    q = f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values/{list[0]}!B{begin}:B{end}"
    headers = {
        "Authorization": f"Bearer {user_access_token}",
        "Content-Type": "application/json; charset=utf-8"
    }
    w = requests.get(q, headers=headers)
    e = w.json()
    if e['code'] != 0:
        print("读取表格内容失败\n")
        print(e['msg'])
        return -1
    raw_data= e['data']

    ogn_data=organize_data(raw_data)
    content=[]
    content=generate_summary(ogn_data)
    if content==-314:
        return 0
    #len为返回content里面元素的个数
    
    csz=len(content)
    #[1727,1731]返回5个元素
    end = begin + csz - 1
    if(csz==0):
        return 0
    ######################################################################
    # 到这里拿到了两个工作表的id:list[],srcsheet行数rows
    # 以及openai组织好的可以直接插入表格的content
    #print(content)#success
    ##############插入数据以后的部分：
    url=f'https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values'
    headers={
        'Authorization': f'Bearer {user_access_token}',
        'Content-Type': 'application/json; charset=utf-8'
    }

    payload={
        'valueRange':{
            'range':f'{list[1]}!A{begin}:E{end}',
            'values':content
        }
    }
    rsp=requests.put(url, json=payload, headers=headers)
    if rsp.json()['code'] == 0 :
        print(f'{begin}-{end}行写入成功\n')
        #返回成功写入的行数
        return csz

    else:
        print(rsp.json()['msg'])
        #print(rsp)
        return -1

```



![image-20240730214032002](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240730214032002.png)

### 完成循环

```python
def moudle_start():
    # 获取 app_access_token
    access_token = get_access_token(APP_ID, APP_SECRET)  # app_access_token
    # 提取预授权码
    authorization_url = get_authorization_url(APP_ID, REDIRECT_URI)
    print(f"请访问以下链接并授权：\n{authorization_url}")
    redirected_url = input("请将授权后重定向的URL粘贴到这里：\n")
    pre_auth_code = extract_pre_auth_code(redirected_url)
    # 获取user_access_token
    user_access_token = get_user_access_token(access_token, pre_auth_code)
    begin = MY_BEGIN
    end = MY_END
    finished=begin-1
    while 1:
        rows = get_src_sheet_rows(SRC_SPREADSHEET_TOKEN, user_access_token)
        #insert_src_sheet函数中设置了对[begin,end]区间的调整
        while begin<=rows:
            #k为从开始的位置开始读了多少行
            k = insert_src_sheet(SRC_SPREADSHEET_TOKEN, user_access_token, begin, end)
            if k==0:
                break
            elif k>0:#正在更新的区间[begin,end]中包含边界
                #[1327,1331]返回的是5
                finished=begin+k-1
                begin=finished+1
                if k==5:
                    end=begin+5-1
                elif k>0&k<5:
                    #到边界了,不能再读了
                    end=begin

            #发现一旦k!=0,数据更新就会停止
            else:
                print(f'[{begin},{end}]区间插入数据失败,正在重新获取user_access_token,请重新授权\n')
                access_token = get_access_token(APP_ID, APP_SECRET)  # app_access_token
                # 提取预授权码
                authorization_url = get_authorization_url(APP_ID, REDIRECT_URI)
                print(f"请访问以下链接并授权：\n{authorization_url}")
                redirected_url = input("请将授权后重定向的URL粘贴到这里：\n")
                pre_auth_code = extract_pre_auth_code(redirected_url)
                # 获取user_access_token
                user_access_token = get_user_access_token(access_token, pre_auth_code)
        #每10s检查一次表格是否需要再次更新
        time.sleep(10)
        print('工作表内容更新完毕')



if __name__ == "__main__":
    moudle_start()


```



![image-20240731005612079](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240731005612079.png)

插入数据后发现可以实现自动更新:

![image-20240731030936197](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240731030936197.png)

![image-20240731031011334](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240731031011334.png)

![image-20240731031025703](C:\Users\15212\AppData\Roaming\Typora\typora-user-images\image-20240731031025703.png)