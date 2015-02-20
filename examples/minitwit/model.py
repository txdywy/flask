from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DATETIME
import datetime

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
    __tablename__ = 'user'
    user_id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    email = Column(String(120), unique=True)
    pw_hash = Column(String(128))
    school = Column(String(128))
    city = Column(String(50))
    country = Column(String(50))
    zipcode = Column(String(50))    
    phone = Column(String(50))

    def __init__(self, username, email, pw_hash):
        self.username = username
        self.email = email
        self.pw_hash = pw_hash

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

    def __init__(self, title, client='', email='', desp='', image_url=None, service='web development', client_id=None):
        self.title = title
        self.client= client
        self.email = email
        self.desp = desp
        self.service = service
        self.client_id = client_id
        if image_url:
            self.image_url=image_url
        self.create_time = datetime.datetime.now()

    def __repr__(self):
        return '<Project %r>' % (self.title)

class Client(Base):
    __tablename__ = 'client'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    email = Column(String(120))

    def __init__(self, name, email):
        self.name = name
        self.email = email

    def __repr__(self):
        return '<Client %r>' % (self.name)

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
