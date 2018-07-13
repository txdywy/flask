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
from bs4 import BeautifulSoup
import time
import pytz
import stock
import psutil
import threading
import Queue
import datetime
from okc import Client as okcc
from hb.Util import *
from hb import HuobiService as hbs
tz = pytz.timezone('Asia/Shanghai')
try:
    from config import QY_KEY, QY_TOKEN, QY_CORPID, QY_SECRET
    from config import JKB_KEY, JKB_TOKEN, JKB_CORPID, JKB_SECRET
except Exception, e:
    print '--------------------------', str(e)  
    QY_KEY = QY_TOKEN = QY_CORPID = QY_SECRET = ''

QY_MSG_CRYPT = WXC.WXBizMsgCrypt(QY_TOKEN, QY_KEY, QY_CORPID)
JKB_MSG_CRYPT = WXC.WXBizMsgCrypt(JKB_TOKEN, JKB_KEY, JKB_CORPID)


QY_TEXT = """
<xml>
   <ToUserName><![CDATA[{to_user}]]></ToUserName>
   <FromUserName><![CDATA[{fr_user}]]></FromUserName> 
   <CreateTime>{timestamp}</CreateTime>
   <MsgType><![CDATA[text]]></MsgType>
   <Content><![CDATA[{content}]]></Content>
</xml>
"""

