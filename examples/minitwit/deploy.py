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
       ]
for pkg in pkgs:
    local(SUDO_PIP_INSTALL % pkg)
local('openssl enc -des -d -a -in alancer_db_enc -out alancer.db')
local('mkdir logs')
local('touch logs/uwsgi.log logs/error.log')
