# -*- coding: utf-8 -*-
"""
    Alancer
    ~~~~~~~~

    An application written with Flask and sqlite3.

    :copyright: (c) 2015 by Yi Wei.
    :license: BSD, see LICENSE for more details.
"""

import time
from sqlite3 import dbapi2 as sqlite3
from hashlib import md5
from datetime import datetime
from flask import Flask, request, session, url_for, redirect, \
     render_template, abort, g, flash, _app_ctx_stack, make_response
import flask
from flask.ext.triangle import Triangle
from werkzeug import check_password_hash, generate_password_hash
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from PIL import Image
from model import flush, db_session
from model import Project, Contact, Client, User, UserLike, Message, ProjectApply, Chat, UserChat
from sqlalchemy import desc
import util, functools
import simplejson as json
from random import randint
try:
    import cache as cacheal 
except:
    print '================no cacheal=============='
    cacheal = None
try:
    import wx_util
except:
    print '------------wx_util import err-----------'
    wx_util = None
try:
    from config import ALANCER_HOST
except:
    print '---------------no host set---------------'
    ALANCER_HOST = 'alancer.ga'

import ierror
from WXBizMsgCrypt import SHA1
import xml.etree.ElementTree as ET
from pygoogle import get_pic_url
import alfaker

WX_SHA1 = SHA1()

from leancloud import File
from StringIO import StringIO
try:
    from config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
    s3_conn = S3Connection(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
except:
    print '------------no valid s3 config keys------------'

try:
    from config import WX_TOKEN
except:
    print '------------WX_TOKEN------------'
    WX_TOKEN = ''

try:
    from config import LC_APP_ID, LC_APP_KEY
    import leancloud
    leancloud.init(LC_APP_ID, LC_APP_KEY)
except:
    print '------------import leancloud error------------'

import chat as lcc
    
try:
    from config import ALANCER_BAIDU_STATS
except:
    ALANCER_BAIDU_STATS = ''
    print '----------------no baidu stat js loaded----------------'

from flask.ext.babel import Babel, gettext as _, get_locale

PROJECT_IMAGE_KEY_TEMPLATE = 'projects/%s'
PROJECT_IMAGE_URL_TEMPLATE = 'https://s3-us-west-2.amazonaws.com/alancer-images/' + PROJECT_IMAGE_KEY_TEMPLATE

PROJECT_LOCAL_IMAGE_TEMPLATE = 'static/project/%s'
# configuration
DATABASE = './minitwit.db'
PER_PAGE = 30
DEBUG = True
SECRET_KEY = 'development key'
ALANCER_INDEX = 'project_list.html'#'alancer/index.html'
ALANCER_HTTP_ROOT = 'http://alancer.cf'
ALANCER_SERVICE_EMAIL = 'geniusron@gmail.com'
ALANCER_MESSAGE_OFFSET = 10

# cacheal
ALANCER_ALL_PROJECTS = 'alancer.all.projects'
ALANCER_USER_PROJECTS_INDEX = 'alancer.user.projects.index.%s'
ALANCER_USER_CLIENT_MESSAGES = 'alancer.user.client.messages.%s.%s'

NO_CONTENT_PICTURE = 'http://media-cache-ak0.pinimg.com/736x/3d/b0/4a/3db04ab7349e7f791d3819b57230751d.jpg'

# create our little application :)
app = Flask(__name__)
app.config['BABEL_DEFAULT_LOCALE'] = 'zh_Hans_CN'
Triangle(app)
app.config.from_object(__name__)
app.config.from_envvar('MINITWIT_SETTINGS', silent=True)
babel = Babel(app)

def add_project(title, email='', desp='', client='N/A', image_url='', service='web dev', client_id=None, client_title='', location=''):
    p = Project(title, client, email, desp, image_url, service, client_id, client_title, location)
    flush(p)
"""
    if not image_url:
        image_file = PROJECT_LOCAL_IMAGE_TEMPLATE % ('project_%s.png' % p.id)
        p.image_url = ALANCER_HTTP_ROOT + '/' + image_file
        flush(p)
"""

def img_local_set(img_name, img_str):
    with open(PROJECT_IMAGE_KEY_TEMPLATE % img_name, 'w') as f:
        f.write(img_str)
    return len(img_str)


def img_local_get(img_name):
    with open(PROJECT_IMAGE_KEY_TEMPLATE % img_name, 'r') as f:
        img_str = f.read()
    return img_str


def img_set(img_name, img_str):
    b = s3_conn.get_bucket('alancer-images')
    k = Key(b)
    k.key = PROJECT_IMAGE_KEY_TEMPLATE % img_name
    str_len = k.set_contents_from_string(img_str)
    return str_len


def img_get(img_name):
    b = s3_conn.get_bucket('alancer-images')
    k = Key(b)
    k.key = img_name
    return k.get_contents_as_string(PROJECT_IMAGE_KEY_TEMPLATE % img_name)


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    top = _app_ctx_stack.top
    if not hasattr(top, 'sqlite_db'):
        top.sqlite_db = sqlite3.connect(app.config['DATABASE'])
        top.sqlite_db.row_factory = sqlite3.Row
    return top.sqlite_db


@app.teardown_appcontext
def close_database(exception):
    """Closes the database again at the end of the request."""
    top = _app_ctx_stack.top
    if hasattr(top, 'sqlite_db'):
        top.sqlite_db.close()


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


def init_db():
    """Initializes the database."""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


#@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database.')


def query_db(query, args=(), one=False):
    """Queries the database and returns a list of dictionaries."""
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    return (rv[0] if rv else None) if one else rv


def get_user_id(username):
    """Convenience method to look up the id for a username."""
    rv = query_db('select user_id from user where username = ?',
                  [username], one=True)
    return rv[0] if rv else None


def format_datetime(timestamp):
    """Format a timestamp for display."""
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d @ %H:%M')


def gravatar_url(email, size=80):
    """Return the gravatar image for the given email address."""
    return 'http://www.gravatar.com/avatar/%s?d=identicon&s=%d' % \
        (md5(email.strip().lower().encode('utf-8')).hexdigest(), size)

def login_required(f):
    @functools.wraps(f)
    def func(*args, **kwargs):
        if 'user_id' in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('login')) 
    return func

