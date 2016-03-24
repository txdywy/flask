# -*- coding: utf-8 -*-
#import gevent
#from gevent import monkey
#monkey.patch_all()
import urllib2
try:import pycurl
except:pass
from StringIO import StringIO
import requests
from bs4 import BeautifulSoup
from pprint import pprint
from models.model_proxy import *
import datetime
import time
from functools import wraps
import socket
from tqdm import tqdm
import requesocks as rs
import random
import iso3166
import base64
sock_session = rs.session()
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.109 Safari/537.36'}

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


def get_sock_proxy():
    r = requests.get('http://www.socks-proxy.net/', headers=headers).text
    s = BeautifulSoup(r)
    r = s.findAll('tr')[1:-1]
    r = [a.findAll('td') for a in r]
    r = [map(lambda x: x.get_text(), a) for a in r]
    return r


def get_us_proxy():
    r = requests.get('http://www.us-proxy.org/', headers=headers).text
    s = BeautifulSoup(r)
    r = s.findAll('tr')[1:-1]
    r = [a.findAll('td') for a in r]
    r = [map(lambda x: x.get_text(), a) for a in r]
    return r


def get_ssl_proxy():
    r = requests.get('http://www.sslproxies.org/', headers=headers).text
    s = BeautifulSoup(r)
    r = s.findAll('tr')[1:-1]
    r = [a.findAll('td') for a in r]
    r = [map(lambda x: x.get_text(), a) for a in r]
    #pprint(r)
    return r


def get_uk_proxy():
    r = requests.get('http://free-proxy-list.net/uk-proxy.html', headers=headers).text
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
        anonymity = item[4].lower()
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


@ex('Fetch Sock Failed')
def fetch_sock_proxy():
    r = get_sock_proxy()
    update_proxy(r)
    return 'Fetch Sock Succeed'


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
                      fetch_sock_proxy(),
                     ])


def check_proxy(ip, port, anonymity=''):
    url = 'http://wtfismyip.com/text'
    if 'sock' not in anonymity:
        pd = {"http": "http://%s:%s" % (ip, port)}
        try:
            t0 = time.time()
            r = requests.get(url, proxies=pd, timeout=2, headers=headers)
            t = time.time() - t0
            print r.text, t, anonymity
            if is_ip(r.text): 
                return True, t
        except Exception, e:
            print str(e)
    else:
        sock_session.proxies = {'http': '%s://%s:%s' % (anonymity, ip, port)}
        try:
            t0 = time.time()
            r = sock_session.get(url, timeout=2)
            t = time.time() - t0
            print r.text, t, anonymity
            if is_ip(r.text):
                return True, t
        except Exception, e:
            print str(e)
    return False, -1


@pace
def task_proxy0():
    print '[Active before: %s/%s]' % (Proxy.query.filter_by(active=1).count(), Proxy.query.count())
    print fetch_proxy()
    print fetch_samair_proxy()
    print fetch_cool_proxy()
    print fetch_nntime_proxy()


@pace
def task_proxy1(n=0, m=500):
    ps = Proxy.query.offset(m*n).limit(m).all()
    now = datetime.datetime.now()
    for i in tqdm(ps):
        if i.active==0:
            d = now - i.update_time
            if d.seconds < 60*60*random.randrange(6, 24) + 60*random.randrange(0, 60):
                continue
            i.active = 1
        r, t = check_proxy(i.ip, i.port, i.anonymity)
        print t, i.code
        if r:
            i.delay = int(t*1000)
            i.hit += 1
        else:
            i.active = 0
        i.update_time = now
        flush(i)
    pprint([vars(a) for a in Proxy.query.filter_by(active=1).all()])
    print '[Active after: %s/%s]' % (Proxy.query.filter_by(active=1).count(), Proxy.query.count())


def get_active_num():
    return Proxy.query.filter_by(active=1).count()
    

def get_all_num():
    return Proxy.query.count()


