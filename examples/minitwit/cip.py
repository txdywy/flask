import aiohttp
import asyncio
import time
import requests
from bs4 import BeautifulSoup
import logging
import socket
logging.basicConfig(level=logging.DEBUG)

try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except:
    print('No uvloop installed, use default asyncio loop')


def page_proxy(r):
    #give me a response r and i give you all proxies entry data
    page_proxy_count = 0
    html = r.content
    soup = BeautifulSoup(html, 'lxml')
    trs = soup.find_all('tr')
    trs = trs[1:]
    tds_list = []
    for tr in trs:
        tds = tr.find_all('td')
        td = tds[0]
        tds_list.append(td.text.strip())
    return tds_list

PD_HEADERS = {
    'authority': 'www.proxydocker.com',
    'pragma': 'no-cache',
    'cache-control': 'no-cache',
    'origin': 'https://www.proxydocker.com',
    'upgrade-insecure-requests': '1',
    'content-type': 'application/x-www-form-urlencoded',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'referer': 'https://www.proxydocker.com/en/socks5-list/',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,zh-TW;q=0.6',
    'cookie': '_ga=GA1.2.587845913.1535014830; __tawkuuid=e::proxydocker.com::JWZ39h6IUYPaAAYuUYbjpiqGWfxMnQ5GPYDOJSuv1bjQTQrUaXpeajfwuZFRBueD::2; _gid=GA1.2.538432557.1539570325; cookieconsent_status=dismiss; REMEMBERME=TWFpbkJ1bmRsZVxFbnRpdHlcVXNlcjpkSGhrZVhkNToxNTM5ODM5OTgyOmQwN2Q3YmNlZDZjNGMxZjgxNmZhMGJhZDZjNDllNTY4OTZkNjg0ZTg4MjIzYWU0N2MxZjAyOGFjMzcxYTY1Mjg%3D; SERVERID31396=234013; PHPSESSID=6908453197842b2ef841260a1a9e5af9; _gat=1; TawkConnectionTime=0',
    'alexatoolbar-alx_ns_ph': 'AlexaToolbar/alx-4.0.3',
}


DP_URL = 'https://www.proxydocker.com/en/proxylist/search?port=All&type=HTTP&anonymity=All&country=United+States&city=All&state=All&need=All'
IPAPI_URL = 'http://ip-api.com'
HTTPS_URL = 'https://www.proxydocker.com/'

def fetch_proxies(page='1'):
    data = [
      ('page', page),
    ]
    #proxies = {
    #    'http': 'socks5://localhost:1080',
    #    'https': 'socks5://localhost:1080'
    #}
    print('started dp fetch', time.strftime('%X'))
    r = requests.post(DP_URL, data=data, headers=PD_HEADERS)
    print('done dp fetch', time.strftime('%X'))
    proxies = page_proxy(r)
    proxies = [i for i in proxies if len(i) > 5]
    for i in proxies:
        print(i)

    print(proxies)
    return proxies


def fetch_proxies_all(pages=1):
    proxies = []
    for i in range(1, pages+1):
        try:
            proxy = fetch_proxies(str(i))
        except:
            print('dp connection failed, you may need update your cookies to fetch more than 1 pages')
        proxies += proxy
    return proxies



def fetch_proxies_all_aio(pages=1):
    t0 = time.time()
    print('started at', time.strftime('%X'))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main_pd(pages=['1','2'], t0=t0))
    print('finished at', time.strftime('%X'))



    

async def post_pd(session, url, proxy, data):
    headers = PD_HEADERS
    async with session.post(url, headers=headers, timeout=90, data=data, proxy=proxy) as response:
        return await response.text()


async def coro_pd(page, proxy, t0=None):
    data = [
      ('page', page),
    ] 
    if not t0:
        t0 = time.time()
    conn = aiohttp.TCPConnector(
        family=socket.AF_INET,
        verify_ssl=False,
    )
    async with aiohttp.ClientSession(connector=conn) as session:
        try:
            html = await post_pd(session, DP_URL, proxy, data)
            print(html)
        except Exception as e:
            raise e
            print('timeout!')
            html = ''
        print(proxy)
        print('elapsed time:', time.time()-t0)
        print('done at', time.strftime('%X'))
        return html


async def main_pd(pages=None, pxys=None, t0=None):
    if not pages:
        pages = ['1']
    coros = [coro_pd(page, pxys, t0) for page in pages]
    x = await asyncio.gather(*coros)
    print(x)



async def fetch(session, url, proxy):
    headers = {'User-Agent:': 'curl/7.54.0'}
    async with session.get(url, headers=headers, proxy=proxy, timeout=20) as response:
        return await response.text()


async def coro(proxy, t0=None):
    if not t0:
        t0 = time.time()
    async with aiohttp.ClientSession() as session:
        try:
            html = await fetch(session, IPAPI_URL, proxy)
            print(html)
        except:
            print('timeout!')
        print(proxy)
        print('elapsed time:', time.time()-t0)
        print('done at', time.strftime('%X'))

        

async def main(pxys, t0=None):
    coros = [coro('http://' + i, t0) for i in pxys]
    await asyncio.gather(*coros)


TEST_PROXIES = ['46.63.45.88:37893',
                '185.129.212.4:32054',
                '5.141.81.80:55501',
                '188.38.105.38:8080',
                '158.255.26.221:41648',
                '103.10.81.46:47077',
                '118.175.176.137:43289',
                '67.160.143.126:36523',
                '97.72.176.78:87',
]  


def fetch_and_poll(pages=1, test=False):
    proxies = TEST_PROXIES if test else fetch_proxies_all(pages)
    print(proxies)
    t0 = time.time()
    print('started at', time.strftime('%X'))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(proxies, t0))
    print('finished at', time.strftime('%X'))


def run(pages=1):
    fetch_and_poll(pages=pages)