def message_secured(f):
    @functools.wraps(f)
    def func(*args, **kwargs):
        user_id = session['user_id']
        m_user_id = request.args.get('m_user_id')
        m_client_id = request.args.get('m_client_id')
        c_user_id = Client.query.get(m_client_id).user_id
        #print '=========================',user_id,m_user_id, c_user_id
        if int(user_id) in (int(m_user_id), int(c_user_id)):
            return f(*args, **kwargs)
        else:
            abort(403)
    return func

def power_required(power=User.POWER_ADMIN):
    def deco(f):
        @functools.wraps(f)
        def func(*args, **kwargs):
            if g.user.power & power:
                return f(*args, **kwargs) 
            else:
                return redirect(url_for('login'))
        return func
    return deco

def get_user_message_num(user_id):
    user = User.query.get(user_id)
    if user.role == User.USER_CLIENT:
        client = Client.query.filter_by(user_id=user_id).first()
        client_id = client.id if client else None
        message_num = Message.query.filter_by(client_id=client_id).group_by(Message.user_id).count()
    else:
        message_num = Message.query.filter_by(user_id=user_id).group_by(Message.client_id).count()
    return message_num

@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        #g.user = query_db('select * from user where user_id = ?', [session['user_id']], one=True)
        g.user = User.query.get(session['user_id'])
        g.admin_power = g.user.power & User.POWER_ADMIN
        g.isowner = g.user.role & User.USER_CLIENT
        g.message_num = get_user_message_num(g.user.user_id)

@app.route('/wx', methods=['GET', 'POST'])
def wx():
    signature = request.args.get('signature')
    timestamp = request.args.get('timestamp')
    nonce = request.args.get('nonce')
    echostr = request.args.get('echostr')
    token = WX_TOKEN
    if request.method == 'POST':
        #print '------', request.data
        return wx_util.reply(request.data)
    return echostr

@app.route('/admin', methods=['GET'])
@login_required
@power_required(power=User.POWER_ADMIN)
def admin():
    classes = ['active', 'success', 'info', 'warning', 'danger']
    cls = {}
    projects = Project.query.all()
    project_num = len(projects)
    cls = dict((p.id, classes[p.id % len(classes)]) for p in projects)
    clients = Client.query.all()
    users = User.query.all()
    return render_template('admin.html', cls=cls, projects=projects, project_num=project_num, clients=clients, users=users)    

@app.route('/upload', methods=['POST'])
@login_required
@power_required(power=User.POWER_ADMIN)
def upload():
    try:
        title = request.form['title']
        desp = request.form['desp']
        incentive = request.form['incentive']
        client_id = int(request.form['client'])
        image_url = request.form['image']
    except:
        print 'upload error: %s' % str(request.form)
        return 'failed'
    client = Client.query.get(client_id)
    p = Project(title=title, email=client.email, desp=desp, client=client.name, image_url=image_url, service='web dev', client_id=client.id, client_title=client.title, location=client.location, incentive=incentive, icon=client.icon)
    flush(p)
    return 'success'

