import time, datetime
import urllib
from faker import Factory
import requests
from proxy import *
from random import randint
import requesocks as rs

sock_session = rs.session()
fake = Factory.create('en_US')
url = 'http://events.chncpa.org/wmx2016/action/pctou.php?id={id}&user_ip={ip}&time={dtime}'
pxs = Proxy.query.filter_by(active=1).all()
pxs = [p for p in pxs if 'sock' not in p.anonymity]
print 'Valid http proxy: [%s]' % len(pxs)


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
def geti(id=5, px=None, timeout=60):
    if not px:
        px = pxs[randint(0, len(pxs)-1)]
    headers = {'Referer': 'http://events.chncpa.org/wmx2016/mobile/pages/jmpx.php', 
               'X-Requested-With': 'XMLHttpRequest', 
               'User-Agent': fake.user_agent(),
               'Accept': 'application/json, text/javascript, */*; q=0.01',
               'Accept-Encoding': 'gzip, deflate, sdch',
               'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6',
               'Cache-Control': 'no-cache',
               'Host': 'events.chncpa.org',
               'Pragma': 'no-cache', 
               } 
    now = datetime.datetime.now() - datetime.timedelta(days=1)
    dtime = str(now)[:19]
    dtime = urllib.quote_plus(dtime)
    ip = px.ip
    turl = url.format(ip=ip, id=id, dtime=dtime)
    pd = {"http": "http://%s:%s" % (px.ip, px.port)}
    print '[%s:%s %s]' % (px.ip, px.port, px.anonymity)
    if 'sock' in px.anonymity:
        sock_session.proxies = {'http': '%s://%s:%s' % (px.anonymity, px.ip, px.port)}
        result = sock_session.get(url, timeout=timeout, headers=headers)
    else:
        result = requests.get(turl, headers=headers, proxies=pd, timeout=timeout)
    _check_result(result.text, px)
    print result.text, result._content
    print turl, result.request.headers
    return vars(result)


def _check_result(result, px):
    key = '%s:%s' % (px.ip, px.port)
    p = ProxyHit.query.filter_by(key=key).first()
    if not p:
        p = ProxyHit(key=key)
        vars(p)
    if '{' in result and '}' in result and 'number' in result:
        p.hit = (p.hit+1) if p.hit else 1
    else:
        p.sit = (p.sit+1) if p.sit else 1
    p.update_time=datetime.datetime.now()
    flush(p)


@ex('')
def beti(id=5, px=None, timeout=60):
    if not px:
        ps = ProxyHit.query.filter(ProxyHit.hit>0).all()
        p = ps[randint(0, len(ps)-1)]
        px = Proxy.query.filter_by(key=p.key).first()
    headers = {'Referer': 'http://events.chncpa.org/wmx2016/mobile/pages/jmpx.php', 
               'X-Requested-With': 'XMLHttpRequest', 
               'User-Agent': fake.user_agent(),
               'Accept': 'application/json, text/javascript, */*; q=0.01',
               'Accept-Encoding': 'gzip, deflate, sdch',
               'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6',
               'Cache-Control': 'no-cache',
               'Host': 'events.chncpa.org',
               'Pragma': 'no-cache', 
               } 
    now = datetime.datetime.now()
    dtime = str(now)[:19]
    dtime = urllib.quote_plus(dtime)
    ip = px.ip
    turl = url.format(ip=ip, id=id, dtime=dtime)
    pd = {"http": "http://%s:%s" % (px.ip, px.port)}
    print '[%s:%s %s]' % (px.ip, px.port, px.anonymity)
    if 'sock' in px.anonymity:
        sock_session.proxies = {'http': '%s://%s:%s' % (px.anonymity, px.ip, px.port)}
        result = sock_session.get(url, timeout=timeout, headers=headers)
    else:
        result = requests.get(turl, headers=headers, proxies=pd, timeout=timeout)
    _check_result(result.text, px)
    print result.text, result._content
    print turl, result.request.headers
    return vars(result)

def task(n=300):
    for _ in xrange(n):
        geti()
