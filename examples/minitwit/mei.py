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
import urllib

"""
curl -i -s -k  -X $'POST' \
-H $'X-CSRFToken: 5dZRowXtZdx8CbZoU4SqNRFhFHCaHQoW' \
-H $'Referer: https://www.instagram.com/djxin_tw/' \
-b $'csrftoken=5dZRowXtZdx8CbZoU4SqNRFhFHCaHQoW' \
--data-binary $'q=ig_user(564987626)+%7B+media.after(1457771457300248551%2C+12)+%7B%0A++count%2C%0A++nodes+%7B%0A++++__typename%2C%0A++++caption%2C%0A++++code%2C%0A++++comments+%7B%0A++++++count%0A++++%7D%2C%0A++++comments_disabled%2C%0A++++date%2C%0A++++dimensions+%7B%0A++++++height%2C%0A++++++width%0A++++%7D%2C%0A++++display_src%2C%0A++++id%2C%0A++++is_video%2C%0A++++likes+%7B%0A++++++count%0A++++%7D%2C%0A++++owner+%7B%0A++++++id%0A++++%7D%2C%0A++++thumbnail_src%2C%0A++++video_views%0A++%7D%2C%0A++page_info%0A%7D%0A+%7D&ref=users%3A%3Ashow&query_id=17849115430193904' \
$'https://www.instagram.com/query/'
"""


"""
Found a better way to get json from inst:
Init call get end_cursor, use end_cursor as max_id to keep retrieve more

https://www.instagram.com/djxin_tw/?__a=1&max_id=1474857804955451050
"""

"""
sessionid in cookie for private inst; shuffled ex:
cookies['sessionid']='IGSC593b290e94db4cfc6431895d3d4afbbf4d369643c4163593f29e808716:EdNgfqySh6SDEQ5Zx7FQeQGHtYNc:{"asns":{"time":1491448126,"103.211.193.88":135391},"_auth_user_id":0002323020,"_platform":4,"_auth_user_backend":"accounts.backends.CaseInsensitiveModelBackend","last_refreshed":1491448127.0286159515,"_auth_user_hash":"","_token":"2969173752:ZOYZQFh3sPzMzvhXQ51CooOAbUVvhq8F:8b8c328f724c0df8c8cba73615054f50873ccdd33e8f3b6a97e5b2227","_token_ver":2}'
"""

tz = pytz.timezone('Asia/Shanghai')

SESSION_ID = None

def set_cookie(x):
    x = urllib.unquote(x)
    global SESSION_ID
    SESSION_ID = x

def inst_init(id='djxin_tw'):
    url = 'https://www.instagram.com/%s/' % id
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
    if SESSION_ID:
        cookies['sessionid'] = SESSION_ID
    return end_cursor, cookies, url, user_id
    #return inst_init__a(id)


def inst_init__a(id='djxin_tw'):
    url = 'https://www.instagram.com/%s/?__a=1' % id
    r = requests.get(url=url, verify=False)
    x = json.loads(r.text)
    end_cursor = x['user']['media']['page_info']['end_cursor']
    cookies = r.cookies.get_dict()
    user_id = x['user']['id']
    return end_cursor, cookies, url, user_id


def inst_init_private(id='rinajackmimi', session_id=None):
    if not session_id:
        session_id = SESSION_ID
    url = 'https://www.instagram.com/%s/?__a=1' % id
    r = requests.get(url=url, verify=False)
    #print r.text
    print '='*50, url
    x = json.loads(r.text)
    end_cursor = x['user']['media']['page_info']['end_cursor']
    cookies = r.cookies.get_dict()
    user_id = x['user']['id']
    cookies['sessionid'] = session_id
    count = x['user']['media']['count']
    return end_cursor, cookies, url, user_id, count 


def inst_get_following(n=9999):
    url = 'https://www.instagram.com/graphql/query/?query_id=17874545323001329&id=2969173752&first=' + str(n)
    cookies = {}
    cookies['sessionid'] = SESSION_ID
    r = requests.get(url=url, cookies=cookies, verify=False)
    d = json.loads(r.text)
    #pprint(d)
    nodes = d['data']['user']['edge_follow']['edges']
    r = [n['node']['username'] for n in nodes]
    print r
    return r


