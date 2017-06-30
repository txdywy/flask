# -*- coding: utf-8 -*-
"""
    Alancer
    ~~~~~~~~

    An application written with Flask and sqlite3.

    :copyright: (c) 2015 by Yi Wei.
    :license: BSD, see LICENSE for more details.
"""
#from gevent import monkey
#monkey.patch_all()
import time, urllib2
from datetime import datetime
from flask import Flask, request, session, url_for, redirect, \
     render_template, abort, g, flash, _app_ctx_stack, make_response
import flask
import models.model_mei as mm
import random
import koji as mcache
import json
app = Flask(__name__)
app.debug = True

GP_INST_OWNER = [
    'djxin_tw',
    'lucycecile',
    '44lucifer77',
    'alicebambam',
    'jenna_chew',
    'actressclara',
    #'hwangbarbie',
    'icicbaby',
    'chiababy116',
    'cyndi811213',
    'crysta1lee',
    'mikibaby_w',
    'mayjam101',
    'hinzajoa',
    'emrata',
    'cindyprado',
    'leananabartlett',
    'melwitharosee',
    'sg.my.babes',
    'peiyu0515',
    'laine_laineng',
    'vickycc061',
    'cherry_quahst',
    'chiaraferragni',
    'josephineskriver',
    'jieun_han',
    'lovelyjoohee',
    'instababes.asian',
]
GP_ID_LIST = mm.InstMei.query.filter(mm.InstMei.inst_owner.in_(GP_INST_OWNER)).all()
GP_ID_LIST = [x.id for x in GP_ID_LIST]

def get_mei_count():
    c = mcache.get('MEI_COUNT')
    c = c if c else mm.InstMei.query.count()
    mcache.set('MEI_COUNT', c, 60)
    return c


def get_mei_more_count():
    c = mcache.get('MEI_MORE_COUNT')
    c = c if c else mm.InstMeiMore.query.count()
    mcache.set('MEI_MORE_COUNT', c, 60)
    return c


@app.route('/')
@app.route('/index')
def index():
    MEI_COUNT = get_mei_count()
    r = [random.randint(1, MEI_COUNT), random.randint(1, MEI_COUNT), random.randint(1, MEI_COUNT)]
    #r = random.sample(GP_ID_LIST, 3)
    ims = mm.InstMei.query.filter(mm.InstMei.id.in_(r)).all()
    return render_template('mei.html', ims=ims, mc=MEI_COUNT, imc=get_mei_count())



ANT_RATE = 0.02
@app.route('/query', methods=['POST'])
def query():
    MEI_COUNT = get_mei_count()
    #ims = mm.InstMei.query.all()
    #ims = random.sample(ims, 3)
    r = [random.randint(1, MEI_COUNT), random.randint(1, MEI_COUNT)]
    #r = random.sample(GP_ID_LIST, 2)
    ims = mm.InstMei.query.filter(mm.InstMei.id.in_(r)).all()
    ant = False if random.random() > ANT_RATE else True
    return render_template('mei_query.html', ims=ims, ant=ant)


@app.route('/api')
def api():
    return "https://ig-s-b-a.akamaihd.net/hphotos-ak-xta1/t51.2885-15/e35/17265902_267101913747541_3627374961242406912_n.jpg"


TEMP_LIST = ['2MKACyCBAs',
 'of5-BaoySM',
 'BHuwr9yD7mr',
 '_wC8z9wEfM',
 '_iYu_FQEfq',
 '7W5-cmQESx',
 'BHZ1DsPj0Ob',
 '9tWRx3QEQG',
 'BHkCmK1D5W5',
 'BL80SfFAyHV',
 '_gDZOHoyQc',
 'BBE7X25iIjA',
 'hgN0BXoyZp',
 '1GXqeNoyZm',
 'xJw85-IyQe',
 'BSTqxRgA6vZ',
 'BQakf6Lgvct',
 '_b8FJys95s',
 'w5uvpNIyf2',
 '9LKTmVIyd_',
 'BHdKZ4WhmNj',
 'BBmtqgOB08p',
 'BDC6l5AIyX4',
 '6n2pfuiBPr',
 'BOOiEjNjgaJ',
 'BMoRqeejRwU',
 'rrjf4WoyQB',
 '-_vzuuqQ3z',
 '5Cr4ikoyTx',
 'd4NXT3oyRC',
 'z6sQy7oyat',
 'gGvHQzIyW5',
 'sHyu80oyfj',
 'BOqiCf2jaGl',
 '_GWd9CoyYR',
 '0MFXryIyc9',
 'fw6I15CIoM',
 'w4NMPKoydC',
 'eM8YeHIyYl',
 'BJAD7HhDqnQ',
 'BSI6guxl9CI',
 'BC8Ky2RIycU',
 'BHkzzPyBhAD',
 'lmWNNXB01H',
 'BDh_vuqqQ6o',
 'k4jxZhIyYx',
 'BDPeEVcKQ-r',
 'wL8ZbiQETl',
 'pgl1OvoySD',
 'ZSTY2koyfI',
 '8KYn4zIyYk',
 '5RQtE4IyXu',
 '_x2NuRiIoA',
 'BQe9i4rjeBM',
 ]


