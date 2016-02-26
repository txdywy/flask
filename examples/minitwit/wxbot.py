#!/usr/bin/env python
# coding=utf-8
from __future__ import print_function

#in case of using json.dumps with ensure_ascii=False 
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from pprint import pprint
from functools import wraps

import os
try:
    from urllib import urlencode, quote_plus
except ImportError:
    from urllib.parse import urlencode, quote_plus

try:
    import urllib2 as wxb_urllib
    from cookielib import CookieJar
except ImportError:
    import urllib.request as wxb_urllib
    from http.cookiejar import CookieJar

import re
import time
import xml.dom.minidom
import json
import math
import subprocess
import ssl
import thread
import urllib2

try:
    from config import WX_TULING_API_KEY
except:
    print('-----------------no TULING api key--------------')
    WX_TULING_API_KEY = ''
WX_TULING_API_URL = 'http://www.tuling123.com/openapi/api?key=' + WX_TULING_API_KEY + '&info=%s'


DEBUG = False
IS_SERVER = False
ROBOT_ON = False

MAX_GROUP_NUM = 35  # 每组人数
INTERFACE_CALLING_INTERVAL = 20  # 接口调用时间间隔, 间隔太短容易出现"操作太频繁", 会被限制操作半小时左右
MAX_PROGRESS_LEN = 50

SERVER_QR_PATH = os.path.join(os.getcwd(), 'static/qrcode.jpg')
QRImagePath = os.path.join(os.getcwd(), 'qrcode.jpg')

tip = 0
uuid = ''

base_uri = ''
redirect_uri = ''
push_uri = ''

skey = ''
wxsid = ''
wxuin = ''
pass_ticket = ''
deviceId = 'e000000000000000'

BaseRequest = {}

ContactList = []
My = []
SyncKey = []
MemberList = []
MemberMap = {}
ALERT_MEMBER = []
ALERT_LAST_MSG_FROM = {}
ALERT_LAST_MSG_REPLY = {}
ALERT_FLAG = False

try:
    xrange
    range = xrange
except:
    # python 3
    pass


def ex(default=0):
    def wrapper(fn):
        @wraps(fn)
        def func(*args, **kwds):
            try:
                r = fn(*args, **kwds)
            except Exception, e:
                r = default
                print('[%s][%s]' % (fn.__name__, str(e)))
                #print traceback.format_exc()
            return r
        return func
    return wrapper


def pace(fn):
    @wraps(fn)
    def func(*args, **kwds):
        t0 = time.time()
        r = fn(*args, **kwds)
        t = time.time() - t0
        print('---%s: %ss---' % (fn.__name__, t)) 
        return r


def show():
    print('ROBOT_ON: %s' % ROBOT_ON)


def robot_on():
    global ROBOT_ON
    ROBOT_ON = True


def robot_off():
    global ROBOT_ON
    ROBOT_ON = False


ALERT_TIMEOUT = 60 * 1
def check_alert():
    now = time.time()
    for k in ALERT_LAST_MSG_FROM:
        if (now-ALERT_LAST_MSG_FROM[k])>ALERT_TIMEOUT and not ALERT_FLAG:
            if k not in ALERT_LAST_MSG_REPLY:
                return True
            if k in ALERT_LAST_MSG_REPLY and ALERT_LAST_MSG_REPLY[k] < ALERT_LAST_MSG_FROM[k]:
                return True
    return False


def init_alert():
    add_alert('Tingting')


def clean_alert():
    global ALERT_MEMBER
    global ALERT_LAST_MSG_FROM
    global ALERT_LAST_MSG_REPLY
    global ALERT_FLAG
    ALERT_FLAG = False
    ALERT_MEMBER = []
    ALERT_LAST_MSG_FROM = {}
    ALERT_LAST_MSG_REPLY = {}
    show_alert()


def re_alert():
    global ALERT_LAST_MSG_FROM, ALERT_LAST_MSG_REPLY, ALERT_FLAG
    ALERT_FLAG = False
    ALERT_LAST_MSG_FROM = {}
    ALERT_LAST_MSG_REPLY = {}
    show_alert()


def show_alert():
    print('ALERT_FLAG: ', ALERT_FLAG)
    print('ALERT_MEMBER: ', ALERT_MEMBER)
    print('ALERT_LAST_MSG_FROM: ', ALERT_LAST_MSG_FROM)
    print('ALERT_LAST_MSG_REPLY: ', ALERT_LAST_MSG_REPLY)


