from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DATETIME, Text, ForeignKey
import datetime
import pygoogle
from faker import Factory
fake = Factory.create('en_US')

try:
    from config import RDS_HOST, RDS_NAME, RDS_PASS
    print '---------------mysql------------------'
except:
    RDS_HOST = RDS_NAME = RDS_PASS = ''
    print '---------------sqlite-----------------'

if RDS_HOST:
    engine = create_engine("mysql://%s:%s@%s/polodb" % (RDS_NAME, RDS_PASS, RDS_HOST), encoding='latin1', echo=True)
else:
    engine = create_engine('sqlite:///alancer.db', convert_unicode=True)

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def flush(db_obj=None):
    if db_obj:
        db_session.add(db_obj)
    db_session.commit()

def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    #import yourapplication.models
    Base.metadata.create_all(bind=engine)

class User(Base):
    USER_STUDENT = 0
    USER_CLIENT = 1
    POWER_ADMIN = 2**9

    __tablename__ = 'user'
    user_id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    email = Column(String(120), unique=True)
    pw_hash = Column(String(128))
    school = Column(String(128), default='')
    city = Column(String(50), default='')
    country = Column(String(50), default='')
    zipcode = Column(String(50), default='')    
    phone = Column(String(50), default='')
    role = Column(Integer, default=USER_STUDENT)
    power = Column(Integer, default=0)
    icon = Column(String(512))
    profile = Column(String(512), default='')
    create_time = Column(DATETIME())
    firstname = Column(String(20), default='')
    lastname = Column(String(20), default='')
    approved = Column(Integer, default=0)

    def __init__(self, username, email, pw_hash):
        self.username = username
        self.email = email
        self.pw_hash = pw_hash
        self.create_time = datetime.datetime.now()

    def __repr__(self):
        return '<User %r>' % (self.user_id)


class Project(Base):
    __tablename__ = 'project'
    id = Column(Integer, primary_key=True)
    title = Column(String(50), unique=True)
    client = Column(String(50))
    email = Column(String(120))
    desp = Column(String(500))
    image_url = Column(String(512))
    service = Column(String(50))
    create_time = Column(DATETIME())
    client_id = Column(Integer)
    location = Column(String(50), default='From Cyberspace')
    incentive = Column(String(500), default='U can U up!')
    client_title = Column(String(50), default='Owner')
    icon = Column(String(512))
    #cnt_like = Column(Integer, default=0)
    #cnt_dislike = Column(Integer, default=0)

    def __init__(self, title='', client='', email='', desp='', image_url=None, service='web development', client_id=None, client_title='', location='', incentive='', icon=''):
        if title:
            self.title = title
        else:
            self.title = str(fake.company())
        self.client= client
        self.email = email
        self.desp = desp
        self.service = service
        self.client_id = client_id
        if image_url:
            self.image_url = image_url
        if client_title:
            self.client_title = client_title
        if location:
            self.location = location 
        if incentive:
            self.incentive = incentive
        if icon:
            self.icon = icon
        self.create_time = datetime.datetime.now()

    def __repr__(self):
        return '<Project %r>' % (self.title)

class Client(Base):
    __tablename__ = 'client'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    email = Column(String(120))
    user_id = Column(Integer, ForeignKey('user.user_id'))
    company = Column(String(120), default='N/A')
    title = Column(String(120), default='N/A')
    icon = Column(String(512), default='http://img1.wikia.nocookie.net/__cb20140912133822/disney/images/6/6f/Baymax_Disney_INFINITY.png')
    location = Column(String(50), default='From Cyberspace') 

    def __repr__(self):
        return '<Client %r>' % (self.name)

class Client1(Base):
    __tablename__ = 'client1'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    email = Column(String(120))

    def __init__(self, name, email):
        self.name = name
        self.email = email

    def __repr__(self):
        return '<Client %r>' % (self.name)

class UserLike(Base):
    __tablename__ = 'user_like'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.user_id'))
    project_id = Column(Integer, ForeignKey('project.id'))
    valid = Column(Integer, index=True, default=1)
    comment = Column(String(1024))

    def __init__(self, user_id, project_id, comment=''):
        self.user_id = user_id
        self.project_id = project_id
        self.comment = comment

    def __repr__(self):
        return  '<UserLike %r>' % (self.id)

class Message(Base):
    MESSAGE_CLIENT = 0
    MESSAGE_USER = 1

    __tablename__ = 'message'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.user_id'))
    client_id = Column(Integer, ForeignKey('client.id'))
    message = Column(Text)
    flag = Column(Integer, default=MESSAGE_USER)
    create_time = Column(DATETIME())
    
    def __init__(self, user_id, client_id, message, flag):
        self.user_id = user_id
        self.client_id = client_id
        self.message = message
        self.flag = flag
        self.create_time = datetime.datetime.now()

    def __repr__(self):
        return  '<Message %r>' % (self.id)

class ProjectApply(Base):
    PROJECT_APPLIED = 0
    PROJECT_REJECTED = 1
    PROJECT_WITHDRAW = 2
    PROJECT_DECLINE = 3

    __tablename__ = 'project_apply'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.user_id'))
    project_id = Column(Integer, ForeignKey('project.id'))
    valid = Column(Integer, index=True, default=1)
    create_time = Column(DATETIME(), index=True)   
    status = Column(Integer, index=True, default=PROJECT_APPLIED)

    def __init__(self, user_id, project_id):
        self.user_id = user_id
        self.project_id = project_id
        self.create_time = datetime.datetime.now()
  
    def __repr__(self):
        return  '<ProjectApply %r>' % (self.id)

class Contact(Base):
    __tablename__ = 'contact'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    phone = Column(String(50))
    email = Column(String(120))
    message = Column(String(512))
    create_time = Column(DATETIME())
    
    def __init__(self, name, phone, email, message):
        self.name = name
        self.phone = phone
        self.email = email
        self.message = message
        self.create_time = datetime.datetime.now()

    def __repr__(self):
        return '<Contact %r>' % (self.name)
