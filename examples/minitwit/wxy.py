# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests 
import json
from functools import wraps
import pytz
tz = pytz.timezone('Asia/Shanghai')

URL = {'bearychat': 'https://hook.bearychat.com/=bw7K8/incoming/78e7c08a86df9f6f89cb375cd324bdc7',
       'slack': '',
       }
WXY_URL = 'http://wxy.chinavalue.net'


def post_alert(s='无', app='bearychat'):
    url = URL[app]
    payload = {'text': s}
    headers = {'content-type': 'application/json'}
    r = requests.post(url, data = json.dumps(payload), headers = headers)


def ex(default=0):
    def wrapper(fn):
        @wraps(fn)
        def func(*args, **kwds):
            try:
                r = fn(*args, **kwds)
            except Exception, e:
                r = default
                print '[%s][%s]' % (fn.__name__, str(e))
                #print traceback.format_exc()
            return r
        return func
    return wrapper


@ex('')
def get_cv_html(url):
    h = requests.get(url).text
    return h


@ex('系统出错')
def get_coun_result(html):
    soup = BeautifulSoup(html)
    r = soup.find("div", {"class": "PageRight"}).find("dl", {"id": "AreaStat"}).findAll('li')[-1].get_text()
    return r


def get_wxy():
    h = get_cv_html(WXY_URL)
    r = get_coun_result(h)
    print r
    return r


def main():
    ac = get_wxy()
    post_alert(ac)
