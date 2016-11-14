# -*- coding: utf-8 -*-
import requests, sys, json
from pprint import pprint
import datetime
import pytz
from random import randint
import time
try:
    import qy_util
    from cache import rcache
    bid = rcache.get('smash_bid', '')
except:
    bid = ''
    pass
tz = pytz.timezone('Asia/Shanghai')
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
        resources_gained = str(int(o['resources_gained']['1']))
        resources_total = str(int(o['resources']['1']))
        energy_now = str(int(o['game_user']['energy']))
        energy_cap = str(int(o['game_user']['energy_cap']))
    except Exception, e:
        str(e)
        qy_util.post(str(e) + '\n北京时间:' + str(now)[:19], toparty=['19'])
        return False
    print resources_gained
    now = datetime.datetime.now(tz)
    try:
        qy_util.post('SMASH自动采集金币:%s/%s' % (resources_gained, resources_total) + '\n能量值:%s/%s' % (energy_now, energy_cap) +'\n北京时间:' + str(now)[:19], toparty=['19'])
    except Exception, e:
        print '没有微信推送'
        print str(e)
    print 'SMASH自动采集金币:' + resources_gained
    return True



#collect()

def random_collect(sample=4):
    flag = rcache.get('smash_collect', None)
    if not flag:
        print '终止运行'
        return
    s = randint(0, sample)
    print s
    if s == 0:
        time.sleep(s * 3)
        f = collect()
        if not f:
            print 'bid0:' + bid
            t = login()
            print 'bid1:' + bid
        collect()



