import time, datetime
import urllib
from faker import Factory
import requests
from proxy import *
from random import randint
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
    now = datetime.datetime.now()
    dtime = str(now)[:19]
    dtime = urllib.quote_plus(dtime)
    ip = px.ip
    turl = url.format(ip=ip, id=id, dtime=dtime)
    pd = {"http": "http://%s:%s" % (px.ip, px.port)}
    print px.ip, px.port
    result = requests.get(turl, headers=headers, proxies=pd, timeout=timeout)
    print result.text, turl, result.request.headers
    return result.text
