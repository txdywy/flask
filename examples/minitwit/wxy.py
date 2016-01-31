# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests 
import json
from functools import wraps
import pytz
import datetime
from models.model_wxy import *

tz = pytz.timezone('Asia/Shanghai')

URL = {'bearychat': 'https://hook.bearychat.com/=bw7K8/incoming/78e7c08a86df9f6f89cb375cd324bdc7',
       'slack': '',
       }
WXY_URL = 'http://wxy.chinavalue.net'

def set(key, value):
    cvs = ChinaValueStat(key=key, data=value)
    flush(cvs)
    return cvs


def get(key):
    cvs = ChinaValueStat.query.filter_by(key=key).order_by(ChinaValueStat.id.desc()).first()
    if cvs:
        return cvs.data
    else:
        return None


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


@ex('')
def get_wxy():
    h = get_cv_html(WXY_URL)
    r = get_coun_result(h)
    return r


def check(key, value):
    o = get(key)
    if o==value:
        return False
    else:
       set(key, value)
       return True


WXY_COUNT_KEY = 'wxy_count_key'

def main():
    now = datetime.datetime.now(tz)
    s = get_wxy()
    flag = check(WXY_COUNT_KEY, s) 
    if flag:
        s = s.encode('utf8')
        s += ' [%s 北京时间]\n' % str(now)[:19]
        print s
        post_alert(s)
    print flag
