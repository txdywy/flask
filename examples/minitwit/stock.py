# -*- coding: utf-8 -*-
import requests
import datetime

US_STOCK = {'facebook': 'fb',
            'msci': 'msci',
            'jd': 'jd',
            'apple': 'aapl',
            'twitter': 'twtr',
            'ms': 'msft',
            }

CN_STOCK = {'海天': 'sh603288',
            '天地': 'sh600582',
            '格力': 'sz000651',
            }

SINA_STOCK_URL = 'http://hq.sinajs.cn/list=%s'


def get_us_stock():
    r = requests.get(SINA_STOCK_URL % ','.join(['gb_' + i for i in US_STOCK.values()])).text.strip()
    r = r.split(';')[:-1]
    r = [i.split('"')[1].split(',')[:] for i in r]
    r = ['%s: \n$%s\n%s+%s \n%s-%s\n' % (i[0], i[1], i[7], _diff(i[1], i[7]), i[6], _diff(i[6], i[1])) for i in r]
    r = '\n'.join(r)
    return r + '\n' + str(datetime.datetime.now())[:19]


def get_cn_stock():
    r = requests.get(SINA_STOCK_URL % ','.join(CN_STOCK.values())).text.strip()
    r = r.split(';')[:-1]
    r = [i.split('"')[1].split(',')[:] for i in r]
    r = ['%s: \n%s\n%s+%s \n%s-%s\n' % (i[0], i[3], i[5], _diff(i[3], i[5]), i[4], _diff(i[4], i[5])) for i in r]
    r = '\n'.join(r)
    return r + '\n' + str(datetime.datetime.now())[:19]


def _diff(a, b):
    return round(float(a) - float(b), 3)
