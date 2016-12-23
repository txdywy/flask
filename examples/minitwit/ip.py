import requests
import urllib
from pprint import pprint
import random
"""
import ip;ip.test_all('US')
"""

COUNTRY = {'US': 'United State',
           'CA': 'Canada',
           'CN': 'China',
           'IN': 'India',
           'SG': 'Singapore',
           'SE': 'Sweden',
           'FR': 'France',
           'MX': 'Mexico',
           'BR': 'Brazil',
           'PL': 'Poland',
           'DK': 'Denmark',
          }

PROXY = {'http': 'socks5://127.0.0.1:1080',
         'https': 'socks5://127.0.0.1:1080',
        }

def get_pxy(c='US', p=False):
    url = 'http://www.gatherproxy.com/sockslist/country/?c=' + urllib.quote(COUNTRY[c])
    h = requests.get(url, proxies = PROXY if p else {}).text
    s = BeautifulSoup(h)
    trs = s.findAll('tr')
    trs_list = []
    for tr in trs:
        tds = tr.findAll('td')
        print '=' * 30
        for td in tds:
            print td.text
        if len(tds) == 7:
            trs_list.append(tds)
    pxy_list = [(trs[0].text,               #ts
                 trs[1].text.split("'")[1], #ip
                 trs[2].text.split("'")[1], #port
                 trs[3].text,               #country
                 trs[6].text,               #delay
                ) for trs in trs_list]
    pprint(pxy_list)
    print '=' * 30
    for p in pxy_list:
        print p[1] + ':' + p[2], '............[%s]' % p[4]
    return pxy_list


def test_pxy(pxy):
    #from fabric.api import local
    print 'curl -x socks5://%s wtfismyip.com/json' % ':'.join((pxy[1], pxy[2])), '............[%s]' % pxy[4]


def test_all(c='US'):
    x = get_pxy(c=c)
    for i in x:test_pxy(i)


def cloak(u='http://goo.gl/oI4ehT', pxy=None, c='US'):
    if not pxy:
        pxys = get_pxy(c=c)
        pxy = pxys[random.randint(0, len(pxys)-1)]
    ip, port = pxy[1], pxy[2]
    pprint(pxy)
    s = "curl -H 'pragma: no-cache' -H 'accept-encoding: gzip, deflate, sdch, br' -H 'accept-language: en-US,en;q=0.8,zh-CN;q=0.6' -H 'upgrade-insecure-requests: 1' -H 'user-agent: Mozilla/5.0 (Linux; Android 5.1.1; Nexus 6 Build/LYZ28E) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Mobile Safari/537.36' -H 'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8' -H 'cache-control: no-cache' -H 'authority: goo.gl' -H 'referer: https://m.facebook.com/' --compressed -L '{u}' -x socks5://{ip}:{port} -I".format(u=u, ip=ip, port=port)
    print s


