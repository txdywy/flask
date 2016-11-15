# -*- coding: utf-8 -*-
import sys
import json
reload(sys)
sys.setdefaultencoding('utf-8')
import wx_crypt.WXBizMsgCrypt as WXC
import xml.etree.ElementTree as ET
import time
from pprint import pprint
import requests
import time
import pytz
import stock
tz = pytz.timezone('Asia/Shanghai')
try:
    from config import QY_KEY, QY_TOKEN, QY_CORPID, QY_SECRET
except Exception, e:
    print '--------------------------', str(e)  
    QY_KEY = QY_TOKEN = QY_CORPID = QY_SECRET = ''

QY_MSG_CRYPT = WXC.WXBizMsgCrypt(QY_TOKEN, QY_KEY, QY_CORPID)


QY_TEXT = """
<xml>
   <ToUserName><![CDATA[{to_user}]]></ToUserName>
   <FromUserName><![CDATA[{fr_user}]]></FromUserName> 
   <CreateTime>{timestamp}</CreateTime>
   <MsgType><![CDATA[text]]></MsgType>
   <Content><![CDATA[{content}]]></Content>
</xml>
"""


class QYMsgProcess(object):

    def __init__(self, data, signature, timestamp, nonce):
        self.data = data
        self.signature = signature
        self.timestamp = timestamp
        self.nonce = nonce
        ret, content = QY_MSG_CRYPT.DecryptMsg(data, signature, timestamp, nonce)
        print '=============',content
        xml_recv = ET.fromstring(content)
        self.to_user, self.fr_user = self.re_fr_user, self.re_to_user = xml_recv.find("ToUserName").text, xml_recv.find("FromUserName").text
        try:self.event = xml_recv.find("Event").text
        except:self.event = None
        try:self.event_key = xml_recv.find("EventKey").text
        except:self.event_key = None
        try:self.content = xml_recv.find("Content").text
        except:self.content = ''

    
    def show(self):
        pprint(vars(self))

    def re_text(self, content):
        ts = int(time.time())
        content_xml = QY_TEXT.format(to_user=self.re_to_user, fr_user=self.re_fr_user, timestamp=ts, content=content)
        ret, result = QY_MSG_CRYPT.EncryptMsg(content_xml, self.nonce, self.timestamp)
        return result
            

def get_dsp_stat():
    data = requests.post('http://sandbox.appflood.com:1200/check')
    return data.json()['text']


def get_fmp_stat():
    data = requests.post('http://sandbox.appflood.com:1200/check_fmp')
    return data.json()['text']


def get_aff_stat():
    data = requests.post('http://sandbox.appflood.com:1200/check_aff') 
    return data.json()['text']


def reply(data, msg_signature, timestamp, nonce):
    msg = QYMsgProcess(data, msg_signature, timestamp, nonce)
    msg.show()
    if 'dsp' == msg.event_key:
        text = get_dsp_stat()
    elif 'fmp' == msg.event_key:
        text = get_fmp_stat()
    elif 'aff' == msg.event_key:
        text = get_aff_stat()
    elif '群发' in msg.content:
        text = post(msg.content).text
    else:
        #text = '还没实现event[%s]哦' % str(msg.event)
        text = ''
    return msg.re_text(text)


def get_poll():
    import ticket
    d = ticket.rank()[:5]
    return '\n'.join(['[第%s位]' % (n+1) + i[0]+':'+str(i[1]) + ' +%s' % (d[0][1]-i[1]) for n, i in enumerate(d)])


def set_ti():
    n = 100
    from wx_util import TICKET_ASYNC_THREAD
    if not TICKET_ASYNC_THREAD.isAlive():
        try:
            TICKET_ASYNC_THREAD.start()
            print '-----thread started-----'
        except Exception, e:
            print '-----thread failed-----', str(e)
    TICKET_ASYNC_THREAD.put(n)
    return '刷%s票中' % n


def get_px():
    import proxy
    return proxy.get_top_active() + '\n\nhttp://wxbot.ml/px'


def get_us_stock():
    import stock
    return stock.get_us_stock()


def get_cn_stock():
    import stock
    return stock.get_cn_stock()


