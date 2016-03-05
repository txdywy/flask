# -*- coding: utf-8 -*-
import gevent
#from gevent import monkey
#monkey.patch_all()
from ib import IB_BOOK
import stock
import ierror, time
from WXBizMsgCrypt import SHA1
import xml.etree.ElementTree as ET
from flask import make_response
from pygoogle import pygoogle
import re, jieba, jieba.analyse
import urllib2, json
from bs4 import BeautifulSoup
import cache as cachewx
from bosonnlp import BosonNLP
from urlparse import urlparse, parse_qs
WX_CACHE_GENERAL_KEY = 'wx.cache.general.key.%s'
WX_CACHE_RESULT_KEY = 'wx.cache.result.key.%s'
WX_LAST_CONTENT_TIMEOUT = 24 * 60 * 60
from config import ALANCER_HOST
try:
    from config import WX_TULING_API_KEY
except:
    print '-----------------no TULING api key--------------'
    WX_TULING_API_KEY = ''
try:
    from config import BOSON_API_TOKEN
    BSNLP = BosonNLP(BOSON_API_TOKEN)
except:
    print '---------------no BOSON api key--------------'
    BOSON_APT_TOKEN = ''
    BSNLP = None
    
BOSON_NEWS_CATEGORY = ['体育', '教育', '财经', '社会', '娱乐', '军事', '国内', '科技', '互联网', '房产', '国际', '女人', '汽车', '游戏']    
WX_TULING_API_URL = 'http://www.tuling123.com/openapi/api?key=' + WX_TULING_API_KEY + '&info=%s'

try:
    from config import FPP_API_KEY, FPP_API_SECRET, FPP_REGION
except:
    print '----------------no FPP api key------------------'
    FPP_API_KEY = FPP_API_SECRET = FPP_REGION = ''
FPP_FACE_DETECT_API_URL = 'http://api%s.faceplusplus.com/v2/detection/detect?api_key=%s' % (FPP_REGION, FPP_API_KEY) +'&api_secret=%s' % FPP_API_SECRET +'&url=%s&attribute=glass,pose,gender,age,race,smiling'

FPP_FACE_COMPARE_API_URL = 'http://api%s.faceplusplus.com/v2/recognition/compare?api_key=%s' % (FPP_REGION, FPP_API_KEY) +'&api_secret=%s' % FPP_API_SECRET + '&face_id2=%s&face_id1=%s'

from models.model_wechat import *
from random import randint
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import codecs
from textrank4zh import TextRank4Keyword, TextRank4Sentence
import proxy
import ticket
import threading, Queue