@app.route('/upload_image', methods=['POST'])
@login_required
def upload_image():        
    try:
        HEIGHT, WIDTH = 384, 240
        c = request.files['file'].read()
        file_orig = StringIO(c)
        im = Image.open(file_orig)
        h, w = im.size
        if h > HEIGHT or w > WIDTH:
            im.thumbnail((HEIGHT, WIDTH), Image.ANTIALIAS)
            file = StringIO()
            h, w = im.size
            if h==w:
                im = im.rotate(90 * 3)
            try:
                im.save(file, 'JPEG')
            except:
                #for .gif
                file = file_orig
        else:
            file = file_orig
        lc_file = File('pi', file_orig)
        lc_file.save()
        return lc_file.url 
    except Exception, e:
       print '=============== upload image failed ============ ', str(e)
       return NO_CONTENT_PICTURE

@app.route('/project_manage', methods=['GET'])
@login_required
def project_manage():
    classes = ['active', 'success', 'info', 'warning', 'danger']
    cls = {}
    user_id = session.get('user_id')
    client = Client.query.filter_by(user_id=user_id).first()
    client_id = client.id
    projects = Project.query.filter_by(client_id=client_id).all()
    project_num = len(projects)
    cls = dict((p.id, classes[p.id % len(classes)]) for p in projects)
    return render_template('project_manage.html', cls=cls, projects=projects, project_num=project_num, client_id=client_id)

@app.route('/owner_upload', methods=['POST'])
@login_required
def owner_upload():
    user_id = session.get('user_id')
    client = Client.query.filter_by(user_id=user_id).first()
    try:
        title = request.form['title']
        desp = request.form['desp']
        incentive = request.form['incentive']
        image_url = request.form['image']
    except:
        print 'upload error: %s' % str(request.form)
        return 'failed'
    p = Project(title=title, email=client.email, desp=desp, client=client.name, image_url=image_url, service='web dev', client_id=client.id, client_title=client.title, location=client.location, incentive=incentive, icon=client.icon)
    flush(p)
    return 'success'

@app.route('/bc', methods=['POST'])
@login_required
@power_required(power=User.POWER_ADMIN)
def bc():
    title = request.form['title']
    body = request.form['body']
    to = request.form['to']
    if not to:
        emails = [u.email for u in User.query.all()]
    else:
        emails = [User.query.get(int(to)).email]
    for email in emails:
        util.send_email(title, body, email)
    return redirect(url_for('admin'))

@app.route('/gp', methods=['POST'])
@login_required
@power_required(power=User.POWER_ADMIN)
def gp():
    n = request.form['n']    
    n = int(n) if n else 1
    for i in xrange(n):
        alfaker.gen_project()
    return redirect(url_for('admin'))

@app.route('/dp', methods=['POST'])
@login_required
@power_required(power=User.POWER_ADMIN)
def dp():
    n = request.form['n']
    n = int(n) if n else 1
    ps = Project.query.all()
    l = len(ps)
    for p in ps:
        if p.id>16 and (l - p.id)<n:
            db_session.delete(p)
    db_session.commit()
    db_session.flush()
    return redirect(url_for('admin'))

@app.route('/contact', methods=['POST'])
def contact():
    name = request.form['n']
    phone = request.form['phone']
    email = request.form['email']
    message = request.form['message']
    c = Contact(name, phone, email, message)
    flush(c)
    util.send_email('[Alancer Contact][%s][%s][%s]' % (name, phone, email), message, ALANCER_SERVICE_EMAIL)
    return 'success'

@app.route('/cat')
def cat():
    return render_template('cat.html', index_ag="{{$index}}")

@app.route('/zl')
def zl():
    return render_template('zl.html')

@app.route('/upc')
def upc():
    return render_template('upc.html')

@app.route('/ps')
def ps():
    projects = Project.query.order_by(desc(Project.id)).all()
    l = len(projects)
    r = l - 10
    s = randint(0, r if r > 0 else 0)
    return render_template('ps.html', projects=projects[s:s+10])

@app.route('/elb')
def elb():
    return '1'

#@app.route('/')
#@app.route('/index')
@app.route('/project_swiper')
def project_swiper():
    if not cacheal or not g.user:
        projects = Project.query.order_by(desc(Project.id)).all()
        l = len(projects)
        r = l - 10
        s = randint(0, r if r > 0 else 0)
    else:
        user_id = g.user.user_id
        projects = Project.query.order_by(desc(Project.id)).all()
        """
        projects = cacheal.get(ALANCER_ALL_PROJECTS)
        if not projects:
            projects = Project.query.order_by(desc(Project.id)).all()
            cacheal.set(ALANCER_ALL_PROJECTS, projects, 300)
        """    
        s = cacheal.get(ALANCER_USER_PROJECTS_INDEX % user_id)
        s = s if s else 0
        ns = (s + 10) % len(projects) if projects else 0
        cacheal.set(ALANCER_USER_PROJECTS_INDEX % user_id, ns)
    return render_template('project_swiper.html', projects=projects[s:s+10])

