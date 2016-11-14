# -*- coding: utf-8 -*-
import requests, sys, json
from pprint import pprint
import datetime
import pytz
from random import randint
import time
try:
    import qy_util
except:
    pass
tz = pytz.timezone('Asia/Shanghai')
bid = 'iUo0KQj6R2ghgZoObEXAxezvdHYzxwpZzwq7tI0Upu0Y3dXCP1GSkPP2IrQpZ/pICD2KISz0FC5jS4eDb57qBg=='
headers = {
    'Host': 'api.smash.athinkingape.com',
    'SquidAuthToken': 'Bearer id=' + bid,
    'Accept': '*/*',
    'Authorization': 'Bearer id=' + bid,
    'Content-Type': 'application/x-www-form-urlencoded',
    'ClientVersion': '91',
    'Accept-Language': 'en-us',
    'Accept-Encoding': 'gzip, deflate',
    'Content-Length': '0',
    'User-Agent': 'ata bundle_id=com.tofulabs.smash2 version=91',
    'Connection': 'keep-alive',
    'X-devilfish-api': '91',
    }


def collect():
    r = requests.post('https://199.167.22.55/game/city/collect_resources/', headers=headers, verify=False)
    t = r.text
    #print t
    o = json.loads(r.text)
    pprint(o)
    try:
        resources_gained = str(o['resources_gained']['1'])
    except Exception, e:
        str(e)
        qy_util.post(str(e) + '\n北京时间:' + str(now)[:19], toparty=['19'])
    print resources_gained
    now = datetime.datetime.now(tz)
    try:
        qy_util.post('SMASH自动采集金币:' + resources_gained + '\n北京时间:' + str(now)[:19], toparty=['19'])
    except Exception, e:
        print '没有微信推送'
        print str(e)
    print 'SMASH自动采集金币:' + resources_gained



#collect()

def random_collect(sample=4):
    s = randint(0, sample)
    print s
    if s == 0:
        time.sleep(s * 3)
        collect()
