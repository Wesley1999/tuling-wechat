#!/usr/bin/python
# coding=utf-8

from time import sleep

import requests
import itchat
import re
import os
import sys
import logging


reload(sys)
sys.setdefaultencoding('utf8')

key = ['1a337b641da04c64aa7fd4849a5f713e',
       '********************************',
       '********************************',
       '********************************',
       '********************************']
nickName = u'小兔几' # 这里是昵称或群昵称，用于检测群聊是否被艾特


# 获取回复的内容
def get_response(msg):
    key_index = 0
    text = '亲爱的，当天请求次数已用完。'
    while text == '亲爱的，当天请求次数已用完。' and key_index <= 4:
        # 构造要发送给服务器的数据
        apiUrl = 'http://www.tuling123.com/openapi/api'
        data = {'key': key[key_index], 'info': msg, 'userid' : 'wechat-robot'}
        r = requests.post(apiUrl, data=data).json()
        # 字典的get方法在字典没有'text'值的时候会返回None而不会抛出异常
        text = r.get('text')
        key_index = key_index + 1;
            
    logging.info('图灵------>request：' + msg + ", response:" + r.get('text'));
    return text

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


if(not os.path.exists('files')):
    os.mkdir('files')
if(not os.path.exists('log')):
    os.mkdir('log')
logging.basicConfig(level=logging.INFO, filename='log/recall.log')
itchat.auto_login(hotReload=True)
itchat.run()
