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
     render_template, abort, g, flash, _app_ctx_stack
from werkzeug import check_password_hash, generate_password_hash
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY

from model import flush, db_session, Project, Contact, Client, User
import util

PROJECT_IMAGE_KEY_TEMPLATE = 'projects/%s'
PROJECT_IMAGE_URL_TEMPLATE = 'https://s3-us-west-2.amazonaws.com/alancer-images/' + PROJECT_IMAGE_KEY_TEMPLATE
s3_conn = S3Connection(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)

PROJECT_LOCAL_IMAGE_TEMPLATE = 'static/project/%s'
# configuration
DATABASE = './minitwit.db'
PER_PAGE = 30
DEBUG = True
SECRET_KEY = 'development key'
ALANCER_INDEX = 'alancer/index.html'
ALANCER_HTTP_ROOT = 'http://alancer.cf/'
ALANCER_SERVICE_EMAIL = 'geniusron@gmail.com'

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('MINITWIT_SETTINGS', silent=True)

def add_project(title, email='', desp='', client='N/A', image_url='', service='web dev', client_id=None):
    p = Project(title, client, email, desp, image_url, service, client_id)
    flush(p)
    if not image_url:
        image_file = PROJECT_LOCAL_IMAGE_TEMPLATE % ('project_%s.png' % p.id)
        p.image_url = ALANCER_HTTP_ROOT + image_file
        flush(p)


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


@app.cli.command('initdb')
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


@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        #g.user = query_db('select * from user where user_id = ?', [session['user_id']], one=True)
        g.user = User.query.get(session['user_id'])


@app.route('/contact', methods=['POST'])
def contact():
    name = request.form['name']
    phone = request.form['phone']
    email = request.form['email']
    message = request.form['message']
    c = Contact(name, phone, email, message)
    flush(c)
    util.send_email('[Alancer Contact][%s][%s][%s]' % (name, phone, email), message, ALANCER_SERVICE_EMAIL)
    return 'success'

@app.route('/project')
def project():
    projects = Project.query.all()
    return render_template('project.html', projects=projects)


@app.route('/index')
def index():
    return render_template(ALANCER_INDEX)


@app.route('/')
def timeline():
    """Shows a users timeline or if no user is logged in it will
    redirect to the public timeline.  This timeline shows the user's
    messages as well as all the messages of followed users.
    """
    return render_template(ALANCER_INDEX)
    """
    if not g.user:
        return redirect(url_for('public_timeline'))
    return render_template('timeline.html', messages=query_db('''
        select message.*, user.* from message, user
        where message.author_id = user.user_id and (
            user.user_id = ? or
            user.user_id in (select whom_id from follower
                                    where who_id = ?))
        order by message.pub_date desc limit ?''',
        [session['user_id'], session['user_id'], PER_PAGE]))
    """


@app.route('/public')
def public_timeline():
    """Displays the latest messages of all users."""
    return render_template('timeline.html', messages=query_db('''
        select message.*, user.* from message, user
        where message.author_id = user.user_id
        order by message.pub_date desc limit ?''', [PER_PAGE]))


@app.route('/<username>')
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
            flash('You were logged in')
            session['user_id'] = user.user_id
            #return redirect(url_for('timeline'))
            return redirect(url_for('index'))
    return render_template('login.html', error=error)


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
        elif get_user_id(request.form['username']) is not None:
            error = 'The username is already taken'
        else:
            #db = get_db()
            #db.execute('''insert into user (
            #  username, email, pw_hash) values (?, ?, ?)''',
            #  [request.form['username'], request.form['email'],
            #   generate_password_hash(request.form['password'])])
            #db.commit()
            u = User(username=request.form['username'].lower(), email=request.form['email'], pw_hash=generate_password_hash(request.form['password']))
            flush(u)
            util.send_email('[Alancer] Congratulations!', 'You have registered at alancer!', request.form['email'])
            util.send_email('[Alancer Signup]', 'You have a new user [%s] @lancer!' % request.form['email'], ALANCER_SERVICE_EMAIL) 
            flash('You were successfully registered and can login now')
            return redirect(url_for('login'))
    return render_template('register.html', error=error)


@app.route('/logout')
def logout():
    """Logs the user out."""
    flash('You were logged out')
    session.pop('user_id', None)
    return redirect(url_for('index'))
    #return redirect(url_for('public_timeline'))


# add some filters to jinja
app.jinja_env.filters['datetimeformat'] = format_datetime
app.jinja_env.filters['gravatar'] = gravatar_url
