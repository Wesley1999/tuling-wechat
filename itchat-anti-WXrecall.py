#!/usr/bin/python
# coding=utf-8

# 说明：可以撤回的有文字、语音、视频、图片（含包情包）、文件，其他类型会报错，但不影响继续运行

import itchat
from itchat.content import *
import sys
import time
import re
import os
import logging

reload(sys)
sys.setdefaultencoding('utf8')

msg_information = {}
# 针对表情包的内容
face_bug = None

# 这里要改成自己的openid，否则自己撤回的消息也会被处理
selfId = '@6ff54fff9520aff9181960cbc4ff03f84bd77d84742b3ee85b08507d4e2290db'

@itchat.msg_register([TEXT,PICTURE,FRIENDS,CARD,MAP,SHARING,RECORDING,ATTACHMENT,VIDEO],isFriendChat=True,isGroupChat=True)
def receive_msg(msg):
    # 永不监听自己的消息
    if msg['FromUserName'] == selfId:
        return
    global face_bug
    # 接收消息的时间
    msg_time_rec = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    if msg.has_key('ActualNickName'):
        # 群消息的发送者,用户的唯一标识
        from_user = msg['ActualUserName']
        # 发送者群内的昵称
        msg_from = msg['ActualNickName']

        # 获取所有的群
        groups = itchat.get_chatrooms(update=True)
        for g in groups:
            # 根据群消息的FromUserName匹配是哪个群
            if msg['FromUserName'] == g['UserName']:
                group_name = g['NickName']
                group_menbers = g['MemberCount']
                break
        group_name = group_name + "(" + str(group_menbers) +")"
    else:
        # 优先使用备注名称
        if itchat.search_friends(userName=msg['FromUserName'])['RemarkName']:
            msg_from = itchat.search_friends(userName=msg['FromUserName'])['RemarkName']
        else:
            # 在好友列表中查询发送信息的好友昵称
            msg_from = itchat.search_friends(userName=msg['FromUserName'])['NickName']
        group_name = ""
    # 信息发送的时间
    msg_time = msg['CreateTime']
    # 每条信息的id
    msg_id = msg['MsgId']
    # 储存信息的内容
    msg_content = None
    # 储存分享的链接，比如分享的文章和音乐
    msg_share_url = None
    # 如果发送的消息是文本或者好友推荐
    if msg['Type'] == 'Text' or msg['Type'] == 'Friends':
        msg_content = msg['Text']

    # 如果发送的消息是附件、视频、图片、语音
    elif msg['Type'] == "Attachment" or msg['Type'] == "Video" or msg['Type'] == 'Picture' or msg['Type'] == 'Recording':
        # 内容就是他们的文件名
        msg_content = msg['FileName']
        # 下载文件
        msg['Text']('files/' + str(msg_content))
        
    summary = msg_time_rec + ' ' + group_name + ' ' + msg_from + '('+ msg['FromUserName'] +'): (' + msg['Type'] + ') ' + msg_content
    logging.info(summary)
        
    msg_information.update({
                            msg_id: {
                                "msg_from": msg_from,
                                "msg_time": msg_time,
                                "msg_time_rec": msg_time_rec,
                                "msg_type": msg["Type"],
                                "msg_content": msg_content,
                                "msg_share_url": msg_share_url,
                                "group_name":group_name,
                                "FromUserName": msg['FromUserName'],
                                "summary": summary
                                }
                            })
    
    # 删除时间超过5分钟的消息记录
    now_timestamp = int(time.time())
    for key in msg_information.keys():
        msg_timestamp = int(msg_information[key]['msg_time'])
        if now_timestamp - msg_timestamp > 300:
            msg_information.pop(key)
            

# 监听撤回消息
@itchat.msg_register(NOTE, isFriendChat=True, isGroupChat=True)
def information(msg):
    # 永不监听自己的消息
    if msg['FromUserName'] == selfId:
        return
    # 这里如果这里的msg['Content']中包含消息撤回和id，就执行下面的语句
    if '撤回了一条消息' in msg['Content']:
        # 在返回的content查找撤回的消息的id
        old_msg_id = re.search("\<msgid\>(.*?)\<\/msgid\>", msg['Content']).group(1)
        # 获取到消息原文
        old_msg = msg_information.get(old_msg_id)
        
        logging.info('监听到一条撤回的消息--> ' + old_msg['summary']);
        itchat.send('监听到一条撤回的消息-->\n' + old_msg['summary'], toUserName='filehelper')
        
        # 发送撤回的消息
        if old_msg['msg_type'] == 'Text':
            msg_body = old_msg.get('msg_from') + " 撤回了一条消息：\n" + old_msg.get('msg_time_rec') + "\n" + old_msg.get('msg_content')
            itchat.send(msg_body, old_msg['FromUserName'])
        elif old_msg['msg_type'] == 'Picture':
            msg_body = old_msg.get('msg_from') + " 撤回了一张图片：\n" + old_msg.get('msg_time_rec') + "\n" + old_msg.get('msg_content')
            itchat.send(msg_body, old_msg['FromUserName'])
            itchat.send_image('files/' + old_msg.get('msg_content'), old_msg['FromUserName'])
        elif old_msg['msg_type'] == 'Video':
            msg_body = old_msg.get('msg_from') + " 撤回了一个视频：\n" + old_msg.get('msg_time_rec') + "\n" + old_msg.get('msg_content')
            itchat.send(msg_body, old_msg['FromUserName'])
            itchat.send_video('files/' + old_msg.get('msg_content'), old_msg['FromUserName'])
        elif old_msg['msg_type'] == 'Recording':
            msg_body = old_msg.get('msg_from') + " 撤回了一条语音：\n" + old_msg.get('msg_time_rec') + "\n" + old_msg.get('msg_content')
            itchat.send(msg_body, old_msg['FromUserName'])
            itchat.send_file('files/' + old_msg.get('msg_content'), old_msg['FromUserName'])
        elif old_msg['msg_type'] == 'Attachment':
            msg_body = old_msg.get('msg_from') + " 撤回了一个文件：\n" + old_msg.get('msg_time_rec') + "\n" + old_msg.get('msg_content')
            if check_contain_chinese(old_msg.get('msg_content')):
                msg_body = msg_body + old_msg.get('msg_content') + "\n因文件名含中文，无法重新发送"
            itchat.send(msg_body, old_msg['FromUserName'])
            itchat.send_file(u'files/' + old_msg.get('msg_content'), old_msg['FromUserName'])
        else:
            msg_body = old_msg.get('msg_from') + " 撤回了一条消息，该消息类型暂时不支持：\n" + old_msg.get('msg_time_rec') + "\n" + old_msg.get('msg_content')
            itchat.send(msg_body, old_msg['FromUserName'])
            
def check_contain_chinese(check_str):
    for ch in check_str.decode('utf-8'):
        if u'\u4e00' <= ch <= u'\u9fff':
            return True
    return False
    
    

if(not os.path.exists('files')):
    os.mkdir('files')
if(not os.path.exists('log')):
    os.mkdir('log')
logging.basicConfig(level=logging.INFO, filename='log/recall.log')
itchat.auto_login(hotReload=True,enableCmdQR=2)
itchat.run()