def start_alert():
    global ALERT_FLAG
    print('*' * 20 + '大王呼叫,全体集合!' + '*' * 20)
    ALERT_FLAG = True
    if sys.platform.find('darwin') >= 0:
        subprocess.call(['open', 'alert.mp3'])
    else:
        os.startfile('alert.mp3')


def send_alert():
    if My:
        send('大王来啦!!!', My['NickName'])


def responseState(func, BaseResponse):
    ErrMsg = BaseResponse['ErrMsg']
    Ret = BaseResponse['Ret']
    if DEBUG or Ret != 0:
        print('func: %s, Ret: %d, ErrMsg: %s' % (func, Ret, ErrMsg))

    if Ret != 0:
        return False

    return True


def add_alert(nickname=None):
    global ALERT_MEMBER
    if nickname:
        ALERT_MEMBER.append(nickname)
       

def to8(u):
    if type(u)==str:
        return u
    if type(u)==unicode:
        return u.encode('utf8')
    return ''


def toU(s):
    if type(s)==str:
        return s.decode('utf8')
    if type(s)==unicode:
        return s
    return u''


def getRequest(url, data=None):
    """
     #this is to ensure the data is in utf-8, not any /uxxxx style string produced by json.dumps. Generally, browser with a meta header will handle /uxxxx style unicode well. However it seems wechat handle /uxxxx with its repr not encoding ones.
    if type(data) == unicode, it works well
    else (str), exception will pass and finally will handle str data
    """
    try:
        data = data.encode('utf-8') 
    except:
        pass
    finally:
        return wxb_urllib.Request(url=url, data=data)


def getUUID():
    global uuid

    url = 'https://login.weixin.qq.com/jslogin'
    params = {
        'appid': 'wx782c26e4c19acffb',
        'fun': 'new',
        'lang': 'zh_CN',
        '_': int(time.time()),
    }

    request = getRequest(url=url, data=urlencode(params))
    response = wxb_urllib.urlopen(request)
    data = response.read().decode('utf-8', 'replace')

    # print(data)

    # window.QRLogin.code = 200; window.QRLogin.uuid = "oZwt_bFfRg==";
    regx = r'window.QRLogin.code = (\d+); window.QRLogin.uuid = "(\S+?)"'
    pm = re.search(regx, data)

    code = pm.group(1)
    uuid = pm.group(2)

    if code == '200':
        return True

    return False


def showQRImage():
    global tip

    url = 'https://login.weixin.qq.com/qrcode/' + uuid
    params = {
        't': 'webwx',
        '_': int(time.time()),
    }

    request = getRequest(url=url, data=urlencode(params))
    response = wxb_urllib.urlopen(request)

    tip = 1

    global IS_SERVER
    if sys.platform.find('linux') >= 0:
        IS_SERVER = True
    if IS_SERVER:
        with open(SERVER_QR_PATH, 'wb') as f:
            f.write(response.read())
        print('请扫码二维码登录,地址 http://alancer.ml/qrcode.jpg')
        
    else:
        f = open(QRImagePath, 'wb')
        f.write(response.read())
        f.close()

        if sys.platform.find('darwin') >= 0:
            subprocess.call(['open', QRImagePath])
        elif sys.platform.find('linux') >= 0:
            subprocess.call(['xdg-open', QRImagePath])
        else:
            os.startfile(QRImagePath)

        print('请使用微信扫描二维码以登录')


def waitForLogin():
    global tip, base_uri, redirect_uri, push_uri

    url = 'https://login.weixin.qq.com/cgi-bin/mmwebwx-bin/login?tip=%s&uuid=%s&_=%s' % (
        tip, uuid, int(time.time()))

    request = getRequest(url=url)
    response = wxb_urllib.urlopen(request)
    data = response.read().decode('utf-8', 'replace')

    # print(data)

    # window.code=500;
    regx = r'window.code=(\d+);'
    pm = re.search(regx, data)

    code = pm.group(1)

    if code == '201':  # 已扫描
        print('成功扫描,请在手机上点击确认以登录')
        tip = 0
    elif code == '200':  # 已登录
        print('正在登录...')
        regx = r'window.redirect_uri="(\S+?)";'
        pm = re.search(regx, data)
        redirect_uri = pm.group(1) + '&fun=new'
        base_uri = redirect_uri[:redirect_uri.rfind('/')]

        # push_uri与base_uri对应关系(排名分先后)(就是这么奇葩..)
        services = [
            ('wx2.qq.com', 'webpush2.weixin.qq.com'),
            ('qq.com', 'webpush.weixin.qq.com'),
            ('web1.wechat.com', 'webpush1.wechat.com'),
            ('web2.wechat.com', 'webpush2.wechat.com'),
            ('wechat.com', 'webpush.wechat.com'),
            ('web1.wechatapp.com', 'webpush1.wechatapp.com'),
        ]
        push_uri = base_uri
        for (searchUrl, pushUrl) in services:
            if base_uri.find(searchUrl) >= 0:
                push_uri = 'https://%s/cgi-bin/mmwebwx-bin' % pushUrl
                break

        # closeQRImage
        if sys.platform.find('darwin') >= 0:  # for OSX with Preview
            os.system("osascript -e 'quit app \"Preview\"'")
    elif code == '408':  # 超时
        pass
    # elif code == '400' or code == '500':

    return code


