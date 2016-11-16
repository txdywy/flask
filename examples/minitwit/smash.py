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
    bid = rcache.get('smash_bid')
    from tqdm import tqdm
except:
    pass
bid = bid if bid else ''
print bid
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


def notify(s='默认信息😴 ', appid=3, toparty=None):
    if not toparty:
        toparty = ['20']
    now = datetime.datetime.now(tz)
    qy_util.post(s + '\n北京时间:' + str(now)[:19], appid=appid, toparty=toparty)


def reward(rid='13386436'):
    payload = {
        'repeat_bonus_id': rid,
        'version': '1126',
    }
    r = requests.post('https://199.167.22.55/game/store/collect_repeat_bonus/', headers=headers, verify=False, data=payload)
    t = r.text
    #print t
    o = json.loads(r.text)
    #pprint(o)
    return o


def auto_reward():
    flag = rcache.get('smash_collect')
    if not flag:
        print '终止运行'
        return
    o = reward()
    #pprint(o)
    if not o.get('exception'):
        text = '[🍊 ]SMASH自动收集奖励🏅 :' + i['headline']
        print text
        notify(s=text)
        time.sleep(1)
    ts = time.time()
    for i in o['pending_repeat_bonuses']:
        print '======'
        pprint(i)
        if i['next_collect_time'] < ts:
            x = reward(rid=str(i['id']))
            #pprint(x)
            if not x.get('exception'):
                text = 'SMASH自动收集奖励🏅 :' + i['headline']
                print text
                notify(s=text)
                time.sleep(1)
            else:
                text = 'SMASH自动收集奖励🏅失败了:' + i['headline']
                print text
                pprint(x)


def target():
    payload = {
        'hard_refresh': '1',
    }
    r = requests.post('https://199.167.22.55/game/battle/get_targets/', headers=headers, verify=False, data=payload)
    t = r.text
    #print t
    o = json.loads(r.text)
    #pprint(o)
    try:
        o['pvp_targets']
    except:
        print '获取不到敌人'
        pprint(o)        
        return 0 
    target_user_id, target_type, energy_cost, target_user = o['pvp_targets'][2]['target_user']['user_id'], o['pvp_targets'][2]['target_type'], o['pvp_targets'][2]['energy_cost'], o['pvp_targets'][2]['target_user']
    energy_base = o['game_user']['energy']
    energy_last_modified = o['game_user']['energy_last_modified']
    energy_regen_rate = o['game_user']['energy_regen_rate']
    energy = int(energy_base + (time.time() - energy_last_modified) / 60 / energy_regen_rate)
    print '================🔋', energy
    #energy = 100 # api can not get accurate value, currently
    if int(energy) < int(energy_cost):
        print '能量不足以战斗🔋 [%s/%s]' % (int(energy), int(energy_cost))
        return 1
    return target_user_id, target_type, energy_cost, target_user


def _cal_energy(o):
    energy_base = o['game_user']['energy']
    energy_last_modified = o['game_user']['energy_last_modified']
    energy_regen_rate = o['game_user']['energy_regen_rate']
    energy = int(energy_base + (time.time() - energy_last_modified) / 60 / energy_regen_rate)
    return energy


#print '=====',target()
def battle(target_user_id, target_type='2', energy_cost='6'):
    payload = [
        ('target_id', target_user_id),
        ('monster_id', '16988815'),
        ('monster_id', '16988814'),
        ('monster_id', '16992346'),
        ('target_type', target_type),
        ('time_when_attackable', str(int(time.time()))),
        ('version', '1126'),
    ]
    r = requests.post('https://199.167.22.55/game/battle/begin_battle/', headers=headers, verify=False, data=payload)
    t = r.text
    #print t
    o = json.loads(r.text)
    #pprint(o)
    return o
    

def auto_battle():
    flag = rcache.get('smash_collect')
    if not flag:
        print '终止运行'
        return '终止运行'
    now = datetime.datetime.now(tz)
    t = target()
    if t == 0:
        qy_util.post('SMASH自动战斗触发:失败，应该需要重新登录🏮' + '\n北京时间:' + str(now)[:19], appid=3, toparty=['20'])
        print '赶上不能登录了呢😯'
        return '赶上不能登录了呢😯' 
    elif t == 1:
        print '能量不够而已😝'
        return '能量不够而已😝'
    target_user_id, target_type, energy_cost, target_user = t
    print '=====', target_user_id, target_type, energy_cost
    pprint(target_user)
    o = battle(target_user_id=target_user_id)
    s = o.get('exception')
    s = s.get('message') if s else None
    text = 'SMASH自动战斗触发:\n'+ (str(o) if not s else (s + '😞')) + '\n北京时间:' + str(now)[:19]
    qy_util.post('SMASH自动战斗触发:\n'+ (('✅ 自动大干了一场!剩余能量🔋 :' + _cal_get(o)) if not s else (s + '😞')) + '\n北京时间:' + str(now)[:19], appid=3, toparty=['20'])
    return text
    


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
    #pprint(o)
    t = o['access_token']
    print 'bid:' + t
    return t


def refresh():
    t = login()
    rcache.set('smash_bid', t)
    s = '🍉 已经更新bid:%s' % t
    print s
    notify(s=s)


def collect():
    r = requests.post('https://199.167.22.55/game/city/collect_resources/', headers=headers, verify=False)
    t = r.text
    #print t
    o = json.loads(r.text)
    ####debug####pprint(o)
    now = datetime.datetime.now(tz)
    try:
        resources_gained = str(int(o['resources_gained']['1']))
        resources_total = str(int(o['resources']['1']))
        energy_now = str(_cal_energy(o))
        energy_cap = str(int(o['game_user']['energy_cap']))
    except Exception, e:
        str(e)
        qy_util.post(str(e) + '\n北京时间:' + str(now)[:19], appid=3, toparty=['20'])
        return False
    #print resources_gained
    try:
        if now.minute % 20 == 0: 
            qy_util.post('SMASH自动采集金币:%s/%s' % (resources_gained, resources_total) + '\n能量值:%s/%s' % (energy_now, energy_cap) +'\n北京时间:' + str(now)[:19], appid=3, toparty=['20'])
    except Exception, e:
        print '没有微信推送'
        print str(e)
    text = 'SMASH自动采集金币:%s/%s' % (resources_gained, resources_total) + '\n能量值:%s/%s' % (energy_now, energy_cap) +'\n北京时间:' + str(now)[:19]
    print text
    return text



#collect()

def random_collect(sample=4):
    flag = rcache.get('smash_collect')
    if not flag:
        print '终止运行'
        return
    s = randint(0, sample)
    print s
    n = datetime.datetime.now()
    if s == 0 or n.minute == 0:
        for i in tqdm(range(0, randint(0, 15))):
            time.sleep(1)
        f = collect()
        if not f:
            bid = rcache.get('smash_bid')
            bid = bid if bid else ''
            print 'bid0:' + bid
            t = login()
            bid = t
            rcache.set('smash_bid', t)
            print 'bid1:' + bid
            global headers
            headers['SquidAuthToken'] = 'Bearer id=' + bid 
            headers['Authorization'] = 'Bearer id=' + bid
            collect()
            tz = pytz.timezone('Asia/Shanghai')
            now = datetime.datetime.now(tz)
            qy_util.post('重新登录，bid:' + bid + '\n北京时间:' + str(now)[:19], appid=3, toparty=['20'])
    else:
        print '随机选择退出了😝'



