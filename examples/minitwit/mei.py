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
    return cookies, end_cursor, url


def inst_query(start_cursor, cookies, ref_url):
    url = 'https://www.instagram.com/query/'
    csrftoken = cookies['csrftoken']
    headers = {
        'X-CSRFToken': csrftoken,
        'Referer': ref_url,
    }
    data = {
        'query_id': '17849115430193904',
        'ref': 'users::show',
        'q': 'ig_user(564987626)+{+media.after(%s,+12)+{\n++count,\n++nodes+{\n++++__typename,\n++++caption,\n++++code,\n++++comments+{\n++++++count\n++++},\n++++comments_disabled,\n++++date,\n++++dimensions+{\n++++++height,\n++++++width\n++++},\n++++display_src,\n++++id,\n++++is_video,\n++++likes+{\n++++++count\n++++},\n++++owner+{\n++++++id\n++++},\n++++thumbnail_src,\n++++video_views\n++},\n++page_info\n}\n+}' % start_cursor,
    }
    data='q=ig_user(564987626)+%7B+media.after(1457771457300248551%2C+12)+%7B%0A++count%2C%0A++nodes+%7B%0A++++__typename%2C%0A++++caption%2C%0A++++code%2C%0A++++comments+%7B%0A++++++count%0A++++%7D%2C%0A++++comments_disabled%2C%0A++++date%2C%0A++++dimensions+%7B%0A++++++height%2C%0A++++++width%0A++++%7D%2C%0A++++display_src%2C%0A++++id%2C%0A++++is_video%2C%0A++++likes+%7B%0A++++++count%0A++++%7D%2C%0A++++owner+%7B%0A++++++id%0A++++%7D%2C%0A++++thumbnail_src%2C%0A++++video_views%0A++%7D%2C%0A++page_info%0A%7D%0A+%7D&ref=users%3A%3Ashow&query_id=17849115430193904'
    r = requests.post(url=url, cookies=cookies, data=data, headers=headers)
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

    