@app.route('/inf')
def inf():
    return render_template('inf.html')
 
@app.route('/infd')
def infd():
    start = int(request.args.get('start'))
    count = int(request.args.get('count'))
    return json.dumps(range(1, 20))

@app.route('/project')
def project():
    user_id = session.get('user_id')
    pas = {}
    pats = {}
    puds = {}
    pics = {}
    projects = Project.query.order_by(desc(Project.id)).all()
    clients = Client.query.all()
    cds = {client.id: client for client in clients}
    for project in projects:
        project_id = project.id
        if user_id:
            pa = ProjectApply.query.filter_by(user_id=user_id, project_id=project_id).first()
            pas[project_id] = True if pa else False
            pats[project_id] = str(pa.create_time)[:10] if pa else None
        puds[project_id] = (datetime.now() - project.create_time).days
        """
        if project.icon:
            pics[project_id] = project.icon
        else:    
            pics[project_id] = "http://cdnvideo.dolimg.com/cdn_assets/189e27f7a893da854ad965e1406cc3878af80307.jpg" #get_pic_url(project.client) 
        """
        pics[project_id] = cds[project.client_id].icon
    #print '----',pas
    #print '====',pats
    return render_template('project_list.html', cds=cds, projects=projects, pas=pas, pats=pats, puds=puds, pics=pics)

@app.route('/project_slider')
def project_slider():
    user_id = session.get('user_id')
    pas = {}
    pats = {}
    puds = {}
    pics = {}
    projects = Project.query.all()
    for project in projects:
        project_id = project.id
        if user_id:
            pa = ProjectApply.query.filter_by(user_id=user_id, project_id=project_id).first()
            pas[project_id] = True if pa else False
            pats[project_id] = str(pa.create_time)[:10] if pa else None
        puds[project_id] = (datetime.now() - project.create_time).days
        if project.icon:
            pics[project_id] = project.icon
        else:
            pics[project_id] = "http://cdnvideo.dolimg.com/cdn_assets/189e27f7a893da854ad965e1406cc3878af80307.jpg" #get_pic_url(project.client)
    #print '----',pas
    #print '====',pats
    return render_template('project_slider.html', projects=projects, pas=pas, pats=pats, puds=puds, pics=pics)

@app.route('/user')
@login_required
def user():
    user_id = request.args.get('user_id')
    user = User.query.get(user_id)
    clients = {}
    client = Client.query.filter_by(user_id=user_id).first()
    if client:
        clients[client.user_id] = client
    return render_template('user.html', user=user, USER_STUDENT=User.USER_STUDENT, clients=clients)

@app.route('/users', methods=['POST', 'GET'])
@login_required
def users():
    if request.method == 'GET': 
        f = request.args.get('filter')
        filter = int(f if f else 0)
        if filter == 0:
            users = User.query.all()
        elif filter == 1:
            users = User.query.filter_by(role=User.USER_CLIENT).all()
        elif filter == 2:
            users = User.query.filter_by(role=User.USER_STUDENT).all()
        else:
            users = []
    if request.method == 'POST':
        filter = int(request.form['filter'])
        if filter == 0:
            users = User.query.all()
        elif filter == 1:
            users = User.query.filter_by(role=User.USER_CLIENT).all()
        elif filter == 2:
            users = User.query.filter_by(role=User.USER_STUDENT).all()
        else:
            users = []
    cs = Client.query.all()
    clients = {}
    for c in cs:
        clients[c.user_id] = c
    return render_template('user_list.html', users=users, filter=filter, USER_STUDENT=User.USER_STUDENT, clients=clients)

@app.route('/profile')
@login_required
def profile():
    user_id = session['user_id']
    user = User.query.get(user_id)
    if user.role == User.USER_CLIENT:
        client = Client.query.filter_by(user_id=user.user_id).first()
        return render_template('profile_client.html', user=user, client=client)
    else:
        return render_template('profile.html', user=user)

@app.route('/project_info')
@login_required
def project_info():
    project_id = request.args.get('project_id')
    user_id = session['user_id']
    user = User.query.get(user_id)
    project = Project.query.get(project_id)
    client = Client.query.filter_by(user_id=user_id).first()
    if project.client_id != client.id:
        abort(403)
    return render_template('project_info.html', project=project)

@app.route('/project_new')
@login_required
def project_new():
    return render_template('project_new.html')    

