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
app = Flask(__name__)


@app.route('/')
@app.route('/index')
def index():
    return render_template('mei.html')


@app.route('/query', methods=['POST'])
def query():
    ims = mm.InstMei.query.all()
    ims = random.sample(ims, 3)
    return render_template('mei_query.html', ims=ims)





