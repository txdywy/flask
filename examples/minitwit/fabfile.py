from fabric.api import *
env.use_ssh_config = True

def sz(file):
    put(file, '~/')

def rz(file):
    get(file, './')

def deploy_alancer():
    with cd('./flask/examples/minitwit/'):
  run('git pull')
  run('supervisorctl restart all')
