# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
from pprint import pprint
from models.model_proxy import *
import datetime
import time
from functools import wraps
import socket


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


def pace(fn):
    @wraps(fn)
    def func(*args, **kwds):
        t0 = time.time()
        r = fn(*args, **kwds)
        t = time.time() - t0
        print '---%s: %ss---' % (fn.__name__, t)
        return r
    return func


@ex(False)
def is_ip(ip):
    socket.inet_aton(ip)
    return True


def get_us_proxy():
    r = requests.get('https://www.us-proxy.org/').text
    s = BeautifulSoup(r)
    r = s.findAll('tr')[1:-1]
    r = [a.findAll('td') for a in r]
    r = [map(lambda x: x.get_text(), a) for a in r]
    return r


def update_proxy(result):
    for item in result:
        ip = item[0]
        port = item[1]
        code = item[2]
        country = item[3]
        anonymity = item[4]
        google = 0 if item[5]=='no' else 1
        https = 0 if item[6]=='no' else 1
        now = datetime.datetime.now()
        key = '%s:%s' % (ip, port)
        if Proxy.query.filter_by(key=key).first():
            continue
        p = Proxy(key=key,
                  ip=ip,
                  port=port,
                  code=code,
                  country=country,
                  anonymity=anonymity,
                  google=google,
                  https=https,
                  update_time=now,
                  create_time=now
                  )
        flush(p)


def fetch_proxy():
    r = get_us_proxy()
    update_proxy(r)


def check_proxy(ip, port):
    pd = {"http": "http://%s:%s" % (ip, port)}
    url = 'http://wtfismyip.com/text'
    try:
        t0 = time.time()
        r = requests.get(url, proxies=pd, timeout=2)
        t = time.time() - t0
        #print r.text, t
        if is_ip(r.text): 
            return True, t
    except Exception, e:
        print str(e)
    return False, 2

a=Proxy.query.all()
for i in a:
    check_proxy(i.ip,i.port)