def check_status():
    active_num = get_active_num()
    sock_num = Proxy.query.filter_by(active=1).filter(Proxy.anonymity.contains('sock')).count()
    http_num = active_num - sock_num
    s = '[H: %s/%s]' % (http_num, active_num)
    s += '\n' + '[S: %s/%s]' % (sock_num, active_num)
    s += '\n\n' + '[A: %s/%s]' % (active_num, get_all_num())
    sum_all = {k: v for k, v in db_session.query(Proxy.site, func.count(1)).group_by(Proxy.site).all()}
    sum_act = {k: v for k, v in db_session.query(Proxy.site, func.count(1)).filter_by(active=1).group_by(Proxy.site).all()}
    st = ['[%s: %s/%s]' % (k, sum_act.get(k, 0), sum_all[k]) for k in sum_all]
    st = '\n'.join(st)
    result = st + '\n\n' + s
    return result


def check_code_status(n=None):
    code_act = db_session.query(Proxy.code, Proxy.country, func.count(1)).filter_by(active=1).group_by(Proxy.code).all()
    code_act = sorted(code_act, key=lambda x: x[2], reverse=True)
    if n:
        code_act = code_act[:n]
    sc = '\n'.join(['[%s (%s): %s]' % (a, b, c) for a, b, c in code_act])
    return sc


def get_active():
    ps = Proxy.query.filter_by(active=1).all()
    ds = ['[No.{i}]\n[{ip}:{port}]\n[{version}]\n[{code}]\n[{country}]\n[{site}]\n[hot: {hit}]\n\n'.format(i=i, ip=p.ip, port=p.port, version=p.anonymity if 'sock' in p.anonymity else p.anonymity+'/http', code=p.code, country=p.country, hit=p.hit, site=p.get_site()) for i, p in enumerate(ps)]
    r = check_status() + '\n\n' + ''.join(ds)
    return r


def get_top_active(n=10):
    ps = Proxy.query.filter_by(active=1).order_by(desc(Proxy.hit)).limit(n).all()
    ds = ['[No.{i}]\n[{ip}:{port}]\n[{version}]\n[{code}]\n[{country}]\n[{site}]\n[hot: {hit}]\n\n'.format(i=i, ip=p.ip, port=p.port, version=p.anonymity if 'sock' in p.anonymity else p.anonymity+'/http', code=p.code, country=p.country, hit=p.hit, site=p.get_site()) for i, p in enumerate(ps)]
    h = check_status()
    c = check_code_status(10 if n==10 else None)
    r = '%s\n\n%s%s' % (h + '\n\n' + c, ''.join(ds), h)
    return r


def check(ip, port, sock=None, timeout=2):
    if not sock:
        check_http(ip, port, timeout)
    else:
        check_sock(ip, port, timeout, sock=sock)


def check_sock(ip, port, timeout=2, sock='socks5'):
    url = 'http://wtfismyip.com/text'
    sock_session.proxies = {'http': '%s://%s:%s' % (sock, ip, port)}
    try:
        t0 = time.time()
        r = sock_session.get(url, timeout=timeout)
        t = time.time() - t0
        print r.text, t, sock
        if is_ip(r.text):
            return True, t
    except Exception, e:
        print str(e)
    return False, -1


def check_http(ip, port, timeout=2):
    url = 'http://wtfismyip.com/text'
    pd = {"http": "http://%s:%s" % (ip, port)}
    try:
        t0 = time.time()
        r = requests.get(url, proxies=pd, timeout=timeout, headers=headers)
        t = time.time() - t0
        print r.text, t
        if is_ip(r.text): 
            return True, t
    except Exception, e:
        print str(e)
    return False, -1


def fetch_http_ip(ip, port, timeout=2):
    proxy = urllib2.ProxyHandler({'http': '%s:%s' % (ip, port)})
    opener = urllib2.build_opener(proxy)
    urllib2.install_opener(opener)
    r = urllib2.urlopen('http://myexternalip.com/raw', timeout=timeout).read()
    return r