def get_temp_ims():
    ims = mm.InstMei.query.filter(mm.InstMei.inst_code.in_(TEMP_LIST)).all()
    return ims
    

@app.route('/recent0')
def recent():
    MEI_COUNT = get_mei_count()
    total = 1000
    s = [random.randint(1, MEI_COUNT) for i in xrange(total)]

    #s = random.sample(GP_ID_LIST, 1000)
    ims = mm.InstMei.query.filter(mm.InstMei.id.in_(s)).all()
    #ims = get_temp_ims()
    #ims = ims * 10
    total = len(ims)
    ims = [i.to_dict() for i in ims]
    random.shuffle(ims)
    r = {}
    r['photos'] = {}
    r['photos']['page'] = 1
    r['photos']['pages'] = 4
    r['photos']['perpage'] = 300
    r['photos']['total'] = total
    r['photos']['photo'] = ims
    r['stat'] = 'ok'
    x = json.dumps(r)
    return 'jsonFlickrApi(%s)' % x 

@app.route('/recent')
def recent1():
    MEI_COUNT = get_mei_more_count()
    total = 1000
    s = [random.randint(1, MEI_COUNT) for i in xrange(total)]

    #s = random.sample(GP_ID_LIST, 1000)
    ims = mm.InstMeiMore.query.filter(mm.InstMeiMore.id.in_(s)).all()
    #ims = get_temp_ims()
    #ims = ims * 10
    total = len(ims)
    ims = [i.to_dict() for i in ims]
    random.shuffle(ims)
    r = {}
    r['photos'] = {}
    r['photos']['page'] = 1
    r['photos']['pages'] = 4
    r['photos']['perpage'] = 300
    r['photos']['total'] = total
    r['photos']['photo'] = ims
    r['stat'] = 'ok'
    x = json.dumps(r)
    return 'jsonFlickrApi(%s)' % x 

@app.route('/recent1')
def recent_tmp():
    MEI_COUNT = get_mei_count()
    total = 1000
    s = [random.randint(1, MEI_COUNT) for i in xrange(total)]

    #s = random.sample(GP_ID_LIST, 1000)
    #ims = mm.InstMei.query.filter(mm.InstMei.id.in_(s)).all()
    ims = get_temp_ims()
    ims = ims * 10
    total = len(ims)
    ims = [i.to_dict() for i in ims]
    random.shuffle(ims)
    r = {}
    r['photos'] = {}
    r['photos']['page'] = 1
    r['photos']['pages'] = 4
    r['photos']['perpage'] = 300
    r['photos']['total'] = total
    r['photos']['photo'] = ims
    r['stat'] = 'ok'
    x = json.dumps(r)
    return 'jsonFlickrApi(%s)' % x

@app.route('/ios')
def ios():
    pre = "https://ig-s-b-a.akamaihd.net/hphotos-ak-xta1/t51.2885-15/e35/"
    flag = 1#random.randint(0, 1)
    MEI_COUNT = get_mei_more_count() if flag else get_mei_count()
    total = 5
    s = [random.randint(1, MEI_COUNT) for i in xrange(total)]
    ims = mm.InstMeiMore.query.filter(mm.InstMeiMore.id.in_(s)).all() if flag else mm.InstMei.query.filter(mm.InstMei.id.in_(s)).all()
    r = [pre+im.to_dict()['secret'] for im in ims]
    d = {'data': r}
    print d
    return json.dumps(d) 

    total = 1000
    s = [random.randint(1, MEI_COUNT) for i in xrange(total)]

    #s = random.sample(GP_ID_LIST, 1000)
    ims = mm.InstMei.query.filter(mm.InstMei.id.in_(s)).all()
    #ims = get_temp_ims()
    #ims = ims * 10
    total = len(ims)
    ims = [i.to_dict() for i in ims]
    random.shuffle(ims)
    r = {}
    r['photos'] = {}
    r['photos']['page'] = 1
    r['photos']['pages'] = 4
    r['photos']['perpage'] = 300
    r['photos']['total'] = total
    r['photos']['photo'] = ims
    r['stat'] = 'ok'
    x = json.dumps(r)
    return x


