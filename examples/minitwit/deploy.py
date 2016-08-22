from fabric.api import *
SUDO_PIP_INSTALL = 'sudo pip install %s'
pkgs = ['boto',
        'beautifulsoup4',
        'fake-factory',
        'flask',
        'flask-triangle',
        'requests',
        'requests[security]',
        'pillow',
        'sqlalchemy',
        'supervisor',
        'uwsgi',
        'leancloud-sdk',
        'numpy',
        'jieba',
        'networkx',
        'ngxtop',
        'Flask-Babel',
        'redis',
        'celery',
        'simplejson',
        'mysql-python',
        'bosonnlp',
        'gevent',
        'tqdm',
        'requesocks',
        'pycurl',
        'iso3166',
        'pytesseract',
        'flask-socketio',
        'eventlet',
        'gunicorn==18.0',
        'bypy',
       ]
for pkg in pkgs:
    local(SUDO_PIP_INSTALL % pkg)
