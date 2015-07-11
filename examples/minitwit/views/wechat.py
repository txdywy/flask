from flask import (Blueprint, current_app, request, g, url_for, make_response,
                   render_template, redirect, jsonify)
from models.model_wechat import *
import cache as cachewx
import cron

view = Blueprint('wechat', __name__, url_prefix='/wechat')

@view.route('/share')
def share():
    key = request.args.get('k')
    c = cachewx.get('VIEW_WX_SHARE_%s' % key)
    if c:
        title, abstract, pic_url = c
        return render_template('wechat/share.html', title=title, abstract=abstract, pic_url=pic_url)
    ws = WechatShare.query.filter_by(key=key).first()
    print '==========', ws.data
    ab = ws.data['abstract']
    abstract = ab.split(' ')
    title = ws.data['title']
    pic_url = ws.data.get('lc_url')
    if not pic_url:
       pic_url = ws.data['pic_url']
       pic_url = cron.get_img(pic_url)
       if not pic_url:
           pic_url = ws.data['pic_url']
       else:
           ws.data['lc_url'] = pic_url
           flush(ws)
           cachewx.set('VIEW_WX_SHARE_%s' % key, (title, abstract, pic_url), 60 * 60)
    else:
        cachewx.set('VIEW_WX_SHARE_%s' % key, (title, abstract, pic_url), 60 * 60)
    return render_template('wechat/share.html', title=title, abstract=abstract, pic_url=pic_url)