@app.route('/create_project', methods=['POST'])
@login_required
def create_project():
    user_id = session['user_id']
    user = User.query.get(user_id)
    project = Project()
    client = Client.query.filter_by(user_id=user_id).first()
    project.client_id = client.id
    project.title = request.form['title']
    project.client = request.form['client']
    project.desp = request.form['desp']
    project.image_url = request.form['image_url']
    #project.service = request.form['service']
    #project.location = request.form['location']
    project.incentive = request.form['incentive']
    #project.client_title = request.form['client_title']
    project.valid_time = request.form['vt']
    flush(project)
    t = _('You have successfully created your project')
    flash(t + ' [%s]' % project.title)
    return redirect(url_for('project_manage'))

@app.route('/edit_project', methods=['POST'])
@login_required
def edit_project():
    user_id = session['user_id']
    user = User.query.get(user_id)
    project_id = request.form['project_id']
    project = Project.query.get(project_id)
    client = Client.query.filter_by(user_id=user_id).first()
    if project.client_id != client.id:
        abort(403)      
    project.title = request.form['title']
    project.client = request.form['client']
    project.desp = request.form['desp']
    project.image_url = request.form['image_url']
    #project.service = request.form['service']
    #project.location = request.form['location']
    project.incentive = request.form['incentive']
    #project.client_title = request.form['client_title']
    project.valid_time = request.form['vt']
    flush(project)
    t = _('You have successfully updated your project')
    flash(t + ' [%s]' % project.title)
    return redirect(url_for('project_manage'))
    #return render_template('project_info.html', project=project)

@app.route('/edit_profile', methods=['POST'])
@login_required
def edit_profile():
    if(request.method == 'POST'):
    	user_id = session['user_id']
    	user = User.query.get(user_id)
    	user.firstname = request.form['firstname']
    	user.lastname = request.form['lastname']
        user.city = request.form['city']
        user.country = request.form['country']
        #user.zipcode = request.form['zipcode']
        #user.phone = request.form['phone']
        user.profile = request.form['profile']
        user.icon = request.form['icon']
        user.username = request.form['username']
        user.email = request.form['email']
        user.refer1 = request.form['refer1']
        user.refer2 = request.form['refer2']
        if user.role == User.USER_STUDENT:
            user.school = request.form['school']
        elif user.role == User.USER_CLIENT:
            client = Client.query.filter_by(user_id=user.user_id).first()
            client.icon = request.form['icon']
            client.location = '%s %s' % (user.city, user.country)
            client.company = request.form['company']
            client.title = request.form['title']
            client.name = user.username
            client.email = user.email
            flush(client)
    	flush(user)
        flash(_('You have successfully updated your profile'))
    	return redirect(url_for('profile'))

@app.route('/mt')
def mt():
    return render_template('mt.html')

@app.route('/chat', methods=['POST', 'GET'])
@login_required
def chat():
    app_id = LC_APP_ID
    user_id = session['user_id']
    user = User.query.get(user_id)
    if(request.method == 'POST'):
        other_user_id = request.form['other_user_id']
    else:
        other_user_id = request.args.get('other_user_id') 
    other_user = User.query.get(other_user_id)
    chat = Chat.get_chat(user_id, other_user_id)
    if chat:
        room_id = chat.room_id
    else:
        room_id = lcc.new_chat(user_id, other_user_id)
        if room_id:
            Chat.new_chat(user_id, other_user_id, room_id)
        else:
            abort(404)
    return render_template('chat.html', app_id=app_id, room_id=room_id, user=user, other_user=other_user)

