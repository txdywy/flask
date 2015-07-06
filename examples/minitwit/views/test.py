from flask import (Blueprint, current_app, request, g, url_for, make_response,
                   render_template, redirect, jsonify)

view = Blueprint('test', __name__)

@view.route('/haha')
def haha():
    return 'hahaahhaha'


