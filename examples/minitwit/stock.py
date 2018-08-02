# -*- coding: utf-8 -*-
import requests
import datetime
import json

US_STOCK = {'fb': 'fb',
            'msci': 'msci',
            'jd': 'jd',
            'app': 'aapl',
            'tw': 'twtr',
            'ms': 'msft',
            'g': 'goog',
            'amz': 'amzn',
            'tsla': 'tsla',
            'ali' : 'baba',
            'net': 'nflx',
            'ko': 'ko',
            'dis': 'dis',
            'data': 'data',
            'gopro': 'gpro',
            #'square': 'sq',
            #'yrd': 'yrd',
            #'vcel': 'vcel',
            'qcom': 'qcom',
            'snap': 'snap',
            }

CN_STOCK = {'海天味业': 'sh603288',
            '科大讯飞': 'sz002230',
            #'天地': 'sh600582',
            #'格力': 'sz000651',
            #'昆仑': 'sz300418',
            #'东阿': 'sz000423',
            #'海欣': 'sz002702',
            '中炬高新': 'sh600872',
            '比亚迪': 'sz002594',
            '京东方': 'sz000725',
}

BZ_STOCK ={ '东方环宇': ('sh603706',  43.47, 0.3),
            '东晶电子': ('sz002199',   8.49, 0.3),
            '双象股份': ('sz002395',  13.99, 0.3),
            '数源科技': ('sz000909',   8.05, 0.3),
            '永吉股份': ('sh603058',  12.08, 0.3),
            }

            
US_BASES = {'fb': 100,
            'msci': 63,
            'jd': 22.3,
            'app': 93.5,
            'tw': 14.3,
            'ms': 48,
            'g': 690,
            'amz': 475,
            'tsla': 165,
            'ali' : 60,
            'net': 80,
            'ko': 41.9,
            'dis': 88,
            'data': 35,
            'gopro': 9,
            #'square': 12,
            #'yrd': 13,
            #'vcel': 3.12,
            'qcom': 70,
            'snap': 25,

          }

SINA_STOCK_URL = 'http://hq.sinajs.cn/list=%s'
US_CASH = 42586
#2016.04.06 #24924
#2016.06.30 #24523
#2016.07.15 #26149
#2016.07.26 #26491
#2016.08.08 #27101
#2016.12.31 #24485
#2017.01.26 #27602
#2017.02.02 #28309
#2017.02.14 #28231
#2017.04.26 #29979
#2017.07.18 #31336
#2017.07.25 #31882
#2017.07.27 #32429
#2017.09.04 #33214
#2017.10.13 #34257
#2017.12.19 #35965
#2017.12.31 #35082
#2018.01.05 #36486
#2018.01.08 #36973
#2018.01.09 #37045
#2018.01.12 #37161
#2018.01.15 #36511
#2018.02.02 #38707
#2018.03.08 #38662
#2018.03.12 #39239
#2018.05.12 #37969
#2018.06.05 #39346
#2018.06.13 #40045
#2018.06.15 #40763
#2018.07.10 #41133
#2018.07.24 #42586

#US2016
US_PROFIT_2016 = 24485 - 23000
US_RATE_2016 = 6.5
US_RATE_2016_SUMIT = 17.8
US_BASE_2016 = 24485

#US2017
US_PROFIT_2017 = 10597
US_RATE_2017 = 43.28
US_BASE_2017 = 35082

US_BASE = US_BASE_2017

#Tue Feb 14 14:35:57 CST 2017
#Tue Jan  2 09:56:46 CST 2018

