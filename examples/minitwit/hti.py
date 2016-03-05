import subprocess
import time
import random
from faker import Factory
import urllib
import datetime
fake = Factory.create('en_US')

template = "http GET http://events.chncpa.org/wmx2016/action/pctou.php\?id\={id}\&user_ip\={ip}\&time\={dtime} X-Requested-With:'XMLHttpRequest' Referer:'http://events.chncpa.org/wmx2016/mobile/pages/jmpx.php' User-Agent:'{ua}' Accept:'application/json, text/javascript, */*; q=0.01' Accept-Encoding:'gzip, deflate, sdch' Accept-Language:'en-US,en;q=0.8,zh-CN;q=0.6' Cache-Control:'no-cache' Host:'events.chncpa.org' Pragma:'no-cache'"


def http(id=5):
    now = datetime.datetime.now()
    dtime = str(now)[:19]
    dtime = urllib.quote_plus(dtime)
    ip = '%s.%s.%s.%s' % (random.randint(2,250),random.randint(2,250),random.randint(2,250),random.randint(2,250))
    ua = fake.user_agent()
    cmd= template.format(id=id, ip='123.3.3.3', dtime='2016-03-04+01%3A23%3A47',ua=ua)
    print cmd
    #cmd = "http GET http://events.chncpa.org/wmx2016/action/pctou.php\?id\=8\&user_ip\=123.2.2.13\&time\=2016-03-04+01%3A23%3A47 X-Requested-With:'XMLHttpRequest' Referer:'http://events.chncpa.org/wmx2016/mobile/pages/jmpx.php' User-Agent:'23sa' Accept:'application/json, text/javascript, */*; q=0.01' Accept-Encoding:'gzip, deflate, sdch' Accept-Language:'en-US,en;q=0.8,zh-CN;q=0.6' Cache-Control:'no-cache' Host:'events.chncpa.org' Pragma:'no-cache'"
    subprocess.call(cmd, shell=True)
 
