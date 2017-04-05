# -*- coding: utf-8 -*-
import pytz
import requests
from bs4 import BeautifulSoup
from pprint import pprint
import datetime
import csv
import time
import json
import models.model_mei as md

"""
curl -i -s -k  -X $'POST' \
-H $'X-CSRFToken: 5dZRowXtZdx8CbZoU4SqNRFhFHCaHQoW' \
-H $'Referer: https://www.instagram.com/djxin_tw/' \
-b $'csrftoken=5dZRowXtZdx8CbZoU4SqNRFhFHCaHQoW' \
--data-binary $'q=ig_user(564987626)+%7B+media.after(1457771457300248551%2C+12)+%7B%0A++count%2C%0A++nodes+%7B%0A++++__typename%2C%0A++++caption%2C%0A++++code%2C%0A++++comments+%7B%0A++++++count%0A++++%7D%2C%0A++++comments_disabled%2C%0A++++date%2C%0A++++dimensions+%7B%0A++++++height%2C%0A++++++width%0A++++%7D%2C%0A++++display_src%2C%0A++++id%2C%0A++++is_video%2C%0A++++likes+%7B%0A++++++count%0A++++%7D%2C%0A++++owner+%7B%0A++++++id%0A++++%7D%2C%0A++++thumbnail_src%2C%0A++++video_views%0A++%7D%2C%0A++page_info%0A%7D%0A+%7D&ref=users%3A%3Ashow&query_id=17849115430193904' \
$'https://www.instagram.com/query/'
"""

tz = pytz.timezone('Asia/Shanghai')



def inst_init(url='https://www.instagram.com/djxin_tw/'):
    r = requests.get(url=url, verify=False)
    cookies = r.cookies.get_dict()
    t = r.text
    n = t.find('end_cursor')
    t = t[n:]
    m = t.find('}')
    t =  t[:m]
    end_cursor = t.split('"')[2]
    t = r.text
    n = t.find('"owner": {"id"')
    t = t[n: n+50]
    user_id = t.split('"')[5]
    return end_cursor, cookies, url, user_id


PROXY = {'http': 'http://127.0.0.1:8080',
         'https': 'http://127.0.0.1:8080',
        }

PROXY = None

def inst_query(start_cursor, cookies, ref_url, user_id):
    url = 'https://www.instagram.com/query/'
    csrftoken = cookies['csrftoken']
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; U; Android 4.0; en-us; GT-I9300 Build/IMM76D) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30',
        'X-CSRFToken': csrftoken,
        'Referer': ref_url,
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    data='q=ig_user({uid})+%7B+media.after({sc}%2C+12)+%7B%0A++count%2C%0A++nodes+%7B%0A++++__typename%2C%0A++++caption%2C%0A++++code%2C%0A++++comments+%7B%0A++++++count%0A++++%7D%2C%0A++++comments_disabled%2C%0A++++date%2C%0A++++dimensions+%7B%0A++++++height%2C%0A++++++width%0A++++%7D%2C%0A++++display_src%2C%0A++++id%2C%0A++++is_video%2C%0A++++likes+%7B%0A++++++count%0A++++%7D%2C%0A++++owner+%7B%0A++++++id%0A++++%7D%2C%0A++++thumbnail_src%2C%0A++++video_views%0A++%7D%2C%0A++page_info%0A%7D%0A+%7D&ref=users%3A%3Ashow&query_id=17849115430193904'.format(sc=start_cursor, uid=user_id)
    r = requests.post(url=url, cookies=cookies, data=data, headers=headers, proxies=PROXY, verify=False)
    t = r.text
    #print user_id
    d = json.loads(t)
    #print d
    media = d['media']
    page_info = media['page_info']
    end_cursor = page_info['end_cursor']
    count = media['count']
    nodes = media['nodes'] 
    return end_cursor, nodes, count


def inst_fetch(id='djxin_tw'):
    r = []
    url = 'https://www.instagram.com/%s/' % id
    start_cursor, cookies, ref_url, user_id = inst_init(url)
    #first query
    end_cursor, nodes, count = inst_query(start_cursor, cookies, ref_url, user_id)
    print '-'*50, count, id
    #if ok loop
    r += nodes
    c = 1
    s = 2
    while nodes:
        time.sleep(s)
        start_cursor = end_cursor
        try:
            end_cursor, nodes, count = inst_query(start_cursor, cookies, ref_url, user_id)
        except Exception, e:
            print str(e)
            s = s * 2
            print '!'*50, s
            continue
        r += nodes
        c += 1
        print '='*50, c, s
        pprint(len(nodes))
        if s > 2:
            s = s / 2
    return r


def inst_new(id):
    nodes = inst_fetch(id)
    c = 0
    for n in nodes:
        m = md.InstMei(inst_owner=id,
                       inst_code=n['code'],
                       inst_ts=n['date'],
                       display_src=n['display_src'],
                       inst_id=n['id'],
                       thumbnail_src=n['thumbnail_src']
        )
        md.flush(m)
        c += 1
        print '-'*50, c


def inst_update(id='djxin_tw'):
    r = []
    url = 'https://www.instagram.com/%s/' % id
    start_cursor, cookies, ref_url, user_id = inst_init(url)
    #first query
    end_cursor, nodes, count = inst_query(start_cursor, cookies, ref_url, user_id)
    print '-'*50, count, id
    old_count = md.InstMei.query.filter_by(inst_owner=id).count()
    if old_count >= count:
        print '-'*50, id, 'no update', old_count, count
        return 
    #if ok loop
    r += nodes
    c = 1
    s = 2
    while nodes:
        flag = False
        for n in nodes:
            #pprint(n)
            x = md.InstMei.query.filter_by(inst_code=(n['code'])).first()
            if x:
                flag = True
            else:
                m = md.InstMei(inst_owner=id,
                               inst_code=n['code'],
                               inst_ts=n['date'],
                               display_src=n['display_src'],
                               inst_id=n['id'],
                               thumbnail_src=n['thumbnail_src']
                )
                md.flush(m)
        if flag:
            print '*'*50, 'done update', old_count, count
            return

        time.sleep(s)
        start_cursor = end_cursor
        try:
            end_cursor, nodes, count = inst_query(start_cursor, cookies, ref_url, user_id)
        except Exception, e:
            print str(e)
            s = s * 2
            print '!'*50, s
            continue
        r += nodes
        c += 1
        print '='*50, c, s
        pprint(len(nodes))
        if s > 2:
            s = s / 2
    return


OWNER_LIST = [
    'cindyprado',
    'djxin_tw',
    'hinzajoa',
    'jenna_chew',
    'leannabartlett',
    'yui_xin_',
]
def up():
    for id in OWNER_LIST:
        inst_update(id)