CN_CASH = 240000 + 5000 
#Thu Jan  5 11:37:48 CST 2017 +100000(MA)
#Tue Feb 14 14:35:57 CST 2017
#Tue Mar 13 09:24:10 CST 2018 +5000(me)
CN_BASE = 140000 + 100000 + 5000 #(my base)
#Tue Feb 14 14:35:57 CST 2017
#Tue Mar 13 09:24:10 CST 2018
CN_PROFIT = 5966.48 + 1314.30 + 5000 + 5000
#Fri Jul  1 09:51:23 CST 2016
#Mon Jul  4 11:35:45 CST 2016
#Tue Sep  6 09:36:49 CST 2016 +1745.93
#Fri Dec 30 08:54:29 UTC 2016 -672.27
#Tue Jan  3 15:27:29 CST 2017 +672.27 start as 140000 since 2017
#Fri Jan 13 21:54:37 CST 2017
#Mon Jan 16 14:38:12 CST 2017 +5966.48 (deposit 5966.48) 
#Tue Feb 14 14:35:57 CST 2017 +1314.30 (deposit 1314.30)
#Fri Nov 10 14:17:43 CST 2017 +5000.00 (deposit 5000.00)
#Mon Dec 18 10:27:34 CST 2017 +5000.00 (deposit 5000.00)
CN_PROFIT_2016 = 10082.06 + 672.27 #adjust by 2017.1.3
CN_RATE_2016 = 7.7
CN_PROFIT_2017 = 58961.94
CN_RATE_2017 = 10.87


def get_bz_cn_stock():
    d = BZ_STOCK.values()
    q = ','.join([i[0] for i in d])
    r = requests.get(SINA_STOCK_URL % q).text.strip()
    lines = r.split(';')[:-1]
    data = [[i[0], i[1], i[2]] for i in d]
    for idx, i in enumerate(lines):
        print i,'==='
        i = i.split('"')[1].split(',')[:]
        data[idx].extend([i[0], i[3], i[5], i[4]]) 
    return data

def get_us_stock():
    r = requests.get(SINA_STOCK_URL % ','.join(['gb_' + US_STOCK[i] for i in US_STOCK])).text.strip()
    r = r.split(';')[:-1]
    r = [i.split('"')[1].split(',')[:] for i in r]
    r = ['%s: \n#[$%s]\n#%s+%s \n#%s-%s\n*[$%s] %s\n*%s+%s \n*%s-%s\n' % (i[0], i[1], i[7], _diff(i[1], i[7]), i[6], _diff(i[6], i[1]), i[21], _diff_sym(i[21], i[1]), i[7], _diff(i[21], i[7]), i[6], _diff(i[6], i[21])) for i in r]
    b = [US_BASES[k] for k in US_BASES]
    r = zip (r, b)
    r = [a + 'Base: [%s]\n' % b for a, b in r]
    r = '\n'.join(r)
    u2016_status = '\n[2016.P:%s]' % US_PROFIT_2016 + '\n[2016.PR:%+.2f%%]' % US_RATE_2016 + '\n' 
    u2017_status = '\n[2017.P:%s]' % US_PROFIT_2017 + '\n[2017.PR:%+.2f%%]' % US_RATE_2017 + '\n'
    now_status = str(datetime.datetime.now())[:19] + '\n' + '#盘内/终\n*盘前/后'.decode('utf8') + '\n[IB:%s/%s][%+d][%+.2f%%]' % (US_CASH, US_BASE, US_CASH-US_BASE, (US_CASH-US_BASE)*100.0/US_BASE)
    rb_base = 1000 + 700 + 502.76 + 25 # $25 payout for transfer failure
    rb_cash = 2237.63 #Tue Jul 24 09:46:41 CST 2018
    #2092.59 #Tue Jul 10 15:16:10 CST 2018 
    #2131.48 #Fri Jun 15 11:11:36 CST 2018
    #2096.91 #Wed Jun 13 14:57:25 CST 2018 
    #2013.28 #Tue Jun  5 10:01:55 CST 2018 
    #1973.66 #Sat May 12 09:44:44 CST 2018
    #2244.11 #Mon Mar 12 15:45:47 CST 2018
    #2156.57 #Thu Mar  8 15:57:02 CST 2018    
    #1902.14 #Fri Feb  2 16:16:36 CST 2018
    rb_status = '\n[RB:%s/%s][%+d][%+.2f%%]' % (rb_cash, rb_base, rb_cash-rb_base, (rb_cash-rb_base)*100.0/rb_base)
    return r + u2016_status + u2017_status + '\n' + now_status + '\n' + rb_status 


