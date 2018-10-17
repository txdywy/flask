import aiohttp
import asyncio
import uvloop
import time
import requests
from bs4 import BeautifulSoup

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

headers = {
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
    'cookie': '_ga=GA1.2.2096249051.1530681834; __tawkuuid=e::proxydocker.com::EvmzLc5o8dGEovH27iEhcbCsu79xTIpcgyAJm9k5j/r0eF0rIYhZkbYo4YYTrxeN::2; cookieconsent_status=dismiss; _gid=GA1.2.484481435.1534470821; REMEMBERME=TWFpbkJ1bmRsZVxFbnRpdHlcVXNlcjpkSGhrZVhkNToxNTM0NTU5MDg3Ojk5Y2E1NzgyZjExNmY2NWYzZWZiZTg0NWUyYzNiMmJlYjA5M2U1MWQ3N2IxM2Y5NjcwODZkZjRkN2Y2ZGZkNTc%3D; SERVERID31396=234013; PHPSESSID=120ed8919f1392088676e23138555d33; TawkConnectionTime=0',
    'alexatoolbar-alx_ns_ph': 'AlexaToolbar/alx-4.0.3',
}

data = [
  ('page', '1'),
]
#proxies = {
#    'http': 'socks5://localhost:1080',
#    'https': 'socks5://localhost:1080'
#}
r = requests.post('https://www.proxydocker.com/en/proxylist/search?port=All&type=HTTP&anonymity=All&country=United+States&city=All&state=All&need=All', data=data, headers=headers)
x = page_proxy(r)
x = [i for i in x if len(i) > 5]
for i in x:
    print(i)

print(x)

t0 = time.time()
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

async def fetch(session, url, proxy):
    headers = {'User-Agent:': 'curl/7.54.0'}
    async with session.get(url, headers=headers, proxy=proxy, timeout=10) as response:
        return await response.text()

async def coro(proxy):
    async with aiohttp.ClientSession() as session:
        try:
            html = await fetch(session, 'http://ip-api.com', proxy)
            print(html)
        except:
            print('timeout!')
        print(proxy)
        print('elapsed time:', time.time()-t0)
        print('done at', time.strftime('%X'))

        

async def main(pxys):
    coros = [coro('http://' + i) for i in pxys]
    await asyncio.gather(*coros)


pxys = ['46.63.45.88:37893',
        '185.129.212.4:32054',
        '5.141.81.80:55501',
        '188.38.105.38:8080',
        '158.255.26.221:41648',
        '103.10.81.46:47077',
        '118.175.176.137:43289',
        '67.160.143.126:36523',
        '97.72.176.78:87',
]  
pxys = x

print('started at', time.strftime('%X'))
loop = asyncio.get_event_loop()
loop.run_until_complete(main(pxys))
print('finished at', time.strftime('%X'))
