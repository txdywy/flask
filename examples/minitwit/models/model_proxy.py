from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DATETIME, Text, ForeignKey, PickleType, desc
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
    id = Column(Integer, primary_key=True)
    active = Column(Integer, default=1, index=True)
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
    update_time = Column(DATETIME(), default=datetime.datetime.now())
    create_time = Column(DATETIME(), default=datetime.datetime.now())

    def __repr__(self):
        return '<Proxy %r>' % (self.id)
