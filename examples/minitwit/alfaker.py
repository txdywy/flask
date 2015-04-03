from minitwit import *
from faker import Factory
from pygoogle import pygoogle
from bs4 import BeautifulSoup

def add_project():
    fake = Factory.create('en_US')
    email = str(fake.email())
    name = str(fake.name())
    client = Client(name=name, email=email)
    flush(client)
    add_project(title=str(fake.company()), email=email, desp=str(fake.text()), client=name, image_url='', service='web dev', client_id=client.id)

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


