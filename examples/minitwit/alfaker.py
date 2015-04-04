from minitwit import *
from faker import Factory
from pygoogle import pygoogle, get_pic_url
from bs4 import BeautifulSoup
from random import randint

def gen_project():
    fake = Factory.create('en_US')
    email = str(fake.email())
    name = str(fake.name())
    #client = Client(name=name, email=email)
    #flush(client)
    client = Client.query.get(1)
    title = str(fake.company())
    desp = get_para(title)
    client_title = str(fake.job())
    location = str(fake.city() + ', ' + fake.country())
    image_url = get_pic_url(title)
    incentive = 'Would like to pay $%s' % str(randint(0, 150))
    p = Project(title=title, email=email, desp=desp, client=name, image_url=image_url, service='web dev', client_id=client.id, client_title=client_title, location=location, incentive=incentive)
    flush(p)

def get_para(word='google'):
    g = pygoogle(word)
    g.pages = 1
    r = g.sr()
    return kill_html(r[0]) if r else 'N/A'

def kill_html(html):
    soup = BeautifulSoup(html)
    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()    # rip it out
    text = soup.get_text()
    return text.replace('\n', ' ').replace('\r', ' ')