def inst_private__a(id='rinajackmimi', session_id=None):
    nodes = []
    s = 2
    c = 1
    if not session_id:
        session_id = SESSION_ID
    print '!'*50, session_id
    if not session_id:
        return nodes
    end_cursor, cookies, url, user_id = inst_init__a(id)
    max_id = end_cursor
    cookies['sessionid'] = session_id
    while True:
        time.sleep(s)
        url = 'https://www.instagram.com/%s/?__a=1&max_id=%s' % (id, max_id)
        try:
            r = requests.get(url=url, cookies=cookies, verify=False)
        except Exception, e:
            print str(e)
            s = s * 2
            print '!'*50, s
            continue
        #print r.text
        x = json.loads(r.text)
        n = x['user']['media']['nodes']
        nodes += n
        end_cursor = x['user']['media']['page_info']['end_cursor']
        count = x['user']['media']['count']
        has_next_page = x['user']['media']['page_info']['has_next_page']
        max_id = end_cursor
        c += 1
        print '='*50, c, s, count, id
        pprint(len(n))
        if s > 2:
            s = s / 2
        if not has_next_page:
            break
    return nodes


def inst_new_private(id, session_id=None):
    nodes = inst_private__a(id, session_id)
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


def inst_update_private(id='rinajackmimi', session_id=None):
    max_id, cookies, ref_url, user_id, count = inst_init_private(id, session_id)
    print '-'*50, count, id
    old_count = md.InstMei.query.filter_by(inst_owner=id).count()
    if old_count >= count:
        print '-'*50, id, 'no update', old_count, count
        return 
    #if ok loop
    c = 1
    s = 2
    while True:
        flag = False
        time.sleep(s)
        url = 'https://www.instagram.com/%s/?__a=1&max_id=%s' % (id, max_id)
        try:
            r = requests.get(url=url, cookies=cookies, verify=False)
        except Exception, e:
            print str(e)
            s = s * 2
            print '!'*50, s
            continue
        #print r.text
        x = json.loads(r.text)
        nodes = x['user']['media']['nodes']
        end_cursor = x['user']['media']['page_info']['end_cursor']
        count = x['user']['media']['count']
        has_next_page = x['user']['media']['page_info']['has_next_page']
        max_id = end_cursor
        #pprint(nodes)
        for n in nodes:
            #pprint(n)
            x = md.InstMei.query.filter_by(inst_code=(n['code'])).first()
            if x:
                flag = True
                print ';'*50,n['code']
            else:
                m = md.InstMei(inst_owner=id,
                               inst_code=n['code'],
                               inst_ts=n['date'],
                               display_src=n['display_src'],
                               inst_id=n['id'],
                               thumbnail_src=n['thumbnail_src']
                )
                md.flush(m)
        c += 1
        print '='*50, c, s, count, id
        pprint(len(n))
        if s > 2:
            s = s / 2
        if not has_next_page:
            break
        if flag:
            print '*'*50, 'done update', old_count, count
            return
    return


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
    start_cursor, cookies, ref_url, user_id = inst_init(id)
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
    start_cursor, cookies, ref_url, user_id = inst_init(id)
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
    'emrata',
    'danbilzerian',
    'joannakrupa',
    'actressclara',
    'melwitharosee',
    'rachelc00k',
    'elizabethcturner',
]

