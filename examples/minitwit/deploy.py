from fabric.api import *
SUDO_PIP_INSTALL = 'sudo pip install %s'
pkgs = ['boto',
        'beautifulsoup4',
        'fake-factory',
        'flask',
        'flask-triangle',
        'pillow',
        'sqlalchemy',
        'supervisor',
        'uwsgi',
        'leancloud-sdk',
        'numpy',
        'jieba',
        'networkx',
        'ngxtop',
       ]
for pkg in pkgs:
    local(SUDO_PIP_INSTALL % pkg)