@app.route('/message', methods=['POST'])
@login_required
def message():
    user_id = session['user_id']
    user = User.query.get(user_id)
    client = Client.query.filter_by(user_id=user_id).first()
    m_user_id = request.form['m_user_id']
    m_client_id = request.form['m_client_id']
    m_client = Client.query.get(m_client_id)
    project_id = request.form.get('project_id')
    if user.role == User.USER_STUDENT:
        flag = Message.MESSAGE_USER
        if project_id:
            pa = ProjectApply.query.filter_by(project_id=project_id, user_id=user_id).first()
            if not pa:
                pa = ProjectApply(project_id=project_id, user_id=user_id)
                flush(pa)
    elif int(client.id) == int(m_client_id):
        flag = Message.MESSAGE_CLIENT
    else:
        flag = Message.MESSAGE_USER
    message = request.form['message']
    m = Message(m_user_id, m_client_id, message, flag)
    flush(m)
    messages = Message.query.filter_by(user_id=m_user_id, client_id=m_client_id).all()
    data = {}
    m_user = User.query.get(m_user_id)
    data['m_user_name'] = m_user.username
    data['m_user_icon'] = m_user.icon
    data['m_client_name'] = m_client.name
    #message notification to admin
    util.send_email('[Alancer] New Message', 'user:%s client:%s message:%s' % (m_user.username, m_client.name, message), ALANCER_SERVICE_EMAIL)
    client_user = User.query.get(m_client.user_id)
    data['m_client_icon'] = client_user.icon
    #print '---------------------',data
    message_room_link = ALANCER_HTTP_ROOT + url_for('message_room') + '?m_user_id=%s&m_client_id=%s#messageLabel' % (m_user_id, m_client.id)
    mr = '<a href="%s" style="text-decoration:none;color:#3b5998" target="_blank">View project chat</a>' % message_room_link    
    pas = ProjectApply.query.filter_by(user_id=m_user.user_id).all()
    project_titles = ', '.join([Project.query.get(pa.project_id).title for pa in pas]) if pas else 'N/A'
    project = Project.query.get(project_id) if project_id else None
    if flag == Message.MESSAGE_USER:
        #to project
        email_notify = client_user.email
        name_from = m_user.username
        email_title = 'Re: Alancer: new reply from %s to your job posting' % name_from
        email_body = '<br><br>'.join(['Hello %s,' % client_user.username, 
                                        '%s from %s has replied to your %s project(s) post.' % (name_from, m_user.school, project_titles), 
                                        'Click the link below to check it out.', mr]) 
    else:
        #to student
        email_notify = m_user.email
        name_from = client_user.username
        email_title = 'Re: Alancer: new reply from %s at %s' % (name_from, m_client.company)
        email_body = '<br><br>'.join(['Hello %s,' % m_user.username,
                                        '%s from %s has replied back to you.' % (name_from, m_client.company),
                                        'Click the link below to check it out.', mr])      
    util.send_email(email_title, email_body, email_notify)
    #print '-----------------',email_title, email_body, email_notify
    #util.send_email('[Alancer] New message from %s' % name_from, '%s: %s <br>%s' % (name_from, message, mr), email_notify)
    if len(messages) == 1:
        return render_template('message.html', data=data, Message=Message, client=m_client, messages=messages, m_user_id=m_user_id, m_user=m_user)
    messages = messages[-1:]
    return render_template('message_more.html', data=data, Message=Message, client=m_client, messages=messages, m_user_id=m_user_id, m_user=m_user)

@app.route('/message_room', methods=['GET', 'POST'])
@login_required
@message_secured
def message_room():
    index = request.args.get('index')
    index = int(index) if index else 0

    m_user_id = request.args.get('m_user_id')
    m_client_id = request.args.get('m_client_id')
    if not m_user_id or not m_client_id:
        redirect(url_for('login'))

    if index == 0:
        messages = Message.query.filter_by(user_id=m_user_id, client_id=m_client_id).all()
        cacheal.set(ALANCER_USER_CLIENT_MESSAGES % (m_user_id, m_client_id), messages)
        messages = messages[-ALANCER_MESSAGE_OFFSET:]
    else:
        messages = cacheal.get(ALANCER_USER_CLIENT_MESSAGES % (m_user_id, m_client_id))
        messages = messages[-(ALANCER_MESSAGE_OFFSET*(index+1)):-(ALANCER_MESSAGE_OFFSET*index)] if messages else [] 
    
    client = Client.query.get(m_client_id)
    data = {}
    m_user = User.query.get(m_user_id)
    m_client = client
    data['m_user_name'] = m_user.username
    data['m_client_name'] = m_client.name
    data['m_user_icon'] = m_user.icon
    m_client_user = User.query.get(m_client.user_id)
    data['m_client_icon'] = m_client_user.icon
    #ucd = (datetime.now() - m_user.create_time).days
    if index == 0:
        return render_template('message.html', data=data, Message=Message, client=client, messages=messages, m_user_id=m_user_id, m_user=m_user)
    else:
        if messages:
            return render_template('message_more.html', data=data, Message=Message, client=client, messages=messages, m_user_id=m_user_id, m_user=m_user)
        else:
            return ''

@app.route('/apply', methods=['GET'])
@login_required
@message_secured
def apply():
    m_user_id = request.args.get('m_user_id')
    m_client_id = request.args.get('m_client_id')
    project_id = request.args.get('project_id')
    if not m_user_id or not m_client_id:
        redirect(url_for('login'))
    messages = Message.query.filter_by(user_id=m_user_id, client_id=m_client_id).all()
    client = Client.query.get(m_client_id)
    data = {}
    m_user = User.query.get(m_user_id)
    m_client = client
    data['m_user_name'] = m_user.username
    data['m_client_name'] = m_client.name
    data['m_user_icon'] = m_user.icon
    ucd = (datetime.now() - m_user.create_time).days
    return render_template('apply.html', data=data, Message=Message, client=client, messages=messages, m_user_id=m_user_id, project_id=project_id, m_user=m_user, ucd=ucd)


