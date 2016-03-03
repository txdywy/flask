from fabric.api import * 
import datetime
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
        run('wget  --header="Accept: text/html" --user-agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:21.0) Gecko/20100101 Firefox/21.0" ' + url)
        f = url.split('/')[-1]
        get(f, './')

@hosts(['bastion'])
def bget(url):
    wget(url)

def ups():
    run('uptime -s')

def upp():
    run('uptime -p')

HOST_DEV = ['miso', 'airbb', 'nn', 'mm']
HOST_ALANCER = ['sushi', 'noodle', 'udon'] # 'polo' retired
HOST_VPN = ['tempura', 'ramen', 'donut', 'nori' , 'mm', 'rib', 'steak']
HOST_APPFLOOD = ['pre3-01', 'af_test', 'test3', 'sandbox', 'pre3-jp']
HOST_ALL = HOST_DEV + HOST_ALANCER + HOST_VPN + HOST_APPFLOOD

HOST_LAUNCH_DATE = {
    'udon': datetime.datetime(2015, 6, 5),
    'sushi': datetime.datetime(2015, 4, 6),
    'noodle': datetime.datetime(2015, 4, 7),
}

def timeout():
    host = env.host_string
    launch_date = HOST_LAUNCH_DATE.get(host)
    if launch_date:
        today = datetime.datetime.today()
        days = (today - launch_date).days
        print 'EC2 [%s] will be timeout in [%s] days' % (host, 365 - days)

def dev():
    env.hosts = HOST_DEV
 
def alancer():
    env.hosts = HOST_ALANCER

def vpn():
    env.hosts = HOST_VPN

def appflood():
    env.hosts = HOST_APPFLOOD

def all():
    env.hosts = HOST_ALL

def ti(n):
    with cd('~/flask/examples/minitwit/'):
        run("python -c 'import ticket as t;t.ti(%s)'" % n)

def pull():
    with cd('~/flask/examples/minitwit/'):
        run('git pull')

def restart():
    with cd('~/flask/examples/minitwit/'):
        run('supervisorctl restart alancer')

def gitup():
    with cd('~/flask/examples/minitwit/'):
        run('git pull')
        run('supervisorctl restart alancer')

@hosts(['udon'])
def ugitup():
    gitup()

@hosts(HOST_ALANCER)
def agitup():
    gitup()

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

def killall(key):
    run('ps -ef|grep %s|grep -v grep|cut -c 9-15' % key)
    run('ps -ef|grep %s|grep -v grep|cut -c 9-15|xargs kill -9' % key)

def cron():
    run('service cron status')

def cronon():
    run('sudo service cron start')

def cronoff():
    run('sudo service cron stop')