def fetch_sock_ip(ip, port, sock='socks5', timeout=2):
    c = pycurl.Curl()
    url = 'http://myexternalip.com/raw'
    s = pycurl.PROXYTYPE_SOCKS5 if sock=='socks5' else pycurl.PROXYTYPE_SOCKS4
    storage = StringIO()
    c.setopt(pycurl.URL, url)
    c.setopt(pycurl.PROXY, ip)
    c.setopt(pycurl.PROXYPORT, port)
    c.setopt(pycurl.PROXYTYPE, s)
    c.setopt(c.WRITEFUNCTION, storage.write)
    c.setopt(pycurl.CONNECTTIMEOUT, timeout)
    c.perform()
    c.close()
    content = storage.getvalue()
    return content


def fetch_ip(ip, port, sock=None, timeout=2):
    port = int(port)
    if sock:
        return fetch_sock_ip(ip, port, sock, timeout=timeout)
    else:
        return fetch_http_ip(ip, port, timeout=timeout)


@pace
def fetch_all():
    #ps = Proxy.query.filter_by(active=1).order_by(desc(Proxy.hit)).limit(100).all()
    now = datetime.datetime.now()
    ps = Proxy.query.all()
    rs = []
    for i in ps:
        d = now - i.update_time
        if not i.active:
            if d.seconds < 60*60*random.randrange(1, 6) + 60*random.randrange(0, 60):
                continue
        rs.append(i)
    ps = rs
    print len(ps)
    #return
    #pprint([vars(p) for p in ps])
    jobs = [gevent.spawn(fetch_ip, p.ip, p.port, p.anonymity if 'sock' in p.anonymity else None) for p in ps]
    gevent.wait(jobs)
    return [j.value for j in jobs]


@ex(default=[])
def get_samair_proxy(url):
    """samair.ru"""
    r = requests.get(url, headers=headers).text
    s = BeautifulSoup(r)
    css_url = 'http://www.samair.ru%s' % s.findAll('link')[1]['href']
    css_r = requests.get(css_url, headers=headers).text
    css_d = {i[1:i.find(':')]: i.split('"')[1] for i in css_r.split('\n')[:-1]}
    trs = s.find('table', {'id': 'proxylist'}).findAll('tr')[1:-1]
    r = [tr.findAll('td') for tr in trs]
    r = [dict(ip=t[0].text[:-1], port=css_d[t[0].find('span')['class'][0]], anonymity=t[1].text, country=t[3].text) for t in r]
    return r


@pace
def get_all_samair_proxy():
    r = []
    for i in tqdm(range(1, 31)):
        t = get_samair_proxy('http://www.samair.ru/proxy/proxy-%s.htm' % (str(i) if i>9 else '0' + str(i)))
        r += t
    return r


@ex('')
def _get_code(country):
    if 'Vietnam'.lower() in country.lower():
        return 'VN'
    if 'Venezuela'.lower() in country.lower():
        return 'VE'
    if 'Kazakstan'.lower() in country.lower():
        return 'KZ'
    if 'Bolivia'.lower() in country.lower():
        return 'BO'
    if 'Serbia and Montenegro'.lower() in country.lower():
        return 'CS'
    if 'Congo, The Democratic Republic of the'.lower() in country.lower():
        return 'CD'
    if 'Palestinian Territory'.lower() in country.lower():
        return 'PS'
    if 'Libyan Arab Jamahiriya'.lower() in country.lower():
        return 'LY'
    if 'Macedonia'.lower() in country.lower():
        return 'MK'
    if 'Moldova, Republic'.lower() in country.lower():
        return 'MD'
    if 'Satellite Provider'.lower() in country.lower():
        return 'A2'
    return iso3166.countries.get(country).alpha2