class QyAsyncTask(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.tasks = Queue.Queue()
        self.setDaemon(True)
        print '=====thread init====='

    def put(self, d):
        if not self.isAlive():
            try:
                self.start()
                print '-----thread started-----'
            except Exception, e:
                print '-----thread failed-----', str(e)
        self.tasks.put(d)

    def run(self):
        while True:
            try:
                d = self.tasks.get(timeout=1)
                if d:
                    cm = sys.modules[__name__]
                    x = getattr(cm, d)
                    x()
                print '=====thread task done===='
            except Exception, e:
                #print '-----threading err-----', str(e)
                pass
            time.sleep(5)

QY_ASYNC_THREAD = QyAsyncTask()



class QYMsgProcess(object):

    def __init__(self, data, signature, timestamp, nonce, cat=0):
        self.data = data
        self.signature = signature
        self.timestamp = timestamp
        self.nonce = nonce
        if cat==0:
            MC = QY_MSG_CRYPT
        if cat==1:
            MC = JKB_MSG_CRYPT
        ret, content = MC.DecryptMsg(data, signature, timestamp, nonce)
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
        text = post(msg.content, toparty=['5', '7', '9', '11', '13', '14']).text
    else:
        #text = '还没实现event[%s]哦' % str(msg.event)
        text = ''
    return msg.re_text(text)


def jkb_reply(data, msg_signature, timestamp, nonce):
    msg = QYMsgProcess(data, msg_signature, timestamp, nonce, cat=1)
    msg.show()
    if '群发' in msg.content:
        text = post(msg.content, appid=4, toparty=['5', '21']).text
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
        #smash.refresh()
    else:
        s = '❌停止自动收集,开始游戏'
        rcache.set('smash_collect', '')
    return s


def get_sys_info():
    s0 = "CPU[%s/100] MEM[%s/100]\n" % (psutil.cpu_percent(), psutil.virtual_memory().percent)
    mem = psutil.virtual_memory().percent
    if mem > 70:
        from fabric.api import local
        local('pgrep python | xargs kill -9')
        s1 = "CPU[%s/100] MEM[%s/100]\n" % (psutil.cpu_percent(), psutil.virtual_memory().percent)
    else:
        s1 = "MEM is OK\n"
    ############################
    #temp google play rank check
    ############################
    #a = fetch_rank(start=50) + fetch_rank(start=300) + fetch_rank(start=200)
    #a=[i for i in a if 'super win' in i or 'Mega Win Vegas' in i or ('Free Vegas Casino' in i and 'Lucky' not in i) or 'Wonderful Wizard of Oz' in i]
    QY_ASYNC_THREAD.put('rank_test')
    ############################
    return s0 + s1 + '\n异步任务随后推送...\n'


TARGETS = {'com.superwin.freeslots': 'super win',
           'com.fleetcommander.ships': 'Fleet Commander:Pacific',
           'com.megawin.vegas.slots.free': 'Mega Win Vegas Casino Slots',
           'com.absolutist.casinoabs': 'Free Vegas Casino',
           'net.RocketSpeed.WonderfulWizardSlots': 'Wonderful Wizard of Oz Slots',
           'com.huuuge.freespins': 'Casino™',
           'com.casino.vip.deluxe.free.slot': 'Casino VIP Deluxe - Free Slot',
           #'com.yiihua.teenpatti': 'TEEN PATTI MASTER - LIVE!',
           'com.oasgames.mugua.mlomgen6': 'Trial Of Heroes: Online RPG',
           'com.megarama.magicslots': 'Magic Slots Free',
           'slots.popnplay.twindragons': 'Twin Dragons Slot Machine',
          }


def fetch_revst(pkg='casino.classic.grandwin.vegas.slots.free.andriod'):
    u = 'https://play.google.com/store/apps/details?id={pkg}'.format(pkg=pkg)
    r = requests.get(url=u, verify=False).text
    s = BeautifulSoup(r)
    a = s.find("div", { "class" : 'rating-box'})
    sc = a.find("div", { "class" : 'score-container'}).findAll("meta")
    rate, votes_total = [getattr(i, 'attrs')['content'] for i in sc]
    rh = a.find("div", { "class" : 'rating-histogram'}).findAll("div")
    votes = [i.find("span", { "class" : 'bar-number'}).text.replace(',', '') for i in rh]
    print rate, votes_total, votes
    return [rate, votes_total] + votes


def get_app_rv():
    result = []
    for k in TARGETS:
        x = fetch_revst(k)
        result.append([TARGETS[k]] + x)
    print result
    r = [tuple([i[0], float(i[1]), i[2]] + [100*float(t)/float(i[2]) for t in i[3:]]) for i in result]
    pprint(r)
    r = ['[%s][%.2f][%s][%2d%%,%2d%%,%2d%%,%2d%%,%2d%%]\n' % i for i in r]
    #'[%s][%.2f][%s][%.2f%%,%.2f%%,%.2f%%,%.2f%%,%.2f%%]\n'
    return ''.join(r)


def rank_test():
    t0 = time.time()
    a = []
    b = []
    p = []
    q = []
    u = []
    m = []
    for i in [1, 100, 200, 300, 400, 500]:
        a += fetch_rank(start=i) 
        q += fetch_rank(start=i, cat='GAME_ROLE_PLAYING', country='ca')
        u += fetch_rank(start=i, cat='GAME_ROLE_PLAYING', country='de') 
        b += fetch_rank(start=i, cat='GAME_CASINO', country='my')
        p += fetch_rank(start=i, cat='GAME_ROLE_PLAYING', country='sg')
        m += fetch_rank(start=i, cat='GAME_CASINO', country='us')
    #a = fetch_rank(start=1) + fetch_rank(start=100) + fetch_rank(start=300) + fetch_rank(start=200) + fetch_rank(start=400) + fetch_rank(start=500)
    a=[i+'[au]' for i in a if 'Twin Dragons Slot Machine' in i or 'Magic Slots Free' in i or 'TEEN PATTI MASTER - LIVE!' in i or 'super win' in i or 'Mega Win Vegas' in i or ('Free Vegas Casino' in i and 'Lucky' not in i and '-' not in i and 'Party' not in i) or 'Wonderful Wizard of Oz' in i or 'Casino VIP Deluxe - Free Slot' in i or ('Casino™' in i and 'Slots' not in i and 'SLOTS' not in i)]
    q=[i+'[ca]' for i in q if 'Fleet Commander:Pacific' in i]
    u=[i+'[de]' for i in u if 'Trial Of Heroes: Online RPG' in i]
    b=[i+'[my]' for i in b if 'super win' in i]
    p=[i+'[sg]' for i in p if 'Trial Of Heroes: Online RPG' in i]
    m=[i+'[us]' for i in m if 'super win' in i or 'Mega Win Vegas' in i]

    a += (b + p + q + u + m)
    #c = [get_app_rv()]
    t1 = time.time()
    t = unicode(datetime.datetime.now(tz))[:19]
    print t, t1-t0
    #post('[%s]\n[%ss]\n' % (t, t1-t0) + '\n'.join(c), appid=3, toparty=['20'])
    post('[%s]\n[%ss]\n' % (t, t1-t0) + '\n'.join(a), appid=3, toparty=['20'])


def fetch_rank(start=400, num=100, cat='GAME_CASINO', country='au'):
    u='https://play.google.com/store/apps/category/{cat}/collection/topselling_free?gl={country}&authuser=0'.format(cat=cat, country=country)
    a='start={start}&num={num}&numChildren=0&cctcss=square-cover&cllayout=NORMAL&ipf=1&xhr=1&token=pLa9Popn4u2QqG2_5u6thgzjxsI%3A1486387681054'.format(start=start,num=num)
    b=a.split('&')
    d=[i.split('=') for i in b]
    d={i[0]:i[1] for i in d}
    r=requests.post(url=u,data=d,verify=False).text
    s=BeautifulSoup(r)
    a=s.findAll("div", { "class" : "card" })
    a=[i.findAll('a')[1].attrs['aria-label'] for i in a]
    #a=[i for i in a if 'super win' in i or 'Mega Win Vegas' in i or 'Free Vegas Casino' in i]
    return a


def get_btc():
    from cache import rcache
    x = rcache.get('BTC')
    if not x:
        x = str(stock.blockchain())
        rcache.set('BTC', x, 60)        
        post(x, appid=3, toparty=['20'])
        return '...'
    return x

    okc_status = json.loads(okcc.get_status())
    total = okc_status['info']['funds']['asset']['total']
    free = okc_status['info']['funds']['free']
    result = 'okc status:\n'
    result += 'total: ' + total + '\n'
    result += '\n'.join(['%s: %s'%(k,free[k]) for k in free])
    result +='\n\n'
    ps = [(i,okcc.get_price(co=i)['ticker']) for i in ['btc','eth','ltc']]
    ps = [x[0] + '\n' + x[1]['last'] + '\n' + x[1]['low'] + '+%s' % _diff(x[1]['last'], x[1]['low']) + '\n' + x[1]['high'] + '-%s' % _diff(x[1]['high'], x[1]['last']) + '\n'  for x in ps]
    result += '\n'.join(ps)
    result += '\n--------------------\n\n'
    result += 'hb status:\n'
    hb_status = hbs.getAccountInfo(ACCOUNT_INFO)
    hb_btc = hb_status['available_btc_display']
    hb_ltc = hb_status['available_ltc_display']
    hb_total = hb_status['total']
    hb_cny = hb_status['available_cny_display']
    hb_btc_frozen = hb_status['frozen_btc_display']
    result += 'btc: ' + hb_btc + '\n'
    result += 'ltc: ' + hb_ltc + '\n'
    result += 'cny: ' + hb_cny + '\n'
    result += 'btc_pend: ' + hb_btc_frozen + '\n'
    result += 'total: ' + hb_total + '\n'
    return result + '\n\n'


def _diff(a, b):
    return round(float(a) - float(b), 3)


def get_battle():
    #import smash 
    #return smash.auto_battle()
    return get_sys_info()


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
    elif 'btc' == msg.event_key:
        text = get_btc()
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
             "21": "AdOps",
             "22": "股神",
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
    #post('[建议]大家最近是不是很少用Phabricator了...大家有什么推动code review方面的建议呢？', toparty=['5'])
    pass


def bz_alert():
    data = stock.get_bz_cn_stock()
    result = []
    for d in data:
        target = d[1]
        price = float(d[3])
        if price <= target + 0.5:
            result.append(d)
    print result
    if result:
        result = [r[2]+':'+r[3]+'/'+str(r[1]) for r in result]
        result.append('上述股票已达到买入点')
        result.append(unicode(datetime.datetime.now(tz))[:19])
        result = '\n'.join(result)
        post(str(result), appid=1000002, toparty=['22'])
    















