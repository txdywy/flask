# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
from pprint import pprint
from models.model_proxy import *
import datetime
import time
from functools import wraps
import socket
from tqdm import tqdm
init_db()

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
    r = requests.get('http://www.us-proxy.org/').text
    s = BeautifulSoup(r)
    r = s.findAll('tr')[1:-1]
    r = [a.findAll('td') for a in r]
    r = [map(lambda x: x.get_text(), a) for a in r]
    return r


def get_ssl_proxy():
    r = requests.get('http://www.sslproxies.org/').text
    s = BeautifulSoup(r)
    r = s.findAll('tr')[1:-1]
    r = [a.findAll('td') for a in r]
    r = [map(lambda x: x.get_text(), a) for a in r]
    #pprint(r)
    return r


def get_uk_proxy():
    r = requests.get('http://free-proxy-list.net/uk-proxy.html').text
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


@ex('Fetch UK Failed')
def fetch_uk_proxy():
    r = get_uk_proxy()
    update_proxy(r)
    return 'Fetch UK Succeed'


@ex('Fetch SSL Failed')
def fetch_ssl_proxy():
    r = get_ssl_proxy()
    update_proxy(r)
    return 'Fetch SSL Succeed'
    

@ex('Fetch US Failed')
def fetch_us_proxy():
    r = get_us_proxy()
    update_proxy(r)
    return 'Fetch US Succeed'


def fetch_proxy():
    return '\n'.join([fetch_uk_proxy(),
                      fetch_ssl_proxy(),
                      fetch_us_proxy(),
                     ])


def check_proxy(ip, port):
    pd = {"http": "http://%s:%s" % (ip, port)}
    url = 'http://wtfismyip.com/text'
    try:
        t0 = time.time()
        r = requests.get(url, proxies=pd, timeout=2)
        t = time.time() - t0
        print r.text, t
        if is_ip(r.text): 
            return True, t
    except Exception, e:
        print str(e)
    return False, 2


@pace
def task_proxy():
    print '[Active before: %s]' % Proxy.query.filter_by(active=1).count()
    print fetch_proxy()
    ps = Proxy.query.all()
    now = datetime.datetime.now()
    for i in tqdm(ps):
        if i.active==0:
            d = now - i.update_time
            if d.seconds < 60*60*6:
                continue
        r, t = check_proxy(i.ip,i.port)
        print t, i.code
        if r:
            i.delay = int(t*1000)
        else:
            i.active = 0
        i.update_time = now
        flush(i)
    pprint([vars(a) for a in Proxy.query.filter_by(active=1).all()])
    print '[Active after: %s]' % Proxy.query.filter_by(active=1).count()

