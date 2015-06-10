import csv
from StringIO import StringIO
from leancloud import File
from PIL import Image 
from config import *
from model import *
from config import LC_APP_ID, LC_APP_KEY
import leancloud
import datetime, time
leancloud.init(LC_APP_ID, LC_APP_KEY)
PASS_HASH = 'pbkdf2:sha1:1000$YPfvc8Gh$7139a371720291feab77eb4b6660fecd5e12810b' #123456
TIMEOUT = 5
def pause():
    for i in range(TIMEOUT):
        print '.'
        time.sleep(1)
def upload_image(fname):        
    HEIGHT, WIDTH = 384, 240
    #c = request.files['file'].read()
    with open(fname, 'rb') as f:
        c = f.read()
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

def join_time(raw):
    d = int(raw.split(' ')[0])
    return datetime.datetime.now() - datetime.timedelta(d)

def publish_time(raw):
    d = int(raw.split(' ')[0][:-1])
    return datetime.datetime.now() - datetime.timedelta(d)

def load_all():
    with open('pd.csv', 'rb') as f:
        lines = csv.reader(f)
        ps = []
        for line in lines:
            #print line
            p = {}
            
            raw = [i.strip('\r').strip('\n').strip(' ') for i in line]
            p['desp'] = raw[0]
            p['valid_time']= raw[1]
            p['incentive']= raw[2]
            p['publish_time']= raw[3]
            p['owner_name']= raw[4]
            p['icon']= raw[5]
            p['owner_title']= raw[6]
            p['company']= raw[7]
            p['logo']= raw[8]
            p['city'] = raw[9]
            p['country'] = raw[10]
            p['profile'] = raw[11]
            p['host'] = raw[12]
            p['join_time'] = raw[13]
            ps.append(p)

    #Create user/client/project
    for p in ps:
        username = p['owner_name'].split(' ')[0] + str(p['icon'].split('.')[0].split('-')[-1])
        email = '%s@gmail.com' % username
        u = User(username=username, email=email, pw_hash=PASS_HASH)
        u.firstname = p['owner_name'].split(' ')[0] 
        u.lastname = p['owner_name'].split(' ')[1]
        u.city = p['city']
        u.country = p['country']
        u.profile = p['profile']
        u.role = User.USER_CLIENT
        u.icon = upload_image('oim/icon/'+p['icon'])
        u.create_time = join_time(p['join_time'])
        flush(u)
        client = Client(name=u.username, email=u.email, user_id=u.user_id, icon=u.icon)
        client.title = p['owner_title']
        client.company = p['company']
        client.location = '%s %s' % (u.city, u.country)
        client.icon = u.icon
        flush(client)

        pause()
        #print p 
        project = Project()
        project.title = '%s\'s project' % u.username
        project.client = p['owner_name']
        project.email = email
        project.desp = p['desp'] + ' (%s)' % p['valid_time']
        project.image_url = upload_image('oim/logo/'+p['logo'])

        pause()
        project.service = ''
        project.location = client.location
        project.incentive = p['incentive']
        project.client_title = p['owner_title']
        project.icon = client.icon
        project.create_time = publish_time(p['publish_time'])
        flush(project)
        print '===============done============', u.user_id, client.id, project.id
