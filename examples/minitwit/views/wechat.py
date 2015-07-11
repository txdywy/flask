from flask import (Blueprint, current_app, request, g, url_for, make_response,
                   render_template, redirect, jsonify)
from models.model_wechat import *
view = Blueprint('wechat', __name__, url_prefix='/wechat')

@view.route('/share')
def share():
    key = request.args.get('k')
    ws = WechatShare.query.filter_by(key=key).first()
    print '==========', ws.data
    ab = ws.data['abstract']
    abstract = ab.split(' ')
    return render_template('wechat/share.html', title=ws.data['title'], abstract=abstract, pic_url=ws.data['pic_url'])


