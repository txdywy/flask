from leancloud import File
from StringIO import StringIO
try:
    from config import LC_APP_ID, LC_APP_KEY
    import leancloud
    leancloud.init(LC_APP_ID, LC_APP_KEY)
except:
    print '------------import leancloud error------------'
import urllib2

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

u='http://mmbiz.qpic.cn/mmbiz/UC8jTLIYtf88ib2WfXbh0UzynYicfcPnoteND7XibIoVSdHnEfPVzuYiahCuAoBnYoTrMiccztySy3mcscunjmehZwQ/0'
print get_img(u)
