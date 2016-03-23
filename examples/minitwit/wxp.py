# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import requests
import json
from functools import wraps
import time

OPEN_ID = ["o7VbEjuienGcLf33ZQ-V8bk0g67Q",
           "o7VbEjtmpDA2YpVB3osiogcH6cTw",
           "o7VbEjh-r-f9-TTtOwbZXXcgMITY",
           "o7VbEjrJ8TIPEWNsW06C1LDdCZb4",
           ]


def main():
    for i, openid in enumerate(OPEN_ID):
        print '-----------%s------------' % i
        p(openid)


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


@ex("error")
def p(openid="o7VbEjuienGcLf33ZQ-V8bk0g67Q"):
    host = "http://wx83214.weixiaoxin.com/Vipvote/vote?wid=83214&id=4753&openid={openid}".format(openid=openid)
    ts = int(time.time())
    para = {}#{"wid": "83214",
            #"id": "4753",
            #"openid": "o7VbEjuienGcLf33ZQ-V8bk0g67Q",
            #}
    data = {"eid": "155415",
            "formhash": "47vkKnE1/XxA6",
            }
    headers = {"X-Requested-With": "XMLHttpRequest",
               "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 9_2_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Mobile/13D15 MicroMessenger/6.3.15 NetType/WIFI Language/zh_CN",
               "Cookie": "Hm_lpvt_50e8608aef835699234de1e805173bbd={ts}; Hm_lvt_50e8608aef835699234de1e805173bbd={ts}; PHPSESSID=9k1rr2jk43qict1725qpsj5fh3; c_4753=o8qVGuD1L07_kBZ5IhTWj7bhxMnE; vipvopenid_83214_4753={openid}; vipvoteopenid_83214_4753={openid}".format(openid=openid, ts=ts),
               "Accept": "application/json, text/javascript, */*; q=0.01",
               "Accept-Encoding": "gzip, deflate",
               "Accept-Language": "zh-cn",
               "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
               "Origin": "http://wx83214.weixiaoxin.com",
               "Referer": "http://wx83214.weixiaoxin.com/Vipvote/index2?wid=83214&openid={openid}&id=4753".format(openid=openid),
               }

    r = requests.post(url=host, data=data, params=para, headers=headers)
    print len(r.text)
    a = json.loads(r.text)
    for k in a:
        print openid, k, a[k]
    return r
