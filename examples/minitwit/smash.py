# -*- coding: utf-8 -*-
import requests, sys, json
from pprint import pprint
import datetime
import pytz
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
    resources_gained = str(o['resources_gained']['1'])
    print resources_gained
    now = datetime.datetime.now(tz)
    try:
        qy_util.post('SMASH自动采集金币:' + resources_gained + '\n北京时间:' + str(now)[:19], touser=['txdywy'])
    except:
        print '没有微信推送'
    print 'SMASH自动采集金币:' + resources_gained



collect()
