import aiohttp
import asyncio
import uvloop
import time

t0 = time.time()
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

async def fetch(session, url, proxy):
    headers = {'User-Agent:': 'curl/7.54.0'}
    async with session.get(url, headers=headers, proxy=proxy) as response:
        return await response.text()

async def coro(proxy):
    async with aiohttp.ClientSession() as session:
        html = await fetch(session, 'http://ip-api.com', proxy)
        print(html)
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

print('started at', time.strftime('%X'))
loop = asyncio.get_event_loop()
loop.run_until_complete(main(pxys))
print('finished at', time.strftime('%X'))