def get_us_in_stock():
    r = requests.get(SINA_STOCK_URL % ','.join(['gb_' + US_STOCK[i] for i in US_STOCK])).text.strip()
    r = r.split(';')[:-1]
    r = [i.split('"')[1].split(',')[:] for i in r]
    a = r
    r = ['%s: \n#[$%s]\n#%s+%s \n#%s-%s\n*[$%s] %s\n*%s+%s \n*%s-%s\n' % (i[0], i[1], i[7], _diff(i[1], i[7]), i[6], _diff(i[6], i[1]), i[21], _diff_sym(i[21], i[1]), i[7], _diff(i[21], i[7]), i[6], _diff(i[6], i[21])) for i in r] 
    b = [US_BASES[k] for k in US_BASES]
    r = zip (r, b, a)
    r = [a + 'Base: [%s]\n' % b for a, b, c in r if _check_in(c[1], c[6], b)]
    r = '\n'.join(r)
    if not r:
        r = '没有符合要求的哟\n静候时机\n'
    return r + '\n' + str(datetime.datetime.now())[:19] + '\n' + '#盘内/终\n*盘前/后'.decode('utf8') + '\n[B:%s/%s][%+d]' % (US_CASH, US_BASE, US_CASH-US_BASE)


def _check_in(v1, v2, base):
    ratio = 0.006
    v1, v2, base = float(v1), float(v2), float(base)
    if v1>=base:
        if (v1-base)/base < ratio:
            return True
    if 0<v1<base or 0<v2<base:
        return True
    if v2>=base:
        if (v2-base)/base < ratio:
            return True
    return False


def get_one_us_stock(k):
    r = requests.get(SINA_STOCK_URL % 'gb_' + US_STOCK[k]).text.strip()
    r = r.split('"')[1].split(',')[:]
    i = r
    r = '%s: \n#[$%s]\n#%s+%s \n#%s-%s\n*[$%s] %s\n*%s+%s \n*%s-%s\n' % (i[0], i[1], i[7], _diff(i[1], i[7]),     i[6], _diff(i[6], i[1]), i[21], _diff_sym(i[21], i[1]), i[7], _diff(i[21], i[7]), i[6], _diff(i[6], i[21]))
    return r + 'Base: %s' % US_BASES[k] + '\n\n' + str(datetime.datetime.now())[:19] + '\n' + '#盘内/终\n*盘前/后'.decode('utf8')



def _diff_sym(a, b):
    x = _diff(a, b)
    if x >= 0:
        s = '+' + str(x)
    else:
        s = str(x)
    return s


def get_cn_stock():
    r = requests.get(SINA_STOCK_URL % ','.join(CN_STOCK.values())).text.strip()
    r = r.split(';')[:-1]
    r = [i.split('"')[1].split(',')[:] for i in r]
    r = ['%s: \n%s\n%s+%s \n%s-%s\n' % (i[0], i[3], i[5], _diff(i[3], i[5]), i[4], _diff(i[4], i[3])) for i in r]
    o = 442603.36 + 50000 + 50000 + 350000 + 100000 + 50000 + 5000 #2018.03.13 +5000(me) #2018.01.09 +50000 #2018.01.08 +100000#2018.01.05 +350000#2017.8.30 +50000 #2017.8 +50000
    n = 1025525.24 #1034452.60 2018.07.10 #1030107.18 2018.06.12 #1018193.28 2018.06.12 #1008775.69 2018.06.05 #1006950.68 2018.05.12 #1002885.37 2018.03.13 #999019.30 2018.03.12 #1047360.31 2018.03.08 #1058203.39 #2018.01.22  #1058142.09 2018.01.16 #1050933.40 2018.01.15 #1046270.98 2018.01.12 #997100.98 2018.01.09 #893777.89 2018.01.08 #893808.41 2018.01.08 #544123.41 2018.01.05(+350000 from m) #544055.52 2018.01.05 #584284.52 2018.01.01 (deposit 41681.16) #585002.77 2017.12.31 #590280.58 2017.12.18 (deposit 5k) #587741.41 2017.12.11 #576566.86 2017.12.11 #574833.30 2017.11.22 #570917.58 2017.11.21 #575917.58 2017.11.10 (deposit 5k) #575314.18 2017.11.10 #573176.55 2017.11.06 #570017.35 2017.11.01 #567619.14 2017.10.20 #564837.97 2017.9.29 #555891.93 2017.9.22 #550837.49 2017.9.4 #507677.78 2017.8.30 #507351.06 2017.8.22 #496287.04 2017.8.15 #464595.87 2017.8.14 #425182.54 2017.8 +50000
    p = (n-o)/o *100
    cn_status = "\n\n now:%s\n base:%s\n prof:%+.2f%%\n diff:%+.2f" % (n,o,p,n-o)
    r = '\n'.join(r)
    c2016_status = '\n[2016.P:%s]' % CN_PROFIT_2016 + '\n[PR:%+.2f%%]' % CN_RATE_2016 + '\n'
    c2017_status = '\n[2017.P:%s]' % CN_PROFIT_2017 + '\n[PR:%+.2f%%]' % CN_RATE_2017 + '\n[PR_out:17280.78]' + '\n[PR_wait:41681.16]' + '\n[PR_mom:32882.36]' + '\n'
    now_status = '\n[B:%s/%s][%+d][%+.2f%%]' % (CN_CASH, CN_BASE, (CN_CASH-CN_BASE), (CN_CASH-CN_BASE)/CN_BASE*100) + '\n[P_out:%s]' % CN_PROFIT + '\n[PR_out:%+.2f%%]' % (CN_PROFIT * 100.0/CN_BASE)
    return r + '\n' + str(datetime.datetime.now())[:19] + c2016_status + c2017_status + now_status + cn_status


