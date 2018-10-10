import requests
import itchat
import re

key = 'd98dbc8b2f784ceb9e11640b87283a62' # 这里是你自己的key
nickName = '大猫' # 这里是你自己的昵称，如果在修改了群昵称则填写你的群昵称

def get_response(msg):
    # 构造了要发送给服务器的数据
    apiUrl = 'http://www.tuling123.com/openapi/api'
    data = {'key': key, 'info': msg, 'userid' : 'wechat-robot'}
    r = requests.post(apiUrl, data=data).json()
    # 字典的get方法在字典没有'text'值的时候会返回None而不会抛出异常
    print('==================================================')
    print('收到消息：', msg)
    print('回复消息：', r.get('text'))
    return r.get('text')

# 处理私聊消息
@itchat.msg_register(itchat.content.TEXT)
def tuling_reply(msg):
    reply = get_response(msg['Text'])
    return reply

# 处理群聊消息
@itchat.msg_register(itchat.content.TEXT, isGroupChat=True)
def tuling_reply(msg):
    pattern = re.compile('.*@' + nickName + '.*')
    match = pattern.match(msg['Text'])
    # 被艾特才回复
    if match!=None:
        # 去掉艾特和名字，以此作为收到的消息
        r = msg['Text'].replace('@' + nickName, '')
        reply = get_response(r)
        return reply

# 为了让实验过程更加方便（修改程序不用多次扫码），我们使用热启动
itchat.auto_login(hotReload=True)
itchat.run()