# -*- coding: utf-8 -*-
import wx_crypt.WXBizMsgCrypt as WXC
import xml.etree.ElementTree as ET
import time
from pprint import pprint
import requests
try:
    from config import QY_KEY, QY_TOKEN, QY_CORPID
except Exception, e:
    print '--------------------------', str(e)  
    QY_KEY = QY_TOKEN = QY_CORPID = ''

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
    else:
        text = '还没实现哦'
    return msg.re_text(text)