def login():
    global skey, wxsid, wxuin, pass_ticket, BaseRequest

    request = getRequest(url=redirect_uri)
    response = wxb_urllib.urlopen(request)
    data = response.read().decode('utf-8', 'replace')

    # print(data)

    doc = xml.dom.minidom.parseString(data)
    root = doc.documentElement

    for node in root.childNodes:
        if node.nodeName == 'skey':
            skey = node.childNodes[0].data
        elif node.nodeName == 'wxsid':
            wxsid = node.childNodes[0].data
        elif node.nodeName == 'wxuin':
            wxuin = node.childNodes[0].data
        elif node.nodeName == 'pass_ticket':
            pass_ticket = node.childNodes[0].data

    # print('skey: %s, wxsid: %s, wxuin: %s, pass_ticket: %s' % (skey, wxsid,
    # wxuin, pass_ticket))

    if not all((skey, wxsid, wxuin, pass_ticket)):
        return False

    BaseRequest = {
        'Uin': int(wxuin),
        'Sid': wxsid,
        'Skey': skey,
        'DeviceID': deviceId,
    }

    return True


def webwxinit():

    url = base_uri + \
        '/webwxinit?pass_ticket=%s&skey=%s&r=%s' % (
            pass_ticket, skey, int(time.time()))
    params = {
        'BaseRequest': BaseRequest
    }

    request = getRequest(url=url, data=json.dumps(params))
    request.add_header('ContentType', 'application/json; charset=UTF-8')
    response = wxb_urllib.urlopen(request)
    data = response.read()

    if DEBUG:
        f = open(os.path.join(os.getcwd(), 'webwxinit.json'), 'wb')
        f.write(data)
        f.close()

    data = data.decode('utf-8', 'replace')

    #print(data)

    global ContactList, My, SyncKey
    dic = json.loads(data)
    ContactList = dic['ContactList']
    My = dic['User']
    SyncKey = dic['SyncKey']

    state = responseState('webwxinit', dic['BaseResponse'])
    return state


def webwxgetcontact():

    url = base_uri + '/webwxgetcontact?pass_ticket=%s&skey=%s&r=%s' % (pass_ticket, skey, int(time.time()))

    request = getRequest(url=url)
    request.add_header('ContentType', 'application/json; charset=UTF-8')
    response = wxb_urllib.urlopen(request)
    data = response.read()

    if DEBUG:
        f = open(os.path.join(os.getcwd(), 'webwxgetcontact.json'), 'wb')
        f.write(data)
        f.close()

    # print(data)
    data = data.decode('utf-8', 'replace')

    dic = json.loads(data)
    MemberList = dic['MemberList']
    return MemberList

def special_user():
    # 倒序遍历,不然删除的时候出问题..
    SpecialUsers = ["newsapp", "fmessage", "filehelper", "weibo", "qqmail", "tmessage", "qmessage", "qqsync", "floatbottle", "lbsapp", "shakeapp", "medianote", "qqfriend", "readerapp", "blogapp", "facebookapp", "masssendapp", "meishiapp", "feedsapp", "voip", "blogappweixin", "weixin", "brandsessionholder", "weixinreminder", "wxid_novlwrv3lqwv11", "gh_22b87fa7cb3c", "officialaccounts", "notification_messages", "wxitil", "userexperience_alarm"]
    for i in range(len(MemberList) - 1, -1, -1):
        Member = MemberList[i]
        if Member['VerifyFlag'] & 8 != 0:  # 公众号/服务号
            MemberList.remove(Member)
        elif Member['UserName'] in SpecialUsers:  # 特殊账号
            MemberList.remove(Member)
        elif Member['UserName'].find('@@') != -1:  # 群聊
            MemberList.remove(Member)
        elif Member['UserName'] == My['UserName']:  # 自己
            MemberList.remove(Member)

    return MemberList


