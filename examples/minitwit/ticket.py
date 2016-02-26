import requests as r
import urllib
import time
import random
def ti(n=10):
    u = 'http://events.chncpa.org/wmx2016/action/pctou.php?id=5&user_ip=%s.%s.%s.%s&time=2016-02-26+'
    headers = {'Referer': 'http://events.chncpa.org/wmx2016/mobile/pages/jmpx.php?from=singlemessage&amp;isappinstalled=0', 'X-Requested-With': 'XMLHttpRequest', 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.%s Safari/537.36'%random.randint(2,250)} 
    for i in range(n):
        ur= u % (random.randint(2,250),random.randint(2,250),random.randint(2,250),random.randint(2,250))+urllib.quote('%s:%s:%s'%(random.randint(2,58),random.randint(2,58),random.randint(2,58),))
        x=r.get(ur,headers=headers)
        time.sleep(random.randint(1,60))
        print x.text