@app.route('/message_box', methods=['GET', 'POST'])
@login_required
def message_box():
    user_id = session['user_id']
    message_items = []
    user = User.query.get(user_id)
    if user.role == User.USER_CLIENT:
        client = Client.query.filter_by(user_id=user_id).first()
        client_id = client.id if client else None
        messages = Message.query.filter_by(client_id=client_id).group_by(Message.user_id).all()
    else:
        messages = Message.query.filter_by(user_id=user_id).group_by(Message.client_id).all()
    now = datetime.now()
    for m in messages:
        mi = {}
        mi['m_user_id'] = m.user_id
        m_user = User.query.get(m.user_id)
        mi['m_username'] = m_user.username
        mi['message'] = m.message
        mi['m_client_id'] = m.client_id
        client = Client.query.get(m.client_id)
        mi['m_client_name'] = client.name
        mi['icon'] = m_user.icon if user.role == User.USER_CLIENT else client.icon
        delta = (now - (m.create_time if m.create_time else datetime(2015, 1, 1))).days
        mi['new'] = True if delta == 0 else False
        mi['days'] = delta
        message_items.append(mi)
    return render_template('message_box.html', message_items=message_items)


@app.route('/chat_box')
@login_required
def chat_box():
    user_id = session['user_id']
    uc = UserChat.query.filter_by(user_id=user_id).first() 
    us = []
    if uc:
        uid_set = uc.chat_list
        us = User.query.filter(User.user_id.in_(uid_set)).all()
    return render_template('chat_box.html', us=us)


@app.route('/like', methods=['GET', 'POST'])
@login_required
def like():
    if request.method == 'GET':
        return render_template(ALANCER_INDEX)    
    project_id = request.form['project_id']
    user_id = session['user_id']
    user = User.query.get(user_id)
    project = Project.query.get(project_id)
    user_like = UserLike.query.filter_by(user_id=user_id, project_id=project_id, valid=1).first()
    return render_template('like.html', project=project, user_like=user_like, user=user)


@app.route('/like_submit', methods=['POST'])
@login_required
def like_submit():
    user_id = session['user_id']
    project_id = request.form['project_id']
    message = request.form['message']
    user_like = UserLike.query.filter_by(user_id=user_id, project_id=project_id, valid=1).first()
    if not user_like:
        user_like = UserLike(user_id, project_id, message)
        flush(user_like)
    user = User.query.get(user_id)
    project = Project.query.get(project_id)
    return render_template('like.html', project=project, user_like=user_like, user=user)


@app.route('/')
@app.route('/index')
def index():
    print '++++++++++', _("hahaha"), get_locale()
    #return redirect(url_for('project_swiper'))
    return redirect(url_for('project'))
    #return render_template(ALANCER_INDEX)


'''
@app.route('/')
def alancer():
    """The Alancer front page
    """
    return redirect(url_for('project_swiper'))
    return redirect(url_for('project'))
    return render_template(ALANCER_INDEX)
'''

@app.route('/public')
def public_timeline():
    """Displays the latest messages of all users."""
    return render_template('timeline.html', messages=query_db('''
        select message.*, user.* from message, user
        where message.author_id = user.user_id
        order by message.pub_date desc limit ?''', [PER_PAGE]))


@app.route('/tl/<username>')
def user_timeline(username):
    """Display's a users tweets."""
    profile_user = query_db('select * from user where username = ?',
                            [username], one=True)
    if profile_user is None:
        abort(404)
    followed = False
    if g.user:
        followed = query_db('''select 1 from follower where
            follower.who_id = ? and follower.whom_id = ?''',
            [session['user_id'], profile_user['user_id']],
            one=True) is not None
    return render_template('timeline.html', messages=query_db('''
            select message.*, user.* from message, user where
            user.user_id = message.author_id and user.user_id = ?
            order by message.pub_date desc limit ?''',
            [profile_user['user_id'], PER_PAGE]), followed=followed,
            profile_user=profile_user)


@app.route('/<username>/follow')
def follow_user(username):
    """Adds the current user as follower of the given user."""
    if not g.user:
        abort(401)
    whom_id = get_user_id(username)
    if whom_id is None:
        abort(404)
    db = get_db()
    db.execute('insert into follower (who_id, whom_id) values (?, ?)',
              [session['user_id'], whom_id])
    db.commit()
    flash('You are now following "%s"' % username)
    return redirect(url_for('user_timeline', username=username))


