import requests, sys, json
from pprint import pprint
import qy_util
headers = {
    'Host': 'api.smash.athinkingape.com',
    'SquidAuthToken': 'Bearer id=tW4fTvv//CvSZxJBX1fOUwlT4ClVGqAmy3qsCpYRtCykknH/Cc1knROyEv00Iwf/qSfTeSjMYPYc9TT5GgQFgw==',
    'Accept': '*/*',
    'Authorization': 'Bearer id=tW4fTvv//CvSZxJBX1fOUwlT4ClVGqAmy3qsCpYRtCykknH/Cc1knROyEv00Iwf/qSfTeSjMYPYc9TT5GgQFgw==',
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
    o = json.loads(r.text)
    #pprint(o)
    resources_gained = o['resources_gained']
    qy_util.post('resources_gained', touser='txdywy')



collect()
