import gevent
from gevent import monkey
monkey.patch_all()

from leancloud import File
from StringIO import StringIO
try:
    from config import LC_APP_ID, LC_APP_KEY
    import leancloud
    leancloud.init(LC_APP_ID, LC_APP_KEY)
except:
    print '------------import leancloud error------------'
import urllib2

from models.model_wechat import *
import cache as cachecr
CRON_TASK_CONVERT_LC = 'cron.task.convert.lc'

def get_img(url):
    try:
        c = urllib2.urlopen(url).read()
        f = StringIO(c)
        lc_file = File('wx', f)
        lc_file.save()
        r = lc_file.url
    except Exception, e:
        print '---------', e
        r = None 
    return r

def task_lc():
    t = cachecr.setnx(CRON_TASK_CONVERT_LC, 1)
    if t:
        try:
            print '-------------start----convert-----'
            convert()
            print '-------------done-----convert-----'
        except Exception, e:
            print '------------fail-------convert----'
        finally:
            cachecr.delete(CRON_TASK_CONVERT_LC)
    else:
        print '----------duplicate--------'
        return

def gconvert():
    ws = WechatShare.query.filter_by(lc=0).all()
    us = [w.data.get('pic_url') for w in ws]
    jobs = [gevent.spawn(get_img, url) for url in us]
    gevent.wait(jobs)
    nus = [j.value for j in jobs]
    for i, url in enumerate(nus):
        w = ws[i]
        if url:
            w.data['lc_url'] = url
            w.lc = 1
            flush(w)

def convert():
    ws = WechatShare.query.filter_by(lc=0).all()
    us = [w.data.get('pic_url') for w in ws] 
    nus = [get_img(url) for url in us] 
    for i, url in enumerate(nus):
        w = ws[i]
        if url:
            w.data['lc_url'] = url 
            w.lc = 1 
            flush(w)