@app.route('/sexy_avi')
def avi():
    return redirect('http://ac-9dv47dhd.clouddn.com/4b336ef074f6d9b5a834.apk', code=302)


@app.route('/more')
def more():
    return str(mm.InstMeiMore.query.count()) + '\n'


@app.route('/pin')
def pin():
    id = request.args.get('id')
    d = mm.Dance.query.get(id)
    if not d:
        return '0'
    d.like += 1
    mm.flush(d)
    return '1'


DANCE_QUEEN_LIST = [
    'http://ac-9dv47dhd.clouddn.com/1bf2e4f9ddcb02beb9bb.JPG',
    'http://ac-9dv47dhd.clouddn.com/56c4dbc4888d98079af2.JPG',
    'http://ac-9dv47dhd.clouddn.com/0d9c1a6ab5f9767a3017.JPG',
    'http://ac-9dv47dhd.clouddn.com/efd4f611e9e648416b94.JPG',
    'http://ac-9dv47dhd.clouddn.com/3ec458b11674adb7dc7d.JPG',
    'http://ac-9dv47dhd.clouddn.com/63f28c98914f9218f26a.JPG',
    'http://ac-9dv47dhd.clouddn.com/219f5d1a182fd71691dc.JPG',
    'http://ac-9dv47dhd.clouddn.com/1bf2e4f9ddcb02beb9bb.JPG',
    'http://ac-9dv47dhd.clouddn.com/b1e152a3018c6b2399e2.JPG',
    'http://ac-9dv47dhd.clouddn.com/08a7c183216b8cd0c2ee.JPG',
    'http://ac-9dv47dhd.clouddn.com/62f257ecdd3fc6d12985.JPG',
    'http://ac-9dv47dhd.clouddn.com/e4148aee8d98a1058f70.JPG',
    'http://ac-9dv47dhd.clouddn.com/0f73edd01dc37caa76ef.JPG',
    'http://ac-9dv47dhd.clouddn.com/61ba1d921a1a8dc17de9.JPG',
    'http://ac-9dv47dhd.clouddn.com/e21eded8ab2391dff4a1.JPG',
    'http://ac-9dv47dhd.clouddn.com/147bff7ac8e939a10946.JPG',
    'http://ac-9dv47dhd.clouddn.com/93cfa14d327c73a58fa2.JPG',
    'http://ac-9dv47dhd.clouddn.com/1f2b5af29c0c47f39398.JPG',
    'http://ac-9dv47dhd.clouddn.com/8cd056c1cc5dd120a644.JPG',
    'http://ac-9dv47dhd.clouddn.com/f5b9e39e74aeff15354f.JPG',
    'http://ac-9dv47dhd.clouddn.com/de53e1886534b2dee676.JPG',
    'http://ac-9dv47dhd.clouddn.com/f04766aa020fabe846d1.JPG',
    'http://ac-9dv47dhd.clouddn.com/001102eed9e80f63798c.JPG',
    'http://b177.photo.store.qq.com/psb?/V11wKDiG23Nj7m/Y*lDiaFiUpIcff8tNPTedQ.xU*.LatKOro*dLO9ERJk!/b/dLEAAAAAAAAA&ek=1&kp=1&pt=0&bo=OAQ4BAAAAAAFFzQ!&tm=1494234000#sce=14-1-1&rf=v1_iph_sq_6.5.0_0_hdbm_t-4-2',
    'http://b166.photo.store.qq.com/psb?/V11wKDiG23Nj7m/RxeOsn4L5JeBvf*7q4hQbkBoh2XJ.Wp.A0xziGBsej8!/b/dKYAAAAAAAAA&ek=1&kp=1&pt=0&bo=OAQ4BAAAAAAFFzQ!&tm=1494234000#sce=14-1-1&rf=v1_iph_sq_6.5.0_0_hdbm_t-4-2',
    'http://b246.photo.store.qq.com/psb?/V11wKDiG23Nj7m/.dm60bfkag10eQLnH6eSxRHmpwdISKM9aiFESEvfYCo!/b/dPYAAAAAAAAA&ek=1&kp=1&pt=0&bo=*gTAAwAAAAAFJz0!&tm=1494234000#sce=14-1-1&rf=v1_iph_sq_6.5.0_0_hdbm_t-4-2',
    'http://b252.photo.store.qq.com/psb?/V11wKDiG23Nj7m/ZgcQAR2qbEcx3t0OFyqWHznkug4jEffK5HAYi9me1oU!/b/dPwAAAAAAAAA&ek=1&kp=1&pt=0&bo=*gTAAwAAAAAFFw0!&tm=1494234000#sce=14-1-1&rf=v1_iph_sq_6.5.0_0_hdbm_t-4-2',
    'http://b177.photo.store.qq.com/psb?/V11wKDiG23Nj7m/UArX5XEZsV4mULC1ETrVg6qXUBgC*zbhG2K5CkWlqfU!/b/dLEAAAAAAAAA&ek=1&kp=1&pt=0&bo=OAQ4BAAAAAAFFzQ!&tm=1494234000#sce=14-1-1&rf=v1_iph_sq_6.5.0_0_hdbm_t-4-2',
    'http://b173.photo.store.qq.com/psb?/V11wKDiG23Nj7m/.NOBdDZqinw3waZAnRRjccNUN0xKFCpfbyVBJLHAHKo!/b/dK0AAAAAAAAA&ek=1&kp=1&pt=0&bo=OAQ4BAAAAAAFFzQ!&tm=1494234000#sce=14-1-1&rf=v1_iph_sq_6.5.0_0_hdbm_t-4-2',
    'http://b174.photo.store.qq.com/psb?/V11wKDiG23Nj7m/XpG4yvbnWVlifQah*W8YgIXT.DCjjPGQTYQ5ri*jDSE!/b/dK4AAAAAAAAA&ek=1&kp=1&pt=0&bo=OAQ4BAAAAAAFFzQ!&tm=1494234000#sce=14-1-1&rf=v1_iph_sq_6.5.0_0_hdbm_t-4-2',
    'http://b177.photo.store.qq.com/psb?/V11wKDiG23Nj7m/XQqclFbkc3PHVRaUU2TfFX2HMhoW6wYnLT7T85YGAHE!/b/dLEAAAAAAAAA&ek=1&kp=1&pt=0&bo=OAQ4BAAAAAAFFzQ!&tm=1494234000#sce=14-1-1&rf=v1_iph_sq_6.5.0_0_hdbm_t-4-2',
    'http://b177.photo.store.qq.com/psb?/V11wKDiG23Nj7m/FA5*dd9HDDhEdbgXRDhtb1ZoCGmuszhhQC2pz5wkk7Q!/b/dLEAAAAAAAAA&ek=1&kp=1&pt=0&bo=OAQ4BAAAAAAFFzQ!&tm=1494234000#sce=14-1-1&rf=v1_iph_sq_6.5.0_0_hdbm_t-4-2',
    'http://b250.photo.store.qq.com/psb?/V11wKDiG23Nj7m/LhlKGRspKcglrx1Wh2ym4rTuc3AzpxCc8Ikb3o9XVsg!/b/dPoAAAAAAAAA&ek=1&kp=1&pt=0&bo=OAQ4BAAAAAAFFzQ!&tm=1494234000#sce=14-1-1&rf=v1_iph_sq_6.5.0_0_hdbm_t-4-2',
    'http://b246.photo.store.qq.com/psb?/V11wKDiG23Nj7m/FxoErT5*nDCiUwwlrXZEgl2TpIVdKKSJiohfNOIvucI!/b/dPYAAAAAAAAA&ek=1&kp=1&pt=0&bo=OAQ4BAAAAAAFFzQ!&tm=1494234000#sce=14-1-1&rf=v1_iph_sq_6.5.0_0_hdbm_t-4-2',
    'http://b165.photo.store.qq.com/psb?/V11wKDiG23Nj7m/buTRP0cl*TSO5gMqSPNrV0Ll*emRNRo2pMr0id2Tbqw!/b/dKUAAAAAAAAA&ek=1&kp=1&pt=0&bo=OAQ4BAAAAAAFFzQ!&tm=1494234000#sce=14-1-1&rf=v1_iph_sq_6.5.0_0_hdbm_t-4-2',
    'http://b172.photo.store.qq.com/psb?/V11wKDiG23Nj7m/7f.H9m3klolzK0.1aMnpZ72dq0m1DndNaf6tIITgmzQ!/b/dKwAAAAAAAAA&ek=1&kp=1&pt=0&bo=OAQ4BAAAAAAFFzQ!&tm=1494234000#sce=14-1-1&rf=v1_iph_sq_6.5.0_0_hdbm_t-4-2',
    'http://b258.photo.store.qq.com/psb?/V11wKDiG23Nj7m/MOsKpO5*9WesBAHI6Lyjw7vW6KHD7fYTPJTKiKIjPdQ!/b/dAIBAAAAAAAA&ek=1&kp=1&pt=0&bo=OAQ4BAAAAAAFFzQ!&tm=1494234000#sce=14-1-1&rf=v1_iph_sq_6.5.0_0_hdbm_t-4-2',
    'http://b166.photo.store.qq.com/psb?/V11wKDiG23Nj7m/ovDsXjNhPGMTFYkgmAZDj*OwunUuTS8FaQ5el3NukIw!/b/dKYAAAAAAAAA&ek=1&kp=1&pt=0&bo=OAQ4BAAAAAAFFzQ!&tm=1494234000#sce=14-1-1&rf=v1_iph_sq_6.5.0_0_hdbm_t-4-2',
    'http://b173.photo.store.qq.com/psb?/V11wKDiG23Nj7m/TXl5Aq8QBwLXmCyOzwv1jVbW.zyaezrgUK743C*H.BY!/b/dK0AAAAAAAAA&ek=1&kp=1&pt=0&bo=OAQ4BAAAAAAFFzQ!&tm=1494234000#sce=14-1-1&rf=v1_iph_sq_6.5.0_0_hdbm_t-4-2',
    'http://b178.photo.store.qq.com/psb?/V11wKDiG23Nj7m/NfqqeLCEWHO2ZycCnIeWjDILgMGyd0z0QmHTcCls.zg!/b/dLIAAAAAAAAA&ek=1&kp=1&pt=0&bo=OAQ4BAAAAAAFFzQ!&tm=1494234000#sce=14-1-1&rf=v1_iph_sq_6.5.0_0_hdbm_t-4-2',
    'http://b248.photo.store.qq.com/psb?/V11wKDiG23Nj7m/jbPXJdHrd3bS9wcHFOCDNVvhciSg.OTPqEEPEhapGxo!/b/dPgAAAAAAAAA&ek=1&kp=1&pt=0&bo=OAQ4BAAAAAAFFzQ!&tm=1494234000#sce=14-1-1&rf=v1_iph_sq_6.5.0_0_hdbm_t-4-2',
    'http://b178.photo.store.qq.com/psb?/V11wKDiG23Nj7m/fxMI.77w5m2jI*UL2mbUQQgB7PsrO912Xul8*jFjpDQ!/b/dLIAAAAAAAAA&ek=1&kp=1&pt=0&bo=OAQ4BAAAAAAFFzQ!&tm=1494234000#sce=14-1-1&rf=v1_iph_sq_6.5.0_0_hdbm_t-4-2',
]

