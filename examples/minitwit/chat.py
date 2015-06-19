from config import LC_APP_ID, LC_APP_KEY
import requests
import json
def new_chat(uid1, uid2):
    url = 'https://api.leancloud.cn/1.1/classes/_Conversation'
    headers = {
        'X-AVOSCloud-Application-Id': LC_APP_ID,
        'X-AVOSCloud-Application-Key': LC_APP_KEY,
        'Content-Type': 'application/json',
    }
    data = {
        'name': 'room_%s_%s' % (uid1, uid2),
        'm': [str(uid1), str(uid2)],
    }
    try:
        r = requests.post(url, data=json.dumps(data), headers=headers)
        room_id = json.loads(r.content)['objectId']
    except Exception, e:
        print '------------new chat room failed-------------', e
        room_id = ''
    return room_id


def push_msg(msg):
    url = 'https://leancloud.cn/1.1/push'
    headers = { 
        'X-AVOSCloud-Application-Id': LC_APP_ID,
        'X-AVOSCloud-Application-Key': LC_APP_KEY,
        'Content-Type': 'application/json',
    } 
    data = {
        'data': {'alert': msg}
    }
    try:
        r = requests.post(url, data=json.dumps(data), headers=headers)
    except Exception, e:
        print '------------push msg failed-------------', e
    return r.content
