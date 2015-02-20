from minitwit import *
from faker import Factory
fake = Factory.create('en_US')
email = str(fake.email())
name = str(fake.name())
client = Client(name=name, email=email)
flush(client)
add_project(title=str(fake.company()), email=email, desp=str(fake.text()), client=name, image_url='', service='web dev', client_id=client.id)