def get_one_cn_stock(k):
    r = requests.get(SINA_STOCK_URL % CN_STOCK[k]).text.strip()
    i = r
    r = i.split('"')[1].split(',')[:] 
    i = r
    print i, '===='
    r = '%s: \n%s\n%s+%s \n%s-%s\n' % (i[0], i[3], i[5], _diff(i[3], i[5]), i[4], _diff(i[4], i[3]))
    return r + '\n' + str(datetime.datetime.now())[:19]


def _diff(a, b):
    return round(float(a) - float(b), 3)


def _get_crypto_price(c='BTC'):
    url = "https://min-api.cryptocompare.com/data/price?fsym=%s&tsyms=USD" % c
    r = requests.get(url)
    d = json.loads(r.text)
    return float(d['USD'])

def _get_usd2cny():
    url = "http://www.apilayer.net/api/live?access_key=4060b590cbcbcbbf02db39c1acd2efde&format=1"
    r = requests.get(url)
    d = json.loads(r.text)
    return float(d['quotes']['USDCNY'])

def _bc():
	#Thu Jan 25 09:43:05 CST 2018 add XRP
	#Fri Jan 26 10:35:19 CST 2018 +IOST +BTC +200CNY +GEMS 3725CNY +Orchid 3952CNY
        #Fri Feb  9 16:53:51 CST 2018 +ETH 1000CNY
        #Fri Feb  9 17:04:50 CST 2018 +BTC 1000CNY
        #Thu Mar  8 15:56:41 CST 2018 +ETH 1000CNY
        #Thu Mar  8 15:57:02 CST 2018 +BTC 1000CNY
        #Mon Apr  9 13:44:09 CST 2018 +ETH 1000CNY
        #Mon Apr  9 13:44:09 CST 2018 +BTC 1000CNY
        #Sat May 12 09:44:44 CST 2018 +ETH 1000CNY
        #Sat May 12 09:44:44 CST 2018 +BTC 1000CNY
        #Fri Jun  8 16:14:41 CST 2018 +ETH 1000CNY
        #Fri Jun  8 16:14:41 CST 2018 +BTC 1000CNY
        #Tue Jul 10 15:16:10 CST 2018 +ETH 1000CNY
        #Tue Jul 10 15:16:10 CST 2018 +BTC 1000CNY
    btc = [#0.0402588, #huobi 500  ... 2000+ (4000)
           0.02224942, #cola  2000
           0.01870556, #cola  1000   2018.2.9
           0.01517451, #cola  1000   2018.3.8
           0.02203554, #cola  1000   2018.4.9
           0.01770225, #cola  1000   2018.5.12
           0.05194554, #huobi 2556   2018.6.8
           0.02024291, #cola  1000   2018.6.8
           0.02273761, #cola  1000   2018.7.10
           ]
    eth = [0.124254, #cola    1000
           0.0602,   #imtoken 500
           0.0470,   #imtoken $53.66
           0.189753, #cola    1000   2018.2.9
           0.198610, #cola    1000   2018.3.8
           0.380228, #cola    1000   2018.4.9
           0.218341, #cola    1000   2018.5.12
           0.256542, #cola    1000   2018.6.8
           0.324570, #cola    1000   2018.7.10
           ]
    eos = [0, #huobi 0
           ]
    xrp = [0, #hupbi 0
           ]
    iost = [0, #huobi 0
           ]
    neo = [0, # huobi 0
           ]
    btc_usd = _get_crypto_price('BTC')
    eth_usd = _get_crypto_price('ETH')
    eos_usd = _get_crypto_price('EOS')
    xrp_usd = _get_crypto_price('XRP')
    iost_usd = _get_crypto_price('IOST')
    neo_usd = _get_crypto_price('NEO')
    usd2cny = _get_usd2cny()
    base_cny = 500.0 + 2000.0 + 1000.0 + 500.0 + 2000.0 + 53.66 * usd2cny + \
               2000.0 + \
               2000.0 + \
               2000.0 + \
               2000.0 + \
               2000.0 + \
               2000.0
               #btc eth each 1k 2018.2.9    
               #btc eth each 1k 2018.3.8
               #btc eth each 1k 2018.4.9
               #btc eth each 1k 2018.5.12
               #btc eth each 1k 2018.6.8
               #btc eth each 1k 2018.7.10
    base_usd = base_cny / usd2cny
    pv_usd = sum(btc) * btc_usd + sum(eth) * eth_usd + sum(eos) * eos_usd + sum(xrp) * xrp_usd + sum(iost) * iost_usd 
    pv_cny = pv_usd * usd2cny
    return pv_usd, base_usd, pv_cny, base_cny, btc_usd*usd2cny, eth_usd*usd2cny, eos_usd*usd2cny, xrp_usd*usd2cny, iost_usd*usd2cny, neo_usd*usd2cny, sum(btc), sum(eth), sum(eos), sum(xrp), sum(iost), sum(neo)


