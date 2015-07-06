from flask import (Blueprint, current_app, request, g, url_for, make_response,
                   render_template, redirect, jsonify)

view = Blueprint('test', __name__, url_prefix='/test')

@view.route('/haha')
def haha():
    return 'hahaahhaha'


