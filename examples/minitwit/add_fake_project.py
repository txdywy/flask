from model import *
from faker import Factory
fake = Factory.create('en_US')
add_project(title=str(fake.company()), email=str(fake.email()), desp=str(fake.text()), client=str(fake.name()), image_url='', service='web dev')