@app.route('/dance')
def dance():
    ims = []
    ds = mm.Dance.query.all()
    ds = sorted(ds, key=lambda x:x.like, reverse=True)
    for i in ds:#DANCE_QUEEN_LIST:
        x = {}
        x["isfamily"] = 0
        x["title"] = "京城舞王"
        x["farm"] = 4
        x["ispublic"] = 1
        x["server"] = ""
        x["isfriend"] = 0
        x["secret"] = i.image_url
        x["owner"] = ""
        x["id"] = ""
        ims.append(x)
    total = len(ims)
    #random.shuffle(ims)
    r = {}
    r['photos'] = {}
    r['photos']['page'] = 1
    r['photos']['pages'] = 4
    r['photos']['perpage'] = 300
    r['photos']['total'] = total
    r['photos']['photo'] = ims
    r['stat'] = 'ok'
    x = json.dumps(r)
    return 'jsonFlickrApi(%s)' % x


@app.route('/idance')
def idance():
    ims = []
    ds = mm.Dance.query.all()
    ds = sorted(ds, key=lambda x:x.like, reverse=True)
    for i in ds:
        x = {}
        x['category'] = 'ZaHui' #i.category
        x['image_url'] = i.image_url
        x['thumb_url'] = i.image_url
        x['title'] = i.title
        x['id'] = str(i.id)
        x['like'] = str(i.like)
        ims.append(x)
    r = {}
    r['category'] = 'All'
    r['page'] = 1
    r['results'] = ims
    rt = json.dumps(r)
    return rt