def blockchain():
    pv_usd, base_usd, pv_cny, base_cny, btc_price_cny, eth_price_cny, eos_price_cny, xrp_price_cny, iost_price_cny, neo_price_cny, btc_v, eth_v, eos_v, xrp_v, iost_v, neo_v = _bc()
    result = '\n[USD:%.2f/%.2f]' % (pv_usd, base_usd) + \
             '\n[CNY:%.2f/%.2f]' % (pv_cny, base_cny) + \
             '\n[BTC:%.2f(%.2f)]' % (btc_price_cny, btc_price_cny*btc_v) + \
             '\n[ETH:%.2f(%.2f)]' % (eth_price_cny, eth_price_cny*eth_v) + \
             '\n[EOS:%.2f(%.2f)]' % (eos_price_cny, eos_price_cny*eos_v) + \
             '\n[XRP:%.2f(%.2f)]' % (xrp_price_cny, xrp_price_cny*xrp_v) + \
             '\n[IOST:%.2f(%.2f)]' % (iost_price_cny, iost_price_cny*iost_v) + \
             '\n[NEO:%.2f(%.2f)]' % (neo_price_cny, neo_price_cny*neo_v) + \
             '\n[btc:%.8f]' % btc_v + \
             '\n[eth:%.8f]' % eth_v + \
             '\n[eos:%.8f]' % eos_v + \
             '\n[xrp:%.8f]' % xrp_v + \
             '\n[iost:%.8f]' % iost_v + \
             '\n[neo:%.8f]' % neo_v + \
             '\n[Total:%dCNY]' % (base_cny + 3725 + 3952) + \
             '\n[GEMS:0.5eth 3725CNY]' + \
             '\n[Orchid:0.5eth 3952CNY]'
    return result    