def createChatroom(UserNames):
    MemberList = [{'UserName': UserName} for UserName in UserNames]

    url = base_uri + \
        '/webwxcreatechatroom?pass_ticket=%s&r=%s' % (
            pass_ticket, int(time.time()))
    params = {
        'BaseRequest': BaseRequest,
        'MemberCount': len(MemberList),
        'MemberList': MemberList,
        'Topic': '',
    }

    request = getRequest(url=url, data=json.dumps(params))
    request.add_header('ContentType', 'application/json; charset=UTF-8')
    response = wxb_urllib.urlopen(request)
    data = response.read().decode('utf-8', 'replace')

    # print(data)

    dic = json.loads(data)
    ChatRoomName = dic['ChatRoomName']
    MemberList = dic['MemberList']
    DeletedList = []
    BlockedList = []
    for Member in MemberList:
        if Member['MemberStatus'] == 4:  # 被对方删除了
            DeletedList.append(Member['UserName'])
        elif Member['MemberStatus'] == 3:  # 被加入黑名单
            BlockedList.append(Member['UserName'])

    state = responseState('createChatroom', dic['BaseResponse'])

    return ChatRoomName, DeletedList, BlockedList


def deleteMember(ChatRoomName, UserNames):
    url = base_uri + \
        '/webwxupdatechatroom?fun=delmember&pass_ticket=%s' % (pass_ticket)
    params = {
        'BaseRequest': BaseRequest,
        'ChatRoomName': ChatRoomName,
        'DelMemberList': ','.join(UserNames),
    }

    request = getRequest(url=url, data=json.dumps(params))
    request.add_header('ContentType', 'application/json; charset=UTF-8')
    response = wxb_urllib.urlopen(request)
    data = response.read().decode('utf-8', 'replace')

    # print(data)

    dic = json.loads(data)

    state = responseState('deleteMember', dic['BaseResponse'])
    return state


def addMember(ChatRoomName, UserNames):
    url = base_uri + \
        '/webwxupdatechatroom?fun=addmember&pass_ticket=%s' % (pass_ticket)
    params = {
        'BaseRequest': BaseRequest,
        'ChatRoomName': ChatRoomName,
        'AddMemberList': ','.join(UserNames),
    }

    request = getRequest(url=url, data=json.dumps(params))
    request.add_header('ContentType', 'application/json; charset=UTF-8')
    response = wxb_urllib.urlopen(request)
    data = response.read().decode('utf-8', 'replace')

    # print(data)

    dic = json.loads(data)
    MemberList = dic['MemberList']
    DeletedList = []
    BlockedList = []
    for Member in MemberList:
        if Member['MemberStatus'] == 4:  # 被对方删除了
            DeletedList.append(Member['UserName'])
        elif Member['MemberStatus'] == 3:  # 被加入黑名单
            BlockedList.append(Member['UserName'])

    state = responseState('addMember', dic['BaseResponse'])

    return DeletedList, BlockedList


def syncKey():
    SyncKeyItems = ['%s_%s' % (item['Key'], item['Val'])
                    for item in SyncKey['List']]
    SyncKeyStr = '|'.join(SyncKeyItems)
    return SyncKeyStr


def syncCheck():
    url = push_uri + '/synccheck?'
    params = {
        'skey': BaseRequest['Skey'],
        'sid': BaseRequest['Sid'],
        'uin': BaseRequest['Uin'],
        'deviceId': BaseRequest['DeviceID'],
        'synckey': syncKey(),
        'r': int(time.time()),
    }

    request = getRequest(url=url + urlencode(params))
    response = wxb_urllib.urlopen(request)
    data = response.read().decode('utf-8', 'replace')

    print('心跳', data)

    # window.synccheck={retcode:"0",selector:"2"}
    regx = r'window.synccheck={retcode:"(\d+)",selector:"(\d+)"}'
    pm = re.search(regx, data)

    retcode = pm.group(1)
    selector = pm.group(2)

    return retcode, selector


def get_member(username):
    if username == My['UserName']:
        return My
    return MemberMap.get(username)


