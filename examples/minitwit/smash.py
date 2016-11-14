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

login_headers = {
    'Host': 'api.smash.athinkingape.com',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Connection': 'keep-alive',
    'X-devilfish-api': '91',
    'ClientVersion': '91',
    'Accept': '*/*',
    'User-Agent': 'ata bundle_id=com.tofulabs.smash2 version=91',
    'Content-Length': '967',
    'Accept-Language': 'en-us',
    'Accept-Encoding': 'gzip, deflate',
}


def login():
    payload = {
        'bundle_id': 'com.tofulabs.smash2',
        'channel_id': '12',
        'scope': '["all"]',
        'client_information': '{"hardware_version":"iPhone7,1","user_agent":"Mozilla\/5.0 (iPhone; CPU iPhone OS 10_1_1 like Mac OS X) AppleWebKit\/602.2.14 (KHTML, like Gecko) Mobile\/14B100","application_tracking_enabled":false,"os_version":"10.1.1","advertiser_tracking_enabled":true,"os_name":"iPhone OS","jailbroken":false,"openudid":"fbf3555669549c31a6ee20a998bb18459d6898d3","udid_vendor":"C82958F8-18DA-42AC-80A6-8E1DEC429174","udid_advertising":"53BEAE8D-3583-4B20-A185-29FAD155EDC6"}',
        'client_version': '91',
        'grant_type': 'refresh_token',
        'version': '1122',
        'asset_version': '1477513611',
        'client_secret': 'n0ts0s3cr3t',
        'client_id' : 'com.tofulabs.smash2',
        'refresh_token': 'cUfzZAQiGodEbS+4ckRP9NwM/Zt9NB2Y9ls+ju8TXs6Gjvw6COvS+kAJxZp3dHMpylsKdPZX2xbk4LTUz/v5og==',
    }
    r = requests.post('https://199.167.22.55/game/auth/login/', headers=login_headers, verify=False, data=payload)
    t = r.text
    #print t
    o = json.loads(r.text)
    pprint(o)


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
    print resources_gained
    now = datetime.datetime.now(tz)
    try:
        qy_util.post('SMASH自动采集金币:%s/%s' % (resources_gained, resources_total) + '\n能量值:%s/%s' % (energy_now, energy_cap) +'\n北京时间:' + str(now)[:19], toparty=['19'])
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