def update_samair_proxy(result):
    for item in result:
        ip = item['ip']
        port = item['port']
        code = _get_code(item['country'])
        country = item['country']
        anonymity = item['anonymity'].lower()
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
                  update_time=now,
                  create_time=now,
                  site=1
                  )
        flush(p)


@ex('Fetch Samair Failed')
def fetch_samair_proxy():
    r = get_all_samair_proxy()
    update_samair_proxy(r)
    return 'Fetch Samair Success'


def gen_cron_task(n=20, m=1000):
    a = "*/20 * * * * cd /home/ubuntu/flask/examples/minitwit; python -c 'import proxy as p;p.task_proxy1(%s, %s)' >> /home/ubuntu/proxy1_%s.log 2>&1"
    for i in range(n):
        print a % (i, m, i)


@ex([])
def get_cool_proxy(url):
    r = requests.get(url, headers=headers)
    if r.status_code == 404:
        return []
    r = r.text
    #print r
    s = BeautifulSoup(r)
    trs0 = s.find('table').findAll('tr')[1:]
    trs = []
    for t in trs0:
        tds = t.findAll('td')
        if len(tds)>1:
            trs.append(tds)
    r = [dict(ip=_parse_cool_ip(i[0].find('script').text), port=i[1].text, country=i[3].text, anonymity=i[5].text) for i in trs]
    #print r
    return r


def _parse_cool_ip(raw):
    r = raw.split('"')[1]
    r = r.encode('rot13')
    r = base64.b64decode(r)
    return r


@pace
def get_all_cool_proxy():
    r = []
    for i in tqdm(range(1, 21)):
        t = get_cool_proxy('http://www.cool-proxy.net/proxies/http_proxy_list/page:%s' % i)
        r += t
    return r


def update_cool_proxy(result):
    for item in result:
        ip = item['ip']
        port = item['port']
        code = _get_code(item['country'])
        country = item['country']
        anonymity = item['anonymity'].lower()
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
                  update_time=now,
                  create_time=now,
                  site=2
                  )
        flush(p)


@ex('Fetch Cool Failed')
def fetch_cool_proxy():
    r = get_all_cool_proxy()
    update_cool_proxy(r)
    return 'Fetch Cool Success'


#@ex([])
def get_nntime_proxy(url):
    r0 = requests.get(url, headers=headers)
    if r0.status_code == 404:
        return []
    r0 = r0.text
    s0 = BeautifulSoup(r0)
    js = s0.findAll('script')[1].text.replace(';', ',')
    jsd = eval('dict(%s)' % js) 
    jsd[''] = ''
    trs = s0.find('table', {'id': 'proxylist'}).findAll('tr',{'class': ('odd', 'even')})
    trs = [tr.findAll('td') for tr in trs]
    r0 = []
    for i in trs:
        item = {}
        raw = i[1].text
        item['ip'] = raw[:raw.find('d')]
        #print raw
        item['port'] = ''.join([str(jsd[x]) for x in raw[raw.find(':')+3:-1].split('+')])
        item['port'] = item['port'] if item['port'] else '80'
        item['country'] = i[4].text.split('(')[0].strip()
        item['anonymity'] = i[2].text.strip()
        r0.append(item)
    return r0


@pace
def get_all_nntime_proxy():
    r = []
    for i in tqdm(range(1, 71)):
        t = get_nntime_proxy('http://nntime.com/proxy-list-%s.htm' % (str(i) if i>9 else '0' + str(i)))
        r += t
    return r


def update_nntime_proxy(result):
    for item in result:
        ip = item['ip']
        port = item['port']
        code = _get_code(item['country'])
        country = item['country']
        anonymity = item['anonymity'].lower()
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
                  update_time=now,
                  create_time=now,
                  site=3
                  )
        flush(p)

@ex('Fetch Nntime Failed')
def fetch_nntime_proxy():
    r = get_all_nntime_proxy()
    update_nntime_proxy(r)
    return 'Fetch Nntime Success'
