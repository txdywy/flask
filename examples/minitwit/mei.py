# -*- coding: utf-8 -*-
import pytz
import requests
from bs4 import BeautifulSoup
from pprint import pprint
import datetime
import csv
import time
import json

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
    return r


def get_inst(key='hinzajoa'):
    url = 'https://www.instagram.com/' + key + '/' 
    r = requests.get(url=url, verify=False).text
    s = BeautifulSoup(r)
    a = s.findAll("div", { "class" : 'single-review'})
    x = []
    print len(a)
    for i in a:
        star = i.find("div", {"class": "tiny-star"}).attrs['aria-label']
        star = int(star.split(' ')[2])
        if star > 3:
            rev = i.find("div", {"class": "review-body"})
            title = rev.find("span").text
            content = rev.text
            x.append([star, title, content])

    
