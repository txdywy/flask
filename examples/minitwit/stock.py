# -*- coding: utf-8 -*-
import requests

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
    r = [i.split('"')[1].split(',')[:2] for i in r]
    r = ['%s: $%s\n' % (i[0], i[1]) for i in r]
    r = ''.join(r)
    return r


def get_cn_stock():
    r = requests.get(SINA_STOCK_URL % ','.join(CN_STOCK.values())).text.strip()
    r = r.split(';')[:-1]
    r = [i.split('"')[1].split(',')[:6] for i in r]
    r = ['%s: %s [%s+%s, %s-%s]\n' % (i[0], i[3], i[5], round(float(i[3]) - float(i[5]), 3), i[4], round(float(i[4]) - float(i[3]), 3)) for i in r]
    r = ''.join(r)
    return r