OWNER_LIST = [u'milaazul', u'red_fox_official1', u'_milenangel_', u'itsdeedster', u'sabrinalynnci', u'emilybloomofficial', u'alice_posse', u'stormy.jpeg', u'sky3mfc', u'sandrageorgiapopa', u'kitty_catxox', u'heyashleytea', u'alexapond_', u'callmems.molly', u'emilytokes', u'rise_xo', u'nintend.xo', u'sunnhii3e', u'lunalanie', u'reyasroom', u'verabambii', u'verabambilive', u'reya__sunshine', u'nataliesng', u'lexivixi', u'svetabily', u'helga_model', u'galina_dub', u'lovelynnc', u'highestheaven', u'kristinabasham', u'lindseypelas', u'saraunderwood', u'playboy', u'bikinidolls', u'sitabellan', u'adrianneho', u'chodakowskaewa', u'karolina_pisarek', u'rosylip123', u'bygracekim', u'lovelyjoohee', u'seojin_ban', u'mi_______u', u'anllela_sagra', u'sommerray2', u'sommerray', u'lynaritaa', u'juli.annee', u'lovely_ahyeong', u'superbaby_dy', u'jieun_han', u'cxxsomi', u'baby_bin47', u'angelyunmi', u'leejina.angel', u'park_sihyun', u'sylvia.1204', u'shamandalie.sg', u'riae_', u'eliselaurenne', u'darshelle_stevens', u'jazzychewter', u'super_kaif', u'ukrainian.beautiful.girls', u'hot.berries', u'hot_girls_everyday_', u'flinktheworld', u'naomihype', u'willypelayo', u'georgecortina', u'skyjuu', u'niponas.kawaii', u'love.curve', u'terminushoot', u'lie.wilawan', u'mariaskyy', u'kkaaww', u'amouranth', u'madi.kat', u'casteels', u'rosiehw', u'realbarbarapalvin', u'marthahunt', u'romeestrijd', u'josephineskriver', u'mirandakerr', u'bellahadid', u'gigihadid', u'taylor_hill', u'angelcandices', u'doutzen', u'alessandraambrosio', u'chiaraferragni', u'itskaylaerin', u'amythunderbolt', u'misalynnclp', u'inran_hibiki', u'makihojyo', u'kizaki_jessica', u'asukakiraran', u'yua_mikami', u'shibuya_yuri', u'l92833', u'vickycc061', u'cherry_quahst', u'laine_laineng', u'maybe_iamawesome', u'gatitayan888', u'_reiikoyuii', u'peiyu0515', u'instababe_universe', u'insta_hotpeople', u'fffrofaizzz', u'cuteprettygirls', u'instababes.asian', u'sg.my.babes', u'edyta_zajac', u'laboon_girls', u'japanese_cutie_girls', u'gravuremagazine', u'melwitharosee', u'leannabartlett', u'cindyprado', u'emrata', u'danbilzerian', u'hinzajoa', u'lizwenya', u'gingerwangim', u'carinalinn_', u'mayjam101', u'liu1ting', u'jjdogdiary', u'mikibaby_w', u'icicbaby', u'crysta1lee', u'cyndi811213', u'yuibabeshop', u'yui_xin_', u'pinkyyyy520', u'sabrinaanellie', u'hwangbarbie', u'hilaryhrhoda', u'actressclara', u'djxin_tw', u'officialhatano', u'jenna_chew', u'chiababy116', u'alicebambam', u'joanne_722', u'chi_7_7_', u'44lucifer77', u'lucycecile', u'nuuu.07', u'rinajackmimi', u'joannakrupa', u'lenagercke', u'kaypikefashion', u'victoriassecret', u'arianagrande', u'nike', u'instagram']


