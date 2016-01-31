# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests 
import json
from functools import wraps
import pytz
import datetime
from models.model_wxy import *
import hashlib

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

WXY_FINANCE_URL = 'http://www.chinavalue.net/Finance/Elite.aspx'
WXY_TOTAL_BLOG_URL = 'http://www.chinavalue.net/WeekArticle.aspx?Type=4'
WXY_TOTAL_COL_URL = 'http://www.chinavalue.net/WeekArticle.aspx?Type=3'
WXY_SEARCH_KEY = u'\u536b\u7965\u4e91'
@ex('')
def get_wxy_rank():
    h = get_cv_html(WXY_FINANCE_URL)
    s = BeautifulSoup(h)
    blog_lis = s.find('div', {'id': 'divBlog'}).findAll('li')
    blog_data = []
    for i, li in enumerate(blog_lis):
        if WXY_SEARCH_KEY in li.text:
            blog_data.append((i+1, li.findAll('a')[0].text.strip()))    
    blog_result = ['财经日志排名第%s位:%s' % (i[0], i[1].encode('utf8')) for i in blog_data]   
    
    col_lis = s.find('div', {'id': 'divColumn'}).findAll('li')
    col_data = []
    for i, li in enumerate(col_lis):
        if WXY_SEARCH_KEY in li.text:
            col_data.append((i+1, li.findAll('a')[1].text.strip())) 
    col_result = ['财经专栏排名第%s位:%s' % (i[0], i[1].encode('utf8')) for i in col_data]

    ht = get_cv_html(WXY_TOTAL_BLOG_URL)
    st = BeautifulSoup(ht)
    blt = st.find('div', {'class': 'SecContent'}).findAll('li')
    bt_data = []
    for i, li in enumerate(blt):
        if WXY_SEARCH_KEY in li.text:
            bt_data.append((i+1, li.findAll('a')[0].text.strip()))
    bt_result = ['热点日志排名第%s位:%s' % (i[0], i[1].encode('utf8')) for i in bt_data]

    hc = get_cv_html(WXY_TOTAL_COL_URL)
    sc = BeautifulSoup(hc)
    clt = sc.find('div', {'class': 'SecContent'}).findAll('li')
    ct_data = []
    for i, li in enumerate(clt):
        if WXY_SEARCH_KEY in li.text:
            ct_data.append((i+1, li.findAll('a')[0].text.strip()))
    ct_result = ['热点专栏排名第%s位:%s' % (i[0], i[1].encode('utf8')) for i in ct_data]
    
    result = ct_result + bt_result + col_result + blog_result
    return '\n'.join(result)



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



WXY_RANK_KEY = 'wxy_rank_key'

def rank():
    now = datetime.datetime.now(tz)
    hour = now.hour
    s = get_wxy_rank()
    m = hashlib.md5()
    m.update(s)
    hv = m.hexdigest()
    flag = check(WXY_RANK_KEY, hv)   
    #print s
    if flag or hour in (8, 12, 18, 22, 23, 0):
        s += '\n[%s 北京时间]\n' % str(now)[:19]
        post_alert(s) 
    print flag