class TiAsyncTask(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.tasks = Queue.Queue()
        self.setDaemon(True)
        print '=====thread init====='

    def put(self, d): 
        self.tasks.put(d)

    def run(self):
        while True:
            try:
                d = self.tasks.get(timeout=1)
                if d:
                    #ticket.ti(int(d), 3)
                    import nti
                    for i in xrange(int(d)):
                        nti.geti()
                print '=====thread task done===='
            except Exception, e:
                #print '-----threading err-----', str(e)
                pass
            time.sleep(5)

TICKET_ASYNC_THREAD = TiAsyncTask()

URL_RE = re.compile(
        r'^(?:http)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

WX_SHA1 = SHA1()

WX_TEMPLATE_TEXT = "<xml><ToUserName><![CDATA[%s]]></ToUserName><FromUserName><![CDATA[%s]]></FromUserName><CreateTime>%s</CreateTime><MsgType><![CDATA[text]]></MsgType><Content><![CDATA[%s]]></Content><FuncFlag>0</FuncFlag></xml>"

WX_TEMPLATE_IMG = "<xml><ToUserName><![CDATA[%s]]></ToUserName><FromUserName><![CDATA[%s]]></FromUserName><CreateTime>%s</CreateTime><MsgType><![CDATA[image]]></MsgType><Image><MediaId><![CDATA[%s]]></MediaId></Image></xml>"

WX_TEMPLATE_IMG_TEXT = "<xml>  \
<ToUserName><![CDATA[%s]]></ToUserName>  \
<FromUserName><![CDATA[%s]]></FromUserName>  \
<CreateTime>%s</CreateTime>  \
<MsgType><![CDATA[news]]></MsgType>  \
<ArticleCount>1</ArticleCount>  \
<Articles>  \
<item>  \
<Title><![CDATA[%s]]></Title>  \
<Description><![CDATA[%s]]></Description>  \
<PicUrl><![CDATA[%s]]></PicUrl>  \
<Url><![CDATA[%s]]></Url>  \
</item>  \
</Articles>  \
</xml> "

WX_TEMPLATE_NEWS_HEAD = "<xml>  \
<ToUserName><![CDATA[%s]]></ToUserName>  \
<FromUserName><![CDATA[%s]]></FromUserName>  \
<CreateTime>%s</CreateTime>  \
<MsgType><![CDATA[news]]></MsgType>"

WX_TEMPLATE_NEWS_BODY = "<ArticleCount>%s</ArticleCount>  \
<Articles>  \
%s  \
</Articles>  \
</xml> "

WX_TEMPLATE_NEWS_ITEM = "<item>  \
<Title><![CDATA[%s]]></Title>  \
<Description><![CDATA[%s]]></Description>  \
<PicUrl><![CDATA[%s]]></PicUrl>  \
<Url><![CDATA[%s]]></Url>  \
</item>"

TIGER_URL_TEMPLATE = 'http://t.hujiang.com/images/peitu/huhu/%s.jpg'

def get_google_news(user_name_from, user_name_to, word):
    g = pygoogle(word)
    g.pages = 1
    d = g.search()
    head = WX_TEMPLATE_NEWS_HEAD % (user_name_from, user_name_to, str(time.time()))
    n = len(d.keys())
    items = ''.join([WX_TEMPLATE_NEWS_ITEM % (k, k, TIGER_URL_TEMPLATE % (i+1), d[k]) for i, k in enumerate(d)])
    body = WX_TEMPLATE_NEWS_BODY % (str(n), items)
    return head + body

def fpp_face_detect(pic_url):
    r = urllib2.urlopen(FPP_FACE_DETECT_API_URL % urllib2.quote(pic_url)).read()
    return json.loads(r)

def fpp_face_compare(fid1, fid2):
    r = urllib2.urlopen(FPP_FACE_COMPARE_API_URL % (fid2, fid1)).read()
    return json.loads(r)

FPP_GLASS_EMOJI = '👓'
def reply_pic(user_name_from, user_name_to, pic_url, skey):
    r = fpp_face_detect(pic_url)
    print '==========', r
    pic_url = r['url']
    head = WX_TEMPLATE_NEWS_HEAD % (user_name_from, user_name_to, str(time.time()))
    web_url = 'http://%s/wechat/share?k=' % ALANCER_HOST + skey
    fs = r.get('face')
    print '============',len(fs)
    if not fs:
        title = '没脸见人咯?怪我咯?!'
        abstract = '看了看图,我只能说,美女都走光了...'
    elif len(fs) == 1:
        a = r['face'][0]['attribute']
        g = True if a['gender']['value'] == 'Male' else False
        t = '发现帅锅💂一枚' if g else '探测美眉👠一颗'
        title = t + ' 年龄:%s' % (a['age']['value'] + a['age']['range'])
        glass = a['glass']['value']
        if glass == 'Normal':
            ag = '换个潮款的眼镜👓吧' if randint(0,1) else '不带眼镜更美🌎'
        elif glass == 'Dark':
            ag = '墨镜很潮哇🌝' if randint(0,1) else '不带墨镜更美😈'
        else:
            ag = '要不要考虑戴个眼镜😖' if randint(0,1) else '果然不戴眼镜比较好看哦😄'
        race, rv = a['race']['value'], a['race']['confidence']
        if race == 'Asian':
            ar = '皮肤不错😁' if rv < 90 else '需要好好保养一下皮肤呢😜'
        elif race == 'White':
            ar = '皮肤真是白嫩呢😍' if rv > 90 else '小脸算白了'
        else:
            ar = '你是刚去了巴厘岛还是掉煤堆里了，额滴包大人😂' if rv < 90 else '阁下好黑...'
        abstract = ' '.join([POSITIVE_EMOJI + '灿烂值:%s' % (str(a['smiling']['value']) + '%'), ar, ag])
    elif len(fs) > 1:
        fid1 = r['face'][0]['face_id']
        fid2 = r['face'][1]['face_id']
        r = fpp_face_compare(fid1, fid2)
        print '============',r
        title = '配对💘指数:%s' % (str(r['similarity']) + '%')
        cs = []
        cs.append('💋:' + str(r['component_similarity']['mouth']) + '%')
        cs.append('👀:' + str(r['component_similarity']['eye']) + '%')
        cs.append('👃:' + str(r['component_similarity']['nose']) + '%')
        cs.append('😳:' + str(r['component_similarity']['eyebrow']) + '%')
        cs.append('口眼鼻眉配对指数如上(*^__^*) 嘻嘻……')
        abstract = ' '.join(cs) 
    else:
        title = abstract = '表示什么都看不清,无能为力...'
    items = WX_TEMPLATE_NEWS_ITEM % (title, abstract, pic_url, web_url)
    body = WX_TEMPLATE_NEWS_BODY % ('1', items)
    data = dict(title=title, abstract=abstract, pic_url=pic_url)
    ws = WechatShare(key=skey, tag=0, data=data)
    flush(ws)
    return head + body

def near_get_pois(x, y, key, tag='美食'):
    city = key[:3]
    url = "http://apis.baidu.com/apistore/location/near?keyWord=%s" % key + "&location=%s,%s;" % (y ,x) + "&tag=%s" % tag + "&radius=3000m&cityName=%s" % city + "&sort_rule=0&number=10&page=1&output=json" 
    #"&coord_type=bd09ll&out_coord_type=bd09ll"
    print ' ==========',url
    req = urllib2.Request(url)
    req.add_header("apikey", "6e285c0e75b3fdcb7ccac476f2c7216b")
    r = urllib2.urlopen(req).read()
    return json.loads(r)

def reply_loc(user_name_from, user_name_to, x, y, k):
    r = near_get_pois(x, y, k)
    p = r['pointList']
    head = WX_TEMPLATE_NEWS_HEAD % (user_name_from, user_name_to, str(time.time()))
    n = len(p)
    #print '=============', [i['additionalInformation'] for i in p]
    its = []
    for index, i in enumerate(p):
        ai = i.get('additionalInformation')
        ai = ai if ai else {}
        url = 'http://m.dianping.com/shoplist/2/search?keyword=%s' % i['name']
        #url = ai['link'][0]['url'] if 'link' in ai else 'http://m.dianping.com/shoplist/2/search?keyword=%s' % i['name']
        it = WX_TEMPLATE_NEWS_ITEM % (('%s (%s) ' + "🐯" + '类型:%s 价位:%s 电话:%s') % (i['name'], i.get('address', ''), ai.get('tag', '无'), ai.get('price', '无'), ai.get('telephone', '无')), i.get('address', ''), TIGER_URL_TEMPLATE % (index % 10 + 1) ,url)
        its.append(it)
    if not p:
        its = [WX_TEMPLATE_NEWS_ITEM % ('啥都没找到...', '...', TIGER_URL_TEMPLATE % 1, 'http://m.dianping.com')]
    items = ''.join(its)
    print '============', items
    body = WX_TEMPLATE_NEWS_BODY % (str(len(its)), items)
    return head + body


def ib(content):
    try:
        a, b = content.split('.')
        a, b = int(a), int(b)
        return IB_BOOK[a]+IB_BOOK[b]
    except:
        print '------not ib-------'
        return None

def check_stock(content):
    try:
        if content == '!7':
            return stock.get_us_stock()
        if content == '!8':
            return stock.get_cn_stock()
        if content == '!6':
            return stock.get_us_in_stock()
    except:
        print '------stock err------'
        return None

def px(content):
    try:
        if content == '!9':
            return proxy.get_top_active() + '\n\nhttp://wxbot.ml/px'
        if '投票' in content:
            d = ticket.rank()[:5]
            return '\n'.join(['[第%s位]' % (n+1) + i[0]+':'+str(i[1]) + ' +%s' % (d[0][1]-i[1]) for n, i in enumerate(d)])
        if '刷票' in content:
            try:
                #i = content.find('刷票')
                #print type(content)
                #print len(content)
                n = int(content[2:])
            except Exception, e:
                n = 10
                print '-----', str(e)
            if not TICKET_ASYNC_THREAD.isAlive():
                try: 
                    TICKET_ASYNC_THREAD.start()
                    print '-----thread started-----'
                except Exception, e:
                    print '-----thread failed-----', str(e)
            TICKET_ASYNC_THREAD.put(n)            
            return '刷%s票中' % n
    except:
        print '------proxy err------'
        return None
    

def check_stock_graph(content):
    if content[0] != '!':
        return None
    c = content[1:]
    print c
    url = None
    if c in stock.US_STOCK:
        url = 'http://ichart.finance.yahoo.com/t?s=' + stock.US_STOCK[c]
    c = c.encode('utf8')
    if c in stock.CN_STOCK:
        url = 'http://image.sinajs.cn/newchart/min/n/%s.gif' % stock.CN_STOCK[c]
    return url


def reply_qr(c, user_name_from, user_name_to):
    r = c.strip().split(' ')
    if 'qr' in  r[-1].lower():
        c = r[0]
    else:
        return None
    img_url = 'http://api.qrserver.com/v1/create-qr-code/?size=150x150&data=' + urllib2.quote(c)
    return _gen_img_response(user_name_from, user_name_to, 'QRCode', c, img_url, img_url)
    

def reply(data):
    reply_tmp = WX_TEMPLATE_TEXT
    xml_recv = ET.fromstring(data)
    user_name_to = xml_recv.find("ToUserName").text
    user_name_from = xml_recv.find("FromUserName").text
    msg_type = xml_recv.find("MsgType").text
    msg_id = xml_recv.find("MsgId").text
    ts = str(int(time.time()))
    skey = '%s_%s' % (msg_id, ts)
    ckey = WX_CACHE_GENERAL_KEY % msg_id
    cr = cachewx.get(ckey)
    print '------------------', ckey
    if cr:
        response = make_response(cr)
        response.content_type = 'application/xml'
        return response

    try:pic_url = xml_recv.find("PicUrl").text
    except:pic_url = None
    if pic_url:
        try:
            result = reply_pic(user_name_from, user_name_to, pic_url, skey)
            cachewx.set(ckey, result, 10 * 60)
            response = make_response(result)
        except Exception, e:
            print '----------', e
            response = make_response(reply_tmp % (user_name_from, user_name_to, str(int(time.time())), 'API err:%s' % str(e)))
        response.content_type = 'application/xml'
        return response

    if msg_type == "location":
        lx = xml_recv.find("Location_X").text
        ly = xml_recv.find("Location_Y").text
        key = xml_recv.find("Label").text
        print '----------------', lx, ly, key
        result = reply_loc(user_name_from, user_name_to, lx, ly, key)
        cachewx.set(ckey, result, 10 * 60)
        response = make_response(result)
        response.content_type = 'application/xml'
        return response

    try:content = xml_recv.find("Content").text
    except:content = ''
    
    if not content:
        try:content = xml_recv.find("Recognition").text
        except:content = ''
    result = content
    if not result:
        response = make_response(reply_tmp % (user_name_from, user_name_to, str(int(time.time())), '你发送的东西微信后台不支持呢(*^__^*) 嘻嘻……'))
        response.content_type = 'application/xml'
        return response
    else:
        p = cachewx.get('WX_LAST_CONTENT')
        if content == 'C':
            if p:
                content = p
                cachewx.set('WX_LAST_CONTENT', content, WX_LAST_CONTENT_TIMEOUT)
        else:
            cachewx.set('WX_LAST_CONTENT', content, WX_LAST_CONTENT_TIMEOUT)

    tmp = 0
    if '小虎' in content:
        result = '小虎最口耐！'
        tmp = 1
    if '猫球' in content:
        result = '猫球棒棒大！'
        tmp = 1
    reply_tmp = WX_TEMPLATE_TEXT
    qr = reply_qr(content, user_name_from, user_name_to)
    if qr:return qr
    ibr = ib(content)
    if ibr:
        tmp = 1
        result = ibr
    cs = check_stock(content)
    if cs:
        tmp = 1
        result = cs
    pxr = px(content)
    if pxr:
        tmp = 1
        result = pxr
    stock_url = check_stock_graph(content)
    if stock_url:
        k = content[1:]
        body = ''
        if k in stock.US_STOCK:
            body = stock.get_one_us_stock(k)
        k = k.encode('utf8')
        if k in stock.CN_STOCK:
            body = stock.get_one_cn_stock(k)
        response = make_response(WX_TEMPLATE_IMG_TEXT % (user_name_from, user_name_to, str(int(time.time())),     content, body, stock_url, stock_url))
        response.content_type = 'application/xml'
        return response
    if '小虎好棒' in content:
        tmp = 1
        reply_tmp = WX_TEMPLATE_IMG
        result = 'e452A-eAAjQzCgYIIcKPxqDb7Z8KoEJpR8hOsTDEbgA8o5bbFsSdWE0UxUc_A2Wf'
    if tmp:
        response = make_response(reply_tmp % (user_name_from, user_name_to, str(int(time.time())), result))
    elif '小虎是谁' in content:
        response = make_response(WX_TEMPLATE_IMG_TEXT % (user_name_from, user_name_to, str(int(time.time())),     '小虎是谁？', '是谁呀？', 'http://t.hujiang.com/images/peitu/huhu/5.jpg', 'http://wxbot.ml'))
    else:
        url = is_url(content)
        print '=============',url
        if url:
            key = WX_CACHE_GENERAL_KEY % url
            content = cachewx.get(key)
            if not content:
                content = get_text_by_url(url)
                cachewx.set(key, content, 60 * 10)
            print '+++++++++++++',url,content
        else:
            if unicode_is_zh(content) and len(content) < 200:
                r = ds_reply(content)
                sense = '' #bs_sentiment(content)
                result = '%s' % sense + json.loads(r)['text']
                response = make_response(reply_tmp % (user_name_from, user_name_to, str(int(time.time())), result))
                response.content_type = 'application/xml'
                return response

        if unicode_is_zh(content):
            rkey = WX_CACHE_RESULT_KEY % url
            result = cachewx.get(rkey)
            if result:
                response = make_response(reply_tmp % (user_name_from, user_name_to, str(int(time.time())), result))
            else:
                seg_list = get_key_words(content)
                result =  '\xe3\x80\x90' + '文章情感晴雨表:%s' % bs_sentiment(content) + '\xe3\x80\x91'
                result += '\xe3\x80\x90' + '文章分类:%s' % bs_calssify(content) + '\xe3\x80\x91'
                result += '\xe3\x80\x90' + '关键词' + '\xe3\x80\x91' + "\xe3\x80\x90%s\xe3\x80\x91" % "🐯".join(seg_list)
                result += '\xF0\x9F\x8C\x8D' + '\xe3\x80\x90' + '摘要' + '\xe3\x80\x91' + "\xe3\x80\x90%s\xe3\x80\x91" % get_text_digest(content)
                cachewx.set(rkey, result, 60 * 10)
            print '--------',result
            response = make_response(reply_tmp % (user_name_from, user_name_to, str(int(time.time())), result))
        else:
            #print '========',repr(content)
            response = make_response(get_google_news(user_name_from, user_name_to, content))
    response.content_type = 'application/xml'
    return response


def _gen_img_response(user_name_from, user_name_to, title, body, img_url, ref_url):
    response = make_response(WX_TEMPLATE_IMG_TEXT % (user_name_from, user_name_to, str(int(time.time())), title, body, img_url, ref_url))
    response.content_type = 'application/xml'
    return response


def unicode_is_zh(data):
    if re.compile(u'[\u4e00-\u9fa5]+').search(data):
        return True
    else:
        return False

def get_key_words(data, topK=20):
    return jieba.analyse.extract_tags(data, topK)

def get_cut_words(data):
    return jieba.cut(content, cut_all=False)

def get_text_digest(data):
    tr4s = TextRank4Sentence(stop_words_file='./stopword.data')
    tr4s.train(text=data, speech_tag_filter=True, lower=True, source = 'all_filters')
    return '\xF0\x9F\x8D\x8B'.join(tr4s.get_key_sentences(num=3))

def get_text_by_url(url="http://www.cnn.com"):
    # weibo
    url_wb = fix_weibo_card(url)
    if url_wb:
        url = url_wb

    # netease
    docid = None
    if fix_netease(url):
        url, docid = get_netease_url(url)
    print '================', url
    request = urllib2.Request(url, headers={"User-Agent" : "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.111 Safari/537.36"})
    html = urllib2.urlopen(request).read()
    if url_wb:
        html = json.loads(html)['data']['article']
    if docid:
        html = json.loads(html[12:-1])[docid]['body']
    soup = BeautifulSoup(html)

    # 36kr
    if fix_36kr(url):
        soup = soup.find("section", {"class": "article"}) 

    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()    # rip it out

    # get text
    text = soup.get_text()
    print '--------------------'

    tlist = text.split('\n')
    tlist = sorted(tlist, key=lambda x:len(x))
    return tlist[-1]

def is_url(data):
    data = data.strip()
    if 'http' != data[:4].lower():
        data = 'http://' + data 
    print '....',data
    if URL_RE.match(data):
        return data
    else:
        return None
    
def fix_weibo_card(url):
    if 'http://card.weibo.com/article/h5/' in url:
        prefix = 'http://card.weibo.com/article/aj/articleshow?cid='
        #url = prefix + url[39:]
        url = prefix + url[url.find('cid=') + 4:]
        return url
    else:
        return None

def fix_36kr(url):
    if '36kr.com' in url:
        return True
    return False

def fix_netease(url):
    if '3g.163.com' in url:
        return True
    return False

def get_netease_url(url):
    r = parse_qs(urlparse(url).query, keep_blank_values=True)
    docid = r.get('docid', '')[0]
    return 'http://3g.163.com/touch/article/%s/full.html' % docid, docid

def ds_reply(words='你是谁'):
    r = urllib2.urlopen(WX_TULING_API_URL % words).read()
    return r

POSITIVE_EMOJI = '😆'
NEGATIVE_EMOJI = '😰'
def bs_sentiment(w=''):
    """
    [+, -]
    """
    r = BSNLP.sentiment(w)
    print r
    p = int(r[0][0] * 100)
    n = 100 - p
    return '%sx%s%sx%s ' % (POSITIVE_EMOJI, p, NEGATIVE_EMOJI, n)

def bs_calssify(w=''):
    r = BSNLP.classify([w])
    print r
    return BOSON_NEWS_CATEGORY[int(r[0])]
