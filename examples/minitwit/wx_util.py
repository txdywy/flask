# -*- coding: utf-8 -*-
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
    from config import FPP_API_KEY, FPP_API_SECRET
except:
    print '----------------no FPP api key------------------'
    FPP_API_KEY, FPP_API_SECRET = '', ''
FPP_FACE_DETECT_API_URL = 'http://apius.faceplusplus.com/v2/detection/detect?api_key=%s' % FPP_API_KEY +'&api_secret=%s' % FPP_API_SECRET +'&url=%s&attribute=glass,pose,gender,age,race,smiling&mode=oneface'

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import codecs
from textrank4zh import TextRank4Keyword, TextRank4Sentence

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

FPP_GLASS_EMOJI = '👓'
def reply_pic(user_name_from, user_name_to, pic_url):
    r = fpp_face_detect(pic_url)
    print '==========',r
    head = WX_TEMPLATE_NEWS_HEAD % (user_name_from, user_name_to, str(time.time()))
    web_url = pic_url
    if not r.get('face'):
        title = '没脸见人咯?怪我咯?!'
        abstract = '看了看图,我只能说,美女都走光了...'
    else:
        a = r['face'][0]['attribute']
        title = '性别:%s' % (a['gender']['value']) + ' 年龄:%s' % (a['age']['value'])
        abstract = POSITIVE_EMOJI * 2 + '指数:%s' % (str(a['smiling']['value']) + '%') + ' ' + '种族:%s' % (a['race']['value'])
    items = WX_TEMPLATE_NEWS_ITEM % (title, abstract, pic_url, web_url)
    body = WX_TEMPLATE_NEWS_BODY % ('1', items)
    return head + body

def reply(data):
    reply_tmp = WX_TEMPLATE_TEXT
    xml_recv = ET.fromstring(data)
    user_name_to = xml_recv.find("ToUserName").text
    user_name_from = xml_recv.find("FromUserName").text
    try:pic_url = xml_recv.find("PicUrl").text
    except:pic_url = None
    if pic_url:
        result = reply_pic(user_name_from, user_name_to, pic_url)
        response = make_response(result)
        response.content_type = 'application/xml'
        return response


    content = xml_recv.find("Content").text
    result = content
    tmp = 0
    if '小虎' in content:
        result = '小虎最口耐！'
        tmp = 1
    if '猫球' in content:
        result = '猫球棒棒大！'
        tmp = 1
    reply_tmp = WX_TEMPLATE_TEXT
    if '小虎好棒' in content:
        tmp = 1
        reply_tmp = WX_TEMPLATE_IMG
        result = 'e452A-eAAjQzCgYIIcKPxqDb7Z8KoEJpR8hOsTDEbgA8o5bbFsSdWE0UxUc_A2Wf'
    if tmp:
        response = make_response(reply_tmp % (user_name_from, user_name_to, str(int(time.time())), result))
    elif '小虎是谁' in content:
        response = make_response(WX_TEMPLATE_IMG_TEXT % (user_name_from, user_name_to, str(int(time.time())),     '小虎是谁？', '是谁呀？', 'http://t.hujiang.com/images/peitu/huhu/5.jpg', 'http://alancer.cf'))
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
                sense = bs_sentiment(content)
                result = '%s' % sense + json.loads(r)['text']
                response = make_response(reply_tmp % (user_name_from, user_name_to, str(int(time.time())), result))
                response.content_type = 'application/xml'
                return response

        if unicode_is_zh(content):
            seg_list = get_key_words(content)
            result =  '\xe3\x80\x90' + '文章情感晴雨表:%s' % bs_sentiment(content) + '\xe3\x80\x91'
            result += '\xe3\x80\x90' + '文章分类:%s' % bs_calssify(content) + '\xe3\x80\x91'
            result += '\xe3\x80\x90' + '关键词' + '\xe3\x80\x91' + "\xe3\x80\x90%s\xe3\x80\x91" % "🐯".join(seg_list)
            result += '\xF0\x9F\x8C\x8D' + '\xe3\x80\x90' + '摘要' + '\xe3\x80\x91' + "\xe3\x80\x90%s\xe3\x80\x91" % get_text_digest(content)
            #print '--------',result
            response = make_response(reply_tmp % (user_name_from, user_name_to, str(int(time.time())), result))
        else:
            #print '========',repr(content)
            response = make_response(get_google_news(user_name_from, user_name_to, content))
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
    if 'http://card.weibo.com/article/h5/s#cid=' in url:
        prefix = 'http://card.weibo.com/article/aj/articleshow?cid='
        url = prefix + url[39:]
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
    p = int(r[0][0] * 10)
    n = 10 - p
    return POSITIVE_EMOJI * p + NEGATIVE_EMOJI * n

def bs_calssify(w=''):
    r = BSNLP.classify([w])
    print r
    return BOSON_NEWS_CATEGORY[int(r[0])]