OWNER_LIST = [u'mybossgirls', u'bossgirls', u'blakelybunny', u'jessicakes33', u'natasha_k_t', u'anastasia_skyline', u'ninaserebrova', u'zuueva', u'amandaeliselee', u'galina.dub', u'vi_odintcova', u'viki_odintcova', u'aroundchernyavsky', u'chernyavskyphoto', u'art_of_ck', u'margo.amp', u'marykalisy', u'alexlynn_art', u'milaazul', u'red_fox_official1', u'_milenangel_', u'itsdeedster', u'sabrinalynnci', u'emilybloomofficial', u'alice_posse', u'stormy.jpeg', u'sky3mfc', u'sandrageorgiapopa', u'kitty_catxox', u'heyashleytea', u'alexapond_', u'callmems.molly', u'emilytokes', u'rise_xo', u'nintend.xo', u'sunnhii3e', u'lunalanie', u'reyasroom', u'verabambii', u'verabambilive', u'reya__sunshine', u'nataliesng', u'lexivixi', u'svetabily', u'helga_model', u'galina_dub', u'lovelynnc', u'highestheaven', u'kristinabasham', u'lindseypelas', u'saraunderwood', u'playboy', u'bikinidolls', u'sitabellan', u'adrianneho', u'chodakowskaewa', u'karolina_pisarek', u'rosylip123', u'bygracekim', u'lovelyjoohee', u'seojin_ban', u'mi_______u', u'anllela_sagra', u'sommerray2', u'sommerray', u'lynaritaa', u'juli.annee', u'lovely_ahyeong', u'superbaby_dy', u'jieun_han', u'cxxsomi', u'baby_bin47', u'angelyunmi', u'leejina.angel', u'park_sihyun', u'sylvia.1204', u'shamandalie.sg', u'riae_', u'eliselaurenne', u'darshelle_stevens', u'jazzychewter', u'super_kaif', u'ukrainian.beautiful.girls', u'hot.berries', u'hot_girls_everyday_', u'flinktheworld', u'naomihype', u'willypelayo', u'georgecortina', u'skyjuu', u'niponas.kawaii', u'love.curve', u'terminushoot', u'julie.wilawan', u'mariaskyy', u'kkaaww', u'amouranth', u'madi.kat', u'casteels', u'rosiehw', u'realbarbarapalvin', u'marthahunt', u'romeestrijd', u'josephineskriver', u'mirandakerr', u'bellahadid', u'gigihadid', u'taylor_hill', u'angelcandices', u'doutzen', u'alessandraambrosio', u'chiaraferragni', u'itskaylaerin', u'amythunderbolt', u'misalynnclp', u'inran_hibiki', u'makihojyo', u'kizaki_jessica', u'asukakiraran', u'yua_mikami', u'shibuya_yuri', u'l92833', u'vickycc061', u'cherry_quahst', u'laine_laineng', u'maybe_iamawesome', u'gatitayan888', u'_reiikoyuii', u'peiyu0515', u'instababe_universe', u'insta_hotpeople', u'fffrofaizzz', u'cuteprettygirls', u'instababes.asian', u'sg.my.babes', u'edyta_zajac', u'laboon_girls', u'japanese_cutie_girls', u'gravuremagazine', u'melwitharosee', u'leannabartlett', u'cindyprado', u'emrata', u'danbilzerian', u'hinzajoa', u'lizwenya', u'gingerwangim', u'carinalinn_', u'mayjam101', u'liu1ting', u'jjdogdiary', u'mikibaby_w', u'icicbaby', u'crysta1lee', u'cyndi811213', u'yuibabeshop', u'yui_xin_', u'pinkyyyy520', u'sabrinaanellie', u'hwangbarbie', u'hilaryhrhoda', u'actressclara', u'djxin_tw', u'officialhatano', u'jenna_chew', u'chiababy116', u'alicebambam', u'joanne_722', u'chi_7_7_', u'44lucifer77', u'lucycecile', u'nuuu.07', u'rinajackmimi', u'joannakrupa', u'lenagercke', u'kaypikefashion', u'victoriassecret', u'arianagrande', u'nike', u'instagram']

PRIVATE_LIST = [
    'rinajackmimi',
    'nuuu.07',
    'mybossgirls',
    #'mainitipanty',
    'beautiful_hip',
    'ranranranran026',
    'fallen_angel__666__',
    'h_r_k_nts',
    'ri30ri30',
    's3xysophia',
    'yui_4402',
    'meri6_6meri',
]

EXCLUDE_LIST = [
    'nike',
    'instagram',
    'bodygirlsdaily',
    'college.girlz',
]
OWNER_LIST = [i for i in OWNER_LIST if i not in PRIVATE_LIST and i not in EXCLUDE_LIST]


def test_new(c):
    set_cookie(c)
    global OWNER_LIST
    OWNER_LIST = inst_get_following()
    OWNER_LIST = [i for i in OWNER_LIST if i not in PRIVATE_LIST and i not in EXCLUDE_LIST]
    up()
    up_private()

def up():
    global PRIVATE_LIST
    private_new = []
    c = 1
    k = len(OWNER_LIST)
    for id in OWNER_LIST:
        print '='*50, id
        try:
            inst_update(id)
        except:
            print '*'*50, 'new private id', id
            private_new.append(id)
            PRIVATE_LIST.append(id)
        print '+'*50, c, k
        c += 1
    print '%'*50, private_new
    with open('np.txt', 'a') as f:
        f.write(str(private_new)+'\n')

def up_private():
    #default off
    global PRIVATE_LIST
    PRIVATE_LIST = [ i for i in PRIVATE_LIST if i not in EXCLUDE_LIST]
    if SESSION_ID:
        for id in PRIVATE_LIST:
            inst_update_private(id)
