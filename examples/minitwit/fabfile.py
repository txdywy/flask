from fabric.api import * 
env.use_ssh_config = True
#env.hosts = ['sushi', 'polo', 'noodle']
def localhost():
    #env.use_ssh_config = False
    global run 
    run = local

def send(file):
    put(file, '~/')

def recv(file):
    get(file, './')

def wget(url):
    with cd('/tmp'):
        run('wget ' + url)
        f = url.split('/')[-1]
        get(f, './')

def dev():
    env.hosts = ['miso', 'airbb', 'nn', 'mm']
 
def alancer():
    env.hosts = ['sushi', 'noodle', 'udon'] # 'polo' retired

def vpn():
    env.hosts = ['tempura', 'ramen', 'donut', 'nori' , 'mm']

def appflood():
    env.hosts = ['pre3-01', 'af_test', 'test3', 'sandbox']

def pull():
    with cd('~/flask/examples/minitwit/'):
        run('git pull')

def restart():
    with cd('~/flask/examples/minitwit/'):
        run('supervisorctl restart alancer')

def install():
    run('cd ~/flask/examples/minitwit;sh install.sh')

def update_db():
    with cd('~/flask/examples/minitwit/'):
        run('openssl enc -des -d -a -in alancer_db_enc -out alancer.db')

def db():
     with cd('~/flask/examples/minitwit/'):
         run('./db_dec')

def init_db():
    with cd('~/flask/examples/minitwit/'):
        run("python -c 'from model import *;init_db()'")

def free():
    run('free -mh')

def net():
    run('vnstat')
    run('vnstat -h')
    run('vnstat -d')
    run('vnstat -w')
    run('vnstat -m')

def fd():
    run('cat /proc/sys/fs/file-nr')

def dns(url):
    dns_server = ['', #local
                  '8.8.8.8', #Google
                  '8.8.4.4', #Google
                  '114.114.114.114', #ChinaTele
                  '4.2.2.2', #Legend
                  '208.67.222.222', #OpenDNS
                  '180.76.76.76', #Baidu
                  '223.5.5.5', #Ali
                  '223.6.6.6', #Ali
                  ]
    for dns in dns_server:
        run('nslookup %s %s' % (url, dns))
