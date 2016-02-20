from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DATETIME, Text, ForeignKey, PickleType, desc, func
from sqlalchemy.ext.mutable import MutableDict
import datetime
from mutable import MutableList, MutableSet
engine = create_engine('sqlite:///proxy.db', convert_unicode=True) 
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

class Proxy(Base):
    __tablename__ = 'proxy'
    site_map = {0: 'free-proxy-list.net',
                1: 'samair.ru',
                2: 'cool-proxy.net',
                }
    id = Column(Integer, primary_key=True)
    active = Column(Integer, default=2, index=True) #0: down #1: up #2: new and default
    key = Column(String(32), unique=True)
    ip = Column(String(16), index=True)
    port = Column(String(8), default='80', index=True)
    code = Column(String(4), default='', index=True)
    country = Column(String(32), default='', index=True)
    anonymity = Column(String(32), default='', index=True)
    google = Column(Integer, default=0, index=True)
    https = Column(Integer, default=0, index=True)
    delay = Column(Integer, default=0)
    hit = Column(Integer, default=0)
    site = Column(Integer, default=0) #0: free-proxy-list.net #1: http://www.samair.ru #2: cool-proxy.net
    update_time = Column(DATETIME(), default=datetime.datetime.now())
    create_time = Column(DATETIME(), default=datetime.datetime.now())

    def __repr__(self):
        return '<Proxy %r>' % (self.id)
   
    def get_site(self):
        r = Proxy.site_map.get(self.site)
        return r if r else ''
