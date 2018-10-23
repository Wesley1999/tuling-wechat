from time import sleep

import requests
import itchat
import re
import pymysql

key = 'd98dbc8b2f784ceb9e11640b87283a62' # 这里是你自己机器人的apikey
nickName = '小兔几' # 这里是昵称或群昵称，用于检测群聊是否被艾特
conn = pymysql.connect(host='localhost', user='root', passwd='123456', db='python')
cur = conn.cursor()

# 获取回复的内容
def get_response(msg):
    try:
        # 先从数据库查找
        pattern = re.compile('teach,.*,.*')
        match = pattern.match(msg)
        if match != None:
            receive = re.findall(r',(.+),', msg)
            reply = re.findall(r',.+,(.+)', msg)
            teach(receive[0], reply[0])
            return "学到了"
        sql = "select reply from tuling where receive='" + msg + "'"
        cur.execute(sql)
        r, = cur.fetchone()
        if r != None:
            print('==================================================')
            print('收到消息：', msg)
            print('回复消息：', r)
            return r
    except:
        pass

    # 数据库中没有再到图灵服务器上找
    # 构造要发送给服务器的数据
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
    sleep(2)
    return reply

# 处理群聊消息
@itchat.msg_register(itchat.content.TEXT, isGroupChat=True)
def tuling_reply(msg):
    # 针对手机版
    pattern = re.compile('.*@' + nickName + '( ).*')
    match = pattern.match(msg['Text'])
    # 被艾特才回复
    if match != None:
        # 去掉艾特和名字，以此作为收到的消息
        r = msg['Text'].replace('@' + nickName + " ", '')
        reply = get_response(r)
        sleep(2)
        return reply

    # 针对电脑版
    pattern = re.compile('.*@' + nickName + '( ).*')
    match = pattern.match(msg['Text'])
    # 被艾特才回复
    if match != None:
        # 去掉艾特和名字，以此作为收到的消息
        r = msg['Text'].replace('@' + nickName + " ", '')
        reply = get_response(r)
        sleep(2)
        return reply

    # 针对艾特放在最后
    pattern = re.compile('.*@' + nickName + '$')
    match = pattern.match(msg['Text'])
    # 被艾特才回复
    if match != None:
        # 去掉艾特和名字，以此作为收到的消息
        r = msg['Text'].replace('@' + nickName, '')
        reply = get_response(r)
        sleep(2)
        return reply

# 教我说话。格式是（teach,收到的消息,回复的消息），英文逗号隔开，后面没有空格
def teach(receive, reply):
    sql = "select * from tuling where receive='" + receive + "' "
    cur.execute(sql)
    rs = cur.fetchone()
    if rs==None:
        sql2 = "insert into tuling(receive, reply) values('" + receive + "', '" + reply+ "')"
    else:
        sql2 = "update tuling set reply='" + reply + "' where receive='" + receive + "'"
    cur.execute(sql2)
    conn.commit()

# 为了让实验过程更加方便（修改程序不用多次扫码），我们使用热启动
itchat.auto_login(hotReload=True)
itchat.run()
# 运行结束后关闭数据库连接
cur.close()
conn.close()