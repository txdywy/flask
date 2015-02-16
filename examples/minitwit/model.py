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
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    email = Column(String(120), unique=True)

    def __init__(self, name=None, email=None):
        self.name = name
        self.email = email

    def __repr__(self):
        return '<User %r>' % (self.name)


class Project(Base):
    __tablename__ = 'project'
    id = Column(Integer, primary_key=True)
    title = Column(String(50), unique=True)
    email = Column(String(120))
    desp = Column(String(500))
    image_url = Column(String(512))
    create_time = Column(DATETIME())

    def __init__(self, title, email=None, desp='', image_url=None):
        self.title = title
        self.email = email
        self.desp = desp
        if image_url:
            self.image_url=image_url
        self.create_time = datetime.datetime.now()

    def __repr__(self):
        return '<Project %r>' % (self.title)
