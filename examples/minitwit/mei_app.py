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

APPNEXT_INST = """
<script type="text/javascript">
 var Appnext = {
       android_id: 'ae43833b-91cd-4a3d-9a43-156a1a369eba',
       ios_id: 'e086edd6-92b0-48f5-97f0-174a45a33e94',
       cat: '',
       pbk: '',
       b_title: '',
       b_color: '',
       auto_play: '',
       timeout: '',
       times_to_show: '',
       times_to_show_reset: '',
       creative:'managed', 
       subid: '',
       ad_server:'false'
     };
        (function(){
        var _s=document.createElement('script');
        _s.type='text/javascript';
        _s.async=true;
        _s.src='https://appnext.hs.llnwd.net/tools/tags/interstitial/manage_script.js';
        (document.body)?document.body.appendChild(_s):document.head.appendChild(_s);
        })();
</script>

"""
MEI_COUNT = mm.InstMei.query.count()
@app.route('/')
@app.route('/index')
def index():
    r = [random.randint(1, MEI_COUNT), random.randint(1, MEI_COUNT), random.randint(1, MEI_COUNT)]
    ims = mm.InstMei.query.filter(mm.InstMei.id.in_(r)).all()
    return render_template('mei.html', ims=ims)


@app.route('/query', methods=['POST'])
def query():
    #ims = mm.InstMei.query.all()
    #ims = random.sample(ims, 3)
    r = [random.randint(1, MEI_COUNT), random.randint(1, MEI_COUNT), random.randint(1, MEI_COUNT)]
    ims = mm.InstMei.query.filter(mm.InstMei.id.in_(r)).all()
    if random.random() > 0.2:
        ant = APPNEXT_INST
    else:
        ant = ''
    return render_template('mei_query.html', ims=ims, app_next_tag=ant)





