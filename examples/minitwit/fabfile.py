from fabric.api import * 
env.use_ssh_config = True
#env.hosts = ['sushi', 'polo', 'noodle']
def sz(file):
    put(file, '~/')

def rz(file):
    get(file, './')

def deploy_alancer():
    with cd('./flask/examples/minitwit/'):
	    run('git pull')
	    run('supervisorctl restart all')

def update_db():
    with cd('./flask/examples/minitwit/'):
        run('git pull')
        run('openssl enc -des -d -a -in alancer_db_enc -out alancer.db')

def alancer():
    env.hosts = ['sushi', 'polo', 'noodle']

def free():
    run('free -mh')
