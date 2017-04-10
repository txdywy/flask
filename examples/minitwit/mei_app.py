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
app = Flask(__name__)

def get_mei_count():
    c = mcache.get('MEI_COUNT')
    c = c if c else mm.InstMei.query.count()
    mcache.set('MEI_COUNT', c, 60)
    return c

@app.route('/')
@app.route('/index')
def index():
    MEI_COUNT = get_mei_count()
    r = [random.randint(1, MEI_COUNT), random.randint(1, MEI_COUNT), random.randint(1, MEI_COUNT)]
    ims = mm.InstMei.query.filter(mm.InstMei.id.in_(r)).all()
    return render_template('mei.html', ims=ims, mc=MEI_COUNT)

ANT_RATE = 0.02
@app.route('/query', methods=['POST'])
def query():
    MEI_COUNT = get_mei_count()
    #ims = mm.InstMei.query.all()
    #ims = random.sample(ims, 3)
    r = [random.randint(1, MEI_COUNT), random.randint(1, MEI_COUNT)]
    ims = mm.InstMei.query.filter(mm.InstMei.id.in_(r)).all()
    ant = False if random.random() > ANT_RATE else True
    return render_template('mei_query.html', ims=ims, ant=ant)





