# -*- coding: utf-8 -*-
import ierror, time
from WXBizMsgCrypt import SHA1
import xml.etree.ElementTree as ET
from flask import make_response
from pygoogle import pygoogle
import re, jieba, jieba.analyse

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import codecs
from textrank4zh import TextRank4Keyword, TextRank4Sentence

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

def reply(data):
    xml_recv = ET.fromstring(data)
    user_name_to = xml_recv.find("ToUserName").text
    user_name_from = xml_recv.find("FromUserName").text
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
        if unicode_is_zh(content):
            seg_list = get_key_words(content)
            result = "🐯".join(seg_list)
            result += '\xF0\x9F\x8C\x8D' + get_text_digest(content)
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
