# -*- coding: utf-8 -*-
import requests
import datetime

US_STOCK = {'fb': 'fb',
            'msci': 'msci',
            'jd': 'jd',
            'app': 'aapl',
            'tw': 'twtr',
            'ms': 'msft',
            'g': 'goog',
            'amz': 'amzn',
            'tsla': 'tsla',
            'ali' : 'baba',
            'net': 'nflx',
            'ko': 'ko',
            'dis': 'dis',
            'data': 'data',
            'gopro': 'gpro',
            #'square': 'sq',
            #'yrd': 'yrd',
            #'vcel': 'vcel',
            }

CN_STOCK = {'海天': 'sh603288',
            '科大': 'sz002230',
            #'天地': 'sh600582',
            '格力': 'sz000651',
            #'昆仑': 'sz300418',
            #'东阿': 'sz000423',
            #'海欣': 'sz002702',
            }
            
US_BASES = { 'fb': 100,
            'msci': 63,
            'jd': 22.3,
            'app': 93.5,
            'tw': 14.3,
            'ms': 48,
            'g': 690,
            'amz': 475,
            'tsla': 165,
            'ali' : 60,
            'net': 80,
            'ko': 41.9,
            'dis': 88,
            'data': 35,
            'gopro': 9,
            #'square': 12,
            #'yrd': 13,
            #'vcel': 3.12,
          }

SINA_STOCK_URL = 'http://hq.sinajs.cn/list=%s'
US_CASH = 34257
#2016.04.06 #24924
#2016.06.30 #24523
#2016.07.15 #26149
#2016.07.26 #26491
#2016.08.08 #27101
#2016.12.31 #24485
#2017.01.26 #27602
#2017.02.02 #28309
#2017.02.14 #28231
#2017.04.26 #29979
#2017.07.18 #31336
#2017.07.25 #31882
#2017.07.27 #32429
#2017.09.04 #33214
#2017.10.13 #34257
US_PROFIT_2016 = 24485 - 23000
US_RATE_2016 = 6.5
US_RATE_2016_SUMIT = 17.8
US_BASE = 24485
#Tue Feb 14 14:35:57 CST 2017
CN_CASH = 240000
#Thu Jan  5 11:37:48 CST 2017 +100000(MA)
#Tue Feb 14 14:35:57 CST 2017
CN_BASE = 140000 + 100000
#Tue Feb 14 14:35:57 CST 2017
CN_PROFIT = 5966.48 + 1314.30
#Fri Jul  1 09:51:23 CST 2016
#Mon Jul  4 11:35:45 CST 2016
#Tue Sep  6 09:36:49 CST 2016 +1745.93
#Fri Dec 30 08:54:29 UTC 2016 -672.27
#Tue Jan  3 15:27:29 CST 2017 +672.27 start as 140000 since 2017
#Fri Jan 13 21:54:37 CST 2017
#Mon Jan 16 14:38:12 CST 2017 +5966.48 (deposit 5966.48) 
#Tue Feb 14 14:35:57 CST 2017 +1314.30 (deposit 1314.30)
CN_PROFIT_2016 = 10082.06 + 672.27 #adjust by 2017.1.3
CN_RATE_2016 = 7.7

def get_us_stock():
    r = requests.get(SINA_STOCK_URL % ','.join(['gb_' + US_STOCK[i] for i in US_STOCK])).text.strip()
    r = r.split(';')[:-1]
    r = [i.split('"')[1].split(',')[:] for i in r]
    r = ['%s: \n#[$%s]\n#%s+%s \n#%s-%s\n*[$%s] %s\n*%s+%s \n*%s-%s\n' % (i[0], i[1], i[7], _diff(i[1], i[7]), i[6], _diff(i[6], i[1]), i[21], _diff_sym(i[21], i[1]), i[7], _diff(i[21], i[7]), i[6], _diff(i[6], i[21])) for i in r]
    b = [US_BASES[k] for k in US_BASES]
    r = zip (r, b)
    r = [a + 'Base: [%s]\n' % b for a, b in r]
    r = '\n'.join(r)
    return r + '\n' + str(datetime.datetime.now())[:19] + '\n' + '#盘内/终\n*盘前/后'.decode('utf8') + '\n[B:%s/%s][%+d][%+.2f%%]' % (US_CASH, US_BASE, US_CASH-US_BASE, (US_CASH-US_BASE)*100.0/US_BASE) + '\n[2016.P:%s]' % US_PROFIT_2016 + '\n[2016.PR:%+.2f%%]' % US_RATE_2016


