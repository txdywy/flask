# -*- coding: utf-8 -*-
import requests, sys, json
from pprint import pprint

headers = {
    'Host': 'ld.m.jd.com',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept-Language': 'zh-CN',
    'User-Agent': 'jdapp;iPhone;5.4.1;10.1.1;722700139de0c2a129cf0cec4dadc72a7546f102;network/wifi;ADID/53BEAE8D-3583-4B20-A185-29FAD155EDC6;supportApplePay/1;pv/710.2;pap/JA2015_311210|122445|IOS 10.1.1;psn/369;psq/1;ads/;ref/JDMainPageViewController;jdv/0|jdzt_refer_null|t_232310336_1|jzt-zhitou|863f4250ad51db1d5b37e50abf5a2e37|1478711412975|1478711426;usc/jdzt_refer_null;adk/;umd/jzt-zhitou;ucp/t_232310336_1;utr/863f4250ad51db1d5b37e50abf5a2e37;Mozilla/5.0 (iPhone; CPU iPhone OS 10_1_1 like Mac OS X) AppleWebKit/602.2.14 (KHTML, like Gecko) Mobile/14B100 QBWebViewType/1',
    'Connection': 'keep-alive',
    'Referer': 'http://ld.m.jd.com/userBeanHomePage/getLoginUserBean.action?lng=116.332193&lat=39.998385&un_area=1_2801_2853_0&sid=b9e3644256749d0472fcbf6500a0121w',
    'X-Requested-With': 'XMLHttpRequest',
    }

def checkin():
    r = requests.get('http://ld.m.jd.com/SignAndGetBeans/getSignedCalendarRecords.action?sid=b9e3644256749d0472fcbf6500a0121w', headers=headers)
    print r.text
    
