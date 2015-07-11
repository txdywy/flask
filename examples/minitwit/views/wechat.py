from flask import (Blueprint, current_app, request, g, url_for, make_response,
                   render_template, redirect, jsonify)
from models.model_wechat import *
import cron

view = Blueprint('wechat', __name__, url_prefix='/wechat')

@view.route('/share')
def share():
    key = request.args.get('k')
    ws = WechatShare.query.filter_by(key=key).first()
    print '==========', ws.data
    ab = ws.data['abstract']
    abstract = ab.split(' ')
    pic_url = ws.data.get('lc_url')
    if not pic_url:
       pic_url = ws.data['pic_url']
       pic_url = cron.get_img(pic_url)
       if not pic_url:
           pic_url = ws.data['pic_url']
       else:
           ws.data['lc_url'] = pic_url
           flush(ws)
    return render_template('wechat/share.html', title=ws.data['title'], abstract=abstract, pic_url=pic_url)