def get_us_in_stock():
    r = requests.get(SINA_STOCK_URL % ','.join(['gb_' + US_STOCK[i] for i in US_STOCK])).text.strip()
    r = r.split(';')[:-1]
    r = [i.split('"')[1].split(',')[:] for i in r]
    a = r
    r = ['%s: \n#[$%s]\n#%s+%s \n#%s-%s\n*[$%s] %s\n*%s+%s \n*%s-%s\n' % (i[0], i[1], i[7], _diff(i[1], i[7]), i[6], _diff(i[6], i[1]), i[21], _diff_sym(i[21], i[1]), i[7], _diff(i[21], i[7]), i[6], _diff(i[6], i[21])) for i in r] 
    b = [US_BASES[k] for k in US_BASES]
    r = zip (r, b, a)
    r = [a + 'Base: [%s]\n' % b for a, b, c in r if _check_in(c[1], c[6], b)]
    r = '\n'.join(r)
    if not r:
        r = '没有符合要求的哟\n静候时机\n'
    return r + '\n' + str(datetime.datetime.now())[:19] + '\n' + '#盘内/终\n*盘前/后'.decode('utf8') + '\n[B:%s/%s][%+d]' % (US_CASH, US_BASE, US_CASH-US_BASE)


def _check_in(v1, v2, base):
    ratio = 0.006
    v1, v2, base = float(v1), float(v2), float(base)
    if v1>=base:
        if (v1-base)/base < ratio:
            return True
    if 0<v1<base or 0<v2<base:
        return True
    if v2>=base:
        if (v2-base)/base < ratio:
            return True
    return False


def get_one_us_stock(k):
    r = requests.get(SINA_STOCK_URL % 'gb_' + US_STOCK[k]).text.strip()
    r = r.split('"')[1].split(',')[:]
    i = r
    r = '%s: \n#[$%s]\n#%s+%s \n#%s-%s\n*[$%s] %s\n*%s+%s \n*%s-%s\n' % (i[0], i[1], i[7], _diff(i[1], i[7]),     i[6], _diff(i[6], i[1]), i[21], _diff_sym(i[21], i[1]), i[7], _diff(i[21], i[7]), i[6], _diff(i[6], i[21]))
    return r + 'Base: %s' % US_BASES[k] + '\n\n' + str(datetime.datetime.now())[:19] + '\n' + '#盘内/终\n*盘前/后'.decode('utf8')



def _diff_sym(a, b):
    x = _diff(a, b)
    if x >= 0:
        s = '+' + str(x)
    else:
        s = str(x)
    return s


def get_cn_stock():
    r = requests.get(SINA_STOCK_URL % ','.join(CN_STOCK.values())).text.strip()
    r = r.split(';')[:-1]
    r = [i.split('"')[1].split(',')[:] for i in r]
    r = ['%s: \n%s\n%s+%s \n%s-%s\n' % (i[0], i[3], i[5], _diff(i[3], i[5]), i[4], _diff(i[4], i[3])) for i in r]
    o = 442603.36 + 50000 + 50000 #2017.8.30 +50000 #2017.8 +50000
    n = 570017.35 #567619.14 2017.10.20 #564837.97 2017.9.29 #555891.93 2017.9.22 #550837.49 2017.9.4 #507677.78 2017.8.30 #507351.06 2017.8.22 #496287.04 2017.8.15 #464595.87 2017.8.14 #425182.54 2017.8 +50000
    p = (n-o)/o *100
    cn_status = "\n\nnow:%s\n base:%s\n P:%+.2f%%" % (n,o,p)
    r = '\n'.join(r)
    return r + '\n' + str(datetime.datetime.now())[:19] + '\n[B:%s/%s][%+d][%+.2f%%]' % (CN_CASH, CN_BASE, (CN_CASH-CN_BASE), (CN_CASH-CN_BASE)/CN_BASE*100) + '\n[P_out:%s]' % CN_PROFIT + '\n[PR_out:%+.2f%%]' % (CN_PROFIT * 100.0/CN_BASE) + '\n[2016.P:%s]' % CN_PROFIT_2016 + '\n[PR:%+.2f%%]' % CN_RATE_2016 + cn_status


def get_one_cn_stock(k):
    r = requests.get(SINA_STOCK_URL % CN_STOCK[k]).text.strip()
    i = r
    r = i.split('"')[1].split(',')[:] 
    i = r
    r = '%s: \n%s\n%s+%s \n%s-%s\n' % (i[0], i[3], i[5], _diff(i[3], i[5]), i[4], _diff(i[4], i[3]))
    return r + '\n' + str(datetime.datetime.now())[:19]


def _diff(a, b):
    return round(float(a) - float(b), 3)
