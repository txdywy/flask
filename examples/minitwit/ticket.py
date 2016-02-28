# -*- coding: utf-8 -*-
import requests as r
import json
import urllib
import time
import random
from bs4 import BeautifulSoup
import urllib2


def post_alert(s='无', app='bearychat'):
    url = 'https://hook.bearychat.com/=bw7K8/incoming/78e7c08a86df9f6f89cb375cd324bdc7'
    payload = {'text': s}
    headers = {'content-type': 'application/json'}
    r.post(url, data = json.dumps(payload), headers = headers)


def ti(n=10, lap=60*7):
    u = 'http://events.chncpa.org/wmx2016/action/pctou.php?id=5&user_ip=%s.%s.%s.%s&time=2016-02-26+'
    headers = {'Referer': 'http://events.chncpa.org/wmx2016/mobile/pages/jmpx.php?from=singlemessage&amp;isappinstalled=0', 'X-Requested-With': 'XMLHttpRequest', 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.%s Safari/537.36'%random.randint(2,250)} 
    for i in range(n):
        ur= u % (random.randint(2,250),random.randint(2,250),random.randint(2,250),random.randint(2,250))+urllib.quote('%s:%s:%s'%(random.randint(2,58),random.randint(2,58),random.randint(2,58),))
        x=r.get(ur,headers=headers)
        print x.text
        time.sleep(random.randint(1, lap))
        print x.text


def rank():
    result = urllib2.urlopen('http://events.chncpa.org/wmx2016/mobile/pages/jmpx.php').read()
    soup = BeautifulSoup(result)
    lis = soup.findAll('li')
    data = [(li.find('div', {'class': 'v_name'}), li.find('span', {'class': 'v_num'})) for li in lis]
    data = [(v[0].text, v[1].text) for v in data if v[0]]
    data = [(v[0], int(v[1].split('：'.decode('utf8'))[-1])) for v in data]
    data = sorted(data, key=lambda x: x[1], reverse=True)
    return data


def tr():
    d = rank()
    t = '\n'.join('[第%s名]' % n + [i[0]+':'+str(i[1]) for n, i in enumerate(d)])
    post_alert(t)


def top1():
    d = rank()
    t = d[0]
    if t[0]!= u'\u6c11\u65cf\u821e\u300a\u7ffb\u8eab\u519c\u5974\u628a\u6b4c\u5531\u300b':
        ti(10, 5)

