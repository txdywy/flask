from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DATETIME, Text, ForeignKey, PickleType
from sqlalchemy.ext.mutable import MutableDict
import datetime
from mutable import MutableList, MutableSet
engine = create_engine('sqlite:///wechat.db', convert_unicode=True) 
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

class WechatShare(Base):
    TAG_COMPARE = 0
    TAG_DETECT = 1
    __tablename__ = 'wechat_share'
    id = Column(Integer, primary_key=True)
    key = Column(String(128), unique=True)
    tag = Column(Integer, default=TAG_COMPARE)
    data = Column(MutableDict.as_mutable(PickleType))
    create_time = Column(DATETIME(), default=datetime.datetime.now())

    def __repr__(self):
        return '<WechatShare %r>' % (self.id)