def webwxsync():
    global SyncKey

    url = base_uri + '/webwxsync?lang=zh_CN&skey=%s&sid=%s&pass_ticket=%s' % (
        BaseRequest['Skey'], BaseRequest['Sid'], quote_plus(pass_ticket))
    params = {
        'BaseRequest': BaseRequest,
        'SyncKey': SyncKey,
        'rr': ~int(time.time()),
    }

    request = getRequest(url=url, data=json.dumps(params))
    request.add_header('ContentType', 'application/json; charset=UTF-8')
    response = wxb_urllib.urlopen(request)
    data = response.read().decode('utf-8', 'replace')
    
    #print('-'*50)
    #print('收信', data)
    #print('='*50)

    d = json.loads(data)#.replace('\n', ''))
    global test, ALERT_LAST_MSG_FROM, ALERT_LAST_MSG_REPLY
    test = d
    if d[u"AddMsgCount"]>0:

        msgs = d["AddMsgList"]
        #print('收信', data)
        print('收信了:>>>>>>>>>>>>>>>>>>>>>>')
        for msg in msgs:
            m_fr = get_member(msg[u"FromUserName"])
            m_to = get_member(msg[u"ToUserName"])
            u_fr = m_fr["NickName"] if m_fr else msg[u"FromUserName"]
            u_to = m_to["NickName"] if m_to else msg[u"ToUserName"]
            content = msg.get("Content", "")
            #print('====raw====')
            ##print(msg)
            #pprint(msg)
            #print('----raw----')
            array = content.split(':<br/>')
            if len(array) == 1:
                content = array[0]
                user = None
            else:
                content = content[len(array[0])+6:]
                user_id = array[0]
                member = MemberMap.get(user_id)
                user = member['NickName'] if member else '非我好友'
            msg_type =  msg.get('MsgType')
            msg_content = '[%s]' % content if not user else '[%s]@[%s]' % (user, content)
            if msg_type in (51, 49, ): #51: enter a room  #49: news push
                print('A Msg[%s]' % msg_type)
            else:
                print(u'[%s]->[%s]: ' % (u_fr, u_to), msg_content, '[Msg:%s]'%str(msg_type))
            if u_fr in ALERT_MEMBER:
                print('<<<<<<<<<<<<<<<<<<<<<大王来啦!快接驾!!!>>>>>>>>>>>>>>>>>>>>')
                ALERT_LAST_MSG_FROM[u_fr] = time.time()
            if u_to in ALERT_MEMBER:
                ALERT_LAST_MSG_REPLY[u_to] = time.time()
            if ROBOT_ON and My['NickName']==u_to and u_to!=u_fr:
                if msg[u"FromUserName"] in MemberMap:
                    bot_re = tre(content)
                    send(bot_re, u_fr)
                    print('我自动回复[%s]-->[%s]' % (u_to, bot_re))
            if u_to==u_fr:
                if 'robot on' in content:
                    robot_on()
                if 'robot off' in content:
                    robot_off()

    dic = json.loads(data)
    SyncKey = dic['SyncKey']

    state = responseState('webwxsync', dic['BaseResponse'])
    return state


def heartBeatLoop():
    while True:
        ret, selector = syncCheck()
        if ret == '1100':
            print('Err Code 1100 and exit system.')
            sys.exit(0)
        if selector != '0':
            webwxsync()
        time.sleep(1)
        if check_alert():
            start_alert()


test=0
def send(content, target_nickname):
    global test
    content = toU(content)
    target_nickname = toU(target_nickname)
    for i in MemberList:
        if i['NickName']==target_nickname:
            to = i
            break
    ts = time.time()
    tid = str(int(ts * 10000000))
    url = base_uri + '/webwxsendmsg?pass_ticket=%s&r=%s' % (pass_ticket, int(ts))
    params = {
        'BaseRequest': BaseRequest,
        'Msg': {
            'ClientMsgId': tid, 
            'Content': content,
            'FromUserName': My['UserName'],
            'LocalID': tid,
            'ToUserName': to['UserName'],
            'Type': 1,
        }
    }

    #print('----params----',params)
    data=json.dumps(params, ensure_ascii=False)
    request = getRequest(url=url, data=data)
    #print('====data====',data)
    request.add_header('ContentType', 'application/json; charset=UTF-8')
    response = wxb_urllib.urlopen(request)
    data = response.read().decode('utf-8', 'replace')
    #test=data
    d = json.loads(data.replace('\n', ''))
    if d[ u'BaseResponse'][u'Ret']==0:
        print('消息送达')
    else:
        print('消息失败[%s]' % d[ u'BaseResponse'][u'Ret'])
        print('send result:', data)
    #print('===send===data', data)