@app.route('/<username>/unfollow')
def unfollow_user(username):
    """Removes the current user as follower of the given user."""
    if not g.user:
        abort(401)
    whom_id = get_user_id(username)
    if whom_id is None:
        abort(404)
    db = get_db()
    db.execute('delete from follower where who_id=? and whom_id=?',
              [session['user_id'], whom_id])
    db.commit()
    flash('You are no longer following "%s"' % username)
    return redirect(url_for('user_timeline', username=username))


@app.route('/add_message', methods=['POST'])
def add_message():
    """Registers a new message for the user."""
    if 'user_id' not in session:
        abort(401)
    if request.form['text']:
        db = get_db()
        db.execute('''insert into message (author_id, text, pub_date)
          values (?, ?, ?)''', (session['user_id'], request.form['text'],
                                int(time.time())))
        db.commit()
        flash('Your message was recorded')
    return redirect(url_for('timeline'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Logs the user in."""
    if g.user:
        #return redirect(url_for('timeline'))
        return redirect(url_for('index'))
    error = None
    if request.method == 'POST':
        #user = query_db('''select * from user where username = ?''', [request.form['username']], one=True)
        user = User.query.filter_by(username=request.form['username'].lower()).first()
        if user is None:
            error = 'Invalid username'
        elif not check_password_hash(user.pw_hash, request.form['password']):
            error = 'Invalid password'
        else:
            flash(_('You were logged in'))
            session['user_id'] = user.user_id
            return redirect(url_for('index'))
    if error:
        flash(_('Wrong with username or password'))
    return render_template('login.html', error=error)


ALANCER_WELCOME_BODY = """
You have successfully registered at aLancer. Click <a href="%s"><strong style="color:#00188f;"><span style="color:#00188f;">here</span></strong></a> to view the latest internship openings being offered by verified business owners nearby you. We may send you notices of new openings as they are added in the future. -the Alancer Team
"""

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registers the user."""
    if g.user:
        #return redirect(url_for('timeline'))
        return render_template(ALANCER_INDEX)
    error = None
    if request.method == 'POST':
        if not request.form['username']:
            error = 'You have to enter a username'
        elif not request.form['email'] or \
                '@' not in request.form['email']:
            error = 'You have to enter a valid email address'
        elif not request.form['password']:
            error = 'You have to enter a password'
        elif request.form['password'] != request.form['password2']:
            error = 'The two passwords do not match'
        #elif get_user_id(request.form['username']) is not None:
        #    error = 'The username is already taken'
        else:
            #db = get_db()
            #db.execute('''insert into user (
            #  username, email, pw_hash) values (?, ?, ?)''',
            #  [request.form['username'], request.form['email'],
            #   generate_password_hash(request.form['password'])])
            #db.commit()
            username=request.form['username'].lower()
            email=request.form['email']
            u = User(username=username, email=email, pw_hash=generate_password_hash(request.form['password']))
            u.icon = get_pic_url('lego %s %s' % (username, email))
            isowner = int(request.form.get('isowner'))
            if isowner:
                u.role = User.USER_CLIENT
            flush(u)
            if isowner:
                client = Client(name=u.username, email=u.email, user_id=u.user_id, icon=u.icon)
                flush(client)
            util.send_email(_('Welcome to Alancer'), ALANCER_WELCOME_BODY % url_for('project'), request.form['email'])
            print '===========', ALANCER_WELCOME_BODY % ('http://%s/project' % ALANCER_HOST)
            util.send_email('[Alancer Signup]', 'You have a new user [%s] @lancer!' % request.form['email'], ALANCER_SERVICE_EMAIL) 
            session['user_id'] = u.user_id
            flash(_('You were successfully registered and can login now'))
            return redirect(url_for('profile'))
    return render_template('register.html', error=error)


@app.route('/logout')
def logout():
    """Logs the user out."""
    flash(_('You were logged out'))
    session.pop('user_id', None)
    return redirect(url_for('index'))
    #return redirect(url_for('public_timeline'))

def dformat(d):
    return str(d)[:10]


# add some filters to jinja
app.jinja_env.filters['dformat'] = dformat
app.jinja_env.filters['datetimeformat'] = format_datetime
app.jinja_env.filters['gravatar'] = gravatar_url
app.jinja_env.filters['get_icon'] = get_pic_url
app.jinja_env.globals['ALANCER_BAIDU_STATS'] = ALANCER_BAIDU_STATS
app.jinja_env.globals['LC_APP_ID'] = LC_APP_ID
app.jinja_env.globals['LC_APP_KEY'] = LC_APP_KEY
