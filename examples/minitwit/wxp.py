# -*- coding: utf-8 -*-
import requests
import json

def p():
    openid = "o7VbEjuienGcLf33ZQ-V8bk0g67Q"
    host = "http://wx83214.weixiaoxin.com/Vipvote/vote?wid=83214&id=4753&openid={openid}".format(openid=openid)
    para = {}#{"wid": "83214",
            #"id": "4753",
            #"openid": "o7VbEjuienGcLf33ZQ-V8bk0g67Q",
            #}
    data = {"eid": "152536",
            "formhash": "47vkKnE1/XxA6",
            }
    headers = {"X-Requested-With": "XMLHttpRequest",
               "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 9_2_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Mobile/13D15 MicroMessenger/6.3.15 NetType/WIFI Language/zh_CN",
               "Cookie": "Hm_lpvt_50e8608aef835699234de1e805173bbd=1458712338o7VbEjuienGcLf33ZQ-V8bk0g67Q; Hm_lvt_50e8608aef835699234de1e805173bbd=1458712333; PHPSESSID=9k1rr2jk43qict1725qpsj5fh3; c_4753=o8qVGuD1L07_kBZ5IhTWj7bhxMnE; vipvopenid_83214_4753={openid}; vipvoteopenid_83214_4753={openid}".format(openid=openid),
               "Accept": "application/json, text/javascript, */*; q=0.01",
               "Accept-Encoding": "gzip, deflate",
               "Accept-Language": "zh-cn",
               "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
               "Origin": "http://wx83214.weixiaoxin.com",
               "Referer": "http://wx83214.weixiaoxin.com/Vipvote/index2?wid=83214&openid={openid}&id=4753".format(openid=openid),
               }

    r = requests.post(url=host, data=data, params=para, headers=headers)
    print r.text
    a = json.loads(r.text)
    for k in a:
        print k, a[k]
    return r
