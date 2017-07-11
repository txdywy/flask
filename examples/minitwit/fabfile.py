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

def ip():
    print env.host_string
    print env.host
    x = HOST_DATA.get(env.host_string, 'no host found')
    print x
    print '-' * ( len(' '.join(x)) + 10 ) + '\n'

HOST_DEV = [] # ['miso', 'airbb', 'nn', 'mm', ] retired
HOST_ALANCER = ['wei'] # ['polo', 'sushi', 'noodle', 'udon', 'natto'] retired
HOST_VPN = ['ton', 
            'koala', 
            'ham', 
            'wiener', 
            'crab', 
            'laksa', 
            'bbq', 
            'pie', 
            'stew', 
            'suki', 
            'bacon', 
            'chip', 
            'fish', 
            'ice', 
            'kim',
            'mei',
            'wei',
            'iit',
            'tod',
            ] # ['tempura', 'ramen', 'donut', 'nori', 'mm', 'rib', 'steak', 'buckeye', 'natto', 'curry', ] retired
HOST_APPFLOOD = ['pre3-01', 'af_test', 'test3', 'sandbox', 'pre3-jp']
HOST_ALL = HOST_DEV + HOST_ALANCER + HOST_VPN + HOST_APPFLOOD
HOST_TBK = HOST_DEV + HOST_VPN
HOST_EVIL = []
HOST_FA = [] # ['miso', 'nn', ] retired


HOST_LAUNCH_DATE = {
    #'udon': datetime.datetime(2015, 6, 5),
    #'sushi': datetime.datetime(2015, 4, 6),
    #'noodle': datetime.datetime(2015, 4, 7),
    #'airbb': datetime.datetime(2015, 8, 26),
    #'nn': datetime.datetime(2015, 8, 29),
    #'mm': datetime.datetime(2015, 8, 31),
    #'rib': datetime.datetime(2016, 2, 16),
    #'steak': datetime.datetime(2016, 2, 16),
    #'buckeye': datetime.datetime(2016, 12, 14),
    #####-----------------------------------#####
    #'natto': datetime.datetime(2016, 5, 23),
    #'curry': datetime.datetime(2016, 6, 27),
    #####-----------------------------------#####
    'ton': datetime.datetime(2016, 8, 18),
    'koala': datetime.datetime(2016, 8, 18),
    'ham': datetime.datetime(2016, 8, 18),
    'wiener': datetime.datetime(2016, 9, 1),
    'crab': datetime.datetime(2016, 9, 1),
    'laksa': datetime.datetime(2016, 9, 2),
    'bbq': datetime.datetime(2016, 9, 2),
    'pie': datetime.datetime(2016, 9, 5),
    'stew': datetime.datetime(2016, 9, 5),
    'suki': datetime.datetime(2016, 10, 10), 
    'bacon': datetime.datetime(2016, 12, 9), 
    'chip': datetime.datetime(2016, 12, 14),
    'fish': datetime.datetime(2016, 12, 14),
    'ice': datetime.datetime(2016, 12, 20),
    'kim': datetime.datetime(2017, 2, 3),
    'mei': datetime.datetime(2017, 5, 2),
    'wei': datetime.datetime(2017, 5, 5),
    'iit': datetime.datetime(2017, 6, 7),
    'tod': datetime.datetime(2017, 7, 10),
}


HOST_INDEX = {#'01': 'rib',      #kr@yahoo
              #'02': 'steak',    #kr@yahoo
              #'17': 'buckeye',  #us-east-oh@outlook
              #'03': 'natto',    #jp@yahoo
              '04': 'ton',      #jp@yahoo
              #'05': 'curry',    #in@yahoo
              '06': 'koala',    #au@yahoo
              '07': 'ham',      #us-east@yahoo
              '08': 'wiener',   #eu-frank@outlook
              '09': 'crab',     #us-west-cal@outlook
              '10': 'laksa',    #sg@outlook
              '11': 'stew',     #eu-ire@gmail
              '12': 'bbq',      #sa@gmail
              '13': 'pie',      #us-west-ore@gmail
              '14': 'suki',     #jp@gmail
              '15': 'bacon',    #ca@gmail
              '16': 'chip',     #uk@outlook
              '18': 'fish',     #uk@outlook
              '19': 'ice',      #us-east-oh@outlook
              '20': 'kim',      #kr@163
              '21': 'mei',      #jp@163
              '22': 'wei',      #jp@163
              '23': 'iit',      #in@gmail
              '24': 'tod',      #jp@gmail
             }

HOST_DATA = {#'rib'    : ('01', 'kr',    'yahoo'),
             #'steak'  : ('02', 'kr',    'yahoo'),
             #'buckeye': ('17', 'ue-oh', 'outlook'),
             #'natto'  : ('03', 'jp',    'yahoo'),
             'ton'    : ('04', 'jp',    'yahoo'),
             #'curry'  : ('05', 'in',    'yahoo'),
             'koala'  : ('06', 'au',    'yahoo'),
             'ham'    : ('07', 'ue',    'yahoo'),
             'wiener' : ('08', 'eu-de', 'outlook'),
             'crab'   : ('09', 'uw-ca', 'outlook'),
             'laksa'  : ('10', 'sg',    'outlook'),
             'stew'   : ('11', 'eu-ir', 'gmail'),
             'bbq'    : ('12', 'sa',    'gmail'),
             'pie'    : ('13', 'uw-or', 'gmail'),
             'suki'   : ('14', 'jp',    'gmail'),
             'bacon'  : ('15', 'ca',    'gmail'),
             'chip'   : ('16', 'uk',    'outlook'),
             'fish'   : ('18', 'uk',    'outlook'),
             'ice'    : ('19', 'ue-oh', 'outlook'),
             'kim'    : ('20', 'kr',    '163'),
             'mei'    : ('21', 'jp',    '163'),
             'wei'    : ('22', 'jp',    '163'),
             'iit'    : ('23', 'in',    'gmail'),
             'tod'    : ('24', 'jp',    'gmail'),
             }


def hls():
    print 'HOST_DEV[%s]: ' % len(HOST_DEV) + ','.join(HOST_DEV)
    print 'HOST_ALANCER[%s]: ' % len(HOST_ALANCER)+ ','.join(HOST_ALANCER)
    print 'HOST_VPN[%s]: ' % len(HOST_VPN) + ','.join(HOST_VPN)
    print 'HOST_APPFLOOD[%s]: ' % len(HOST_APPFLOOD) + ','.join(HOST_APPFLOOD)
    print 'HOST_ALL[%s]: ' % len(HOST_ALL) + ','.join(HOST_ALL)
    print 'HOST_TBK[%s]: ' % len(HOST_TBK) + ','.join(HOST_TBK)
    print 'HOST_EVIL[%s]: ' % len(HOST_EVIL) + ','.join(HOST_EVIL)
    print 'HOST_FA[%s]: ' % len(HOST_FA) + ','.join(HOST_FA)


def timeout():
    host = env.host_string
    launch_date = HOST_LAUNCH_DATE.get(host)
    if launch_date:
        today = datetime.datetime.today()
        days = (today - launch_date).days
        print 'EC2 [%s] will be timeout in [%s] days' % (host, 365 - days)

def fa():
    env.hosts = HOST_FA

def evil():
    env.hosts = HOST_EVIL

def tbk():
    env.hosts = HOST_TBK

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

def ikeup():
    with cd('~/ubuntu_vpn/'):
        run('git pull')
        run('./ikev2.sh')

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

def ti():
    with cd('~/flask/examples/minitwit/'):
        run("python -c 'import ticket as t;t.ti(1,1,5)'")