def main(server=False):
    global IS_SERVER
    global MemberList, MemberMap
    if server:
        IS_SERVER = True
    try:
        ssl._create_default_https_context = ssl._create_unverified_context
    except Exception, e:
        print('ssl模块加载问题', str(e))
        
    opener = wxb_urllib.build_opener(wxb_urllib.HTTPCookieProcessor(CookieJar()))
    opener.addheaders = [('User-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.125 Safari/537.36')]
    wxb_urllib.install_opener(opener)

    if not getUUID():
        print('获取uuid失败')
        return

    print('正在获取二维码图片...')
    showQRImage()
    time.sleep(1)

    while waitForLogin() != '200':
        pass

    if IS_SERVER:
        os.remove(SERVER_QR_PATH)
    else:
        os.remove(QRImagePath)

    if not login():
        print('登录失败')
        return
    else:
        print('登录成功')

    if not webwxinit():
        print('初始化失败')
        return
    else:
        print('初始化胜利')

    MemberList = webwxgetcontact()
    MemberMap = {m[u'UserName']: m for m in MemberList}

    print('开启心跳线程')
    thread.start_new_thread(heartBeatLoop, ())

    MemberCount = len(MemberList)
    print('通讯录共%s位好友' % MemberCount)



def more():
    ChatRoomName = ''
    result = []
    d = {}
    for Member in MemberList:
        d[Member['UserName']] = (Member['NickName'].encode(
            'utf-8'), Member['RemarkName'].encode('utf-8'))
    print('开始查找...')
    group_num = int(math.ceil(MemberCount / float(MAX_GROUP_NUM)))
    for i in range(0, group_num):
        UserNames = []
        for j in range(0, MAX_GROUP_NUM):
            if i * MAX_GROUP_NUM + j >= MemberCount:
                break
            Member = MemberList[i * MAX_GROUP_NUM + j]
            UserNames.append(Member['UserName'])

        # 新建群组/添加成员
        if ChatRoomName == '':
            (ChatRoomName, DeletedList, BlockedList) = createChatroom(
                UserNames)
        else:
            (DeletedList, BlockedList) = addMember(ChatRoomName, UserNames)

        # todo BlockedList 被拉黑列表

        DeletedCount = len(DeletedList)
        if DeletedCount > 0:
            result += DeletedList

        # 删除成员
        deleteMember(ChatRoomName, UserNames)

        # 进度条
        progress = MAX_PROGRESS_LEN * (i + 1) / group_num
        print('[', '#' * progress, '-' * (MAX_PROGRESS_LEN - progress), ']', end=' ')
        print('新发现你被%d人删除' % DeletedCount)
        for i in range(DeletedCount):
            if d[DeletedList[i]][1] != '':
                print(d[DeletedList[i]][0] + '(%s)' % d[DeletedList[i]][1])
            else:
                print(d[DeletedList[i]][0])

        if i != group_num - 1:
            print('正在继续查找,请耐心等待...')
            # 下一次进行接口调用需要等待的时间
            time.sleep(INTERFACE_CALLING_INTERVAL)
    # todo 删除群组

    print('\n结果汇总完毕,20s后可重试...')
    resultNames = []
    for r in result:
        if d[r][1] != '':
            resultNames.append(d[r][0] + '(%s)' % d[r][1])
        else:
            resultNames.append(d[r][0])

    print('---------- 被删除的好友列表(共%d人) ----------' % len(result))
    # 过滤emoji
    resultNames = map(lambda x: re.sub(r'<span.+/span>', '', x), resultNames)
    if len(resultNames):
        print('\n'.join(resultNames))
    else:
        print("无")
    print('---------------------------------------------')


# windows下编码问题修复
# http://blog.csdn.net/heyuxuanzee/article/details/8442718


class UnicodeStreamFilter:

    def __init__(self, target):
        self.target = target
        self.encoding = 'utf-8'
        self.errors = 'replace'
        self.encode_to = self.target.encoding

    def write(self, s):
        if type(s) == str:
            s = s.decode('utf-8')
        s = s.encode(self.encode_to, self.errors).decode(self.encode_to)
        self.target.write(s)

if sys.stdout.encoding == 'cp936':
    sys.stdout = UnicodeStreamFilter(sys.stdout)

if __name__ == '__main__':

    print('本程序的查询结果可能会引起一些心理上的不适,请小心使用...')
    main()
    print('回车键退出...')


@ex('error')
def tre(words='你是谁'):
    r = urllib2.urlopen(WX_TULING_API_URL % words).read()
    return json.loads(r)['text']


main()