def get_ec2():
    import fabfile
    d = fabfile.HOST_DATA
    t = []
    for k in d:
        t.append('[%s]' % k + '__%s__\n[%s][%s]\n' % d[k])
    return '\n'.join(t) 


def set_smash():
    from cache import rcache
    import smash
    f = rcache.get('smash_collect')
    if not f:
        s = '✅开始自动收集金币，停止游戏'
        rcache.set('smash_collect', '1')
        smash.refresh()
    else:
        s = '❌停止自动收集,开始游戏'
        rcache.set('smash_collect', '')
    return s


def get_battle():
    import smash 
    return smash.auto_battle()


def get_gold():
    import smash
    return smash.collect()


def hhmm_reply(data, msg_signature, timestamp, nonce):
    msg = QYMsgProcess(data, msg_signature, timestamp, nonce)
    msg.show()
    if 'poll' == msg.event_key:
        text = get_poll()
    elif 'ti' == msg.event_key:
        text = set_ti()
    elif 'px' == msg.event_key:
        text = get_px()
    elif 'us' == msg.event_key:
        text = get_us_stock()
    elif 'cn' == msg.event_key:
        text = get_cn_stock()
    elif 'haitian' == msg.event_key:
        text = stock.get_one_cn_stock('海天')
    elif 'vcel' == msg.event_key:
        text = stock.get_one_us_stock('vcel')
    elif 'ip' == msg.event_key:
        text = get_ec2()
    elif 'sm' == msg.event_key:
        text = set_smash()
    elif 'ba' == msg.event_key:
        text = get_battle()
        time.sleep(0.5)
        text = str(text) + '✔️ 还不能战✌️ '
    elif 'go' == msg.event_key:
        text = get_gold()
    else:
        #text = '还没实现event[%s]哦' % str(msg.event)
        text = ''
    print '==========',text
    return msg.re_text(text)


ACCESS_TOKEN_GROUP = (None, time.time())
def get_access_token():
    global ACCESS_TOKEN_GROUP
    ts =  time.time()
    if ACCESS_TOKEN_GROUP[1] < ts:
        url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={corpid}&corpsecret={secrect}'
        url = url.format(corpid=QY_CORPID, secrect=QY_SECRET)
        result = requests.get(url).json()
        ACCESS_TOKEN_GROUP = (result["access_token"], ts + result["expires_in"])
    return ACCESS_TOKEN_GROUP[0]


PARTY_MAP = {"2": "Appflood",
             "5": "EngineX",
             "6": "PM",
             "7": "TEST",
             "8": "OP",
             "9": "FrontX",
             "10": "DevOps",
             "11": "HR",
             "12": "Data",
             "13": "AntiSpam",
             }
def post(text, appid=2, touser=None, toparty=None):
    """
    party
    """
    #print '=========',type(text)
    if type(text) is unicode:
        text = text.encode('utf8')
    if not touser:
        touser = []
    if not toparty:
        toparty = ['2']
    url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}'
    url = url.format(access_token=get_access_token())
    data = {"touser": "|".join(touser),
            "toparty": "|".join(toparty),
            "msgtype": "text",
            "agentid": str(appid),
            "text": {"content": text},
            "safe": "0",
            }
    result = requests.post(url, data=json.dumps(data, ensure_ascii=False))
    print result.text
    return result


def friday_task():
    post('[提醒]请大家今天下班前记得提交自己的工作周报哦!', toparty=['5', '7', '9', '11', '13', '14'])


def monday_task():
    post('[提醒]请各组LEADER提交上周项目周报', toparty=['18'])


def saturday_task():
    pass
    #post('[提醒]友情提示提交周报:)', toparty=['5', '7', '9', '11', '13', '14'])


def thursday_task():
    post('[通知]请本周五下午分享的同学给大家提前发布一下分享内容,邮件请抄送appflood_engineer+pm_appflood+sa+data+as@papayamobile.com', toparty=['5', '7', '9', '11', '13', '14'])
    post('[通知]请将分享信息内容总结入这个Google表格:https://goo.gl/bHJ0T9', toparty=['5', '7', '9', '11', '13', '14'])


def fmp_cr():
    post('[提醒]工程师同学们今天code reviewO(∩_∩)O~ Phabricator工具用起来!', toparty=['5'])
