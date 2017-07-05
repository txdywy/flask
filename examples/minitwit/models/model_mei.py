from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DATETIME, Text, ForeignKey, PickleType, desc, func
from sqlalchemy.ext.mutable import MutableDict
import datetime
from mutable import MutableList, MutableSet
engine = create_engine('sqlite:///mei.db', convert_unicode=True) 
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

CDN_PREFIX = 'https://ig-s-c-a.akamaihd.net/hphotos-ak-xat1/'
class InstMei(Base):
    __tablename__ = 'inst_mei'
    id = Column(Integer, primary_key=True)
    inst_owner = Column(String(32), default='', index=True)
    active = Column(Integer, default=1, index=True) #0: down #1: up
    inst_code = Column(String(16), default='', index=True)
    inst_ts = Column(Integer, default=0)
    display_src = Column(Text, default='')
    inst_id = Column(String(16), index=True)
    thumbnail_src = Column(Text, default='')
    update_time = Column(DATETIME(), default=datetime.datetime.now())
    create_time = Column(DATETIME(), default=datetime.datetime.now())

    def __repr__(self):
        return '<InstMei %r>' % (self.id)

    def pic_url(self):
        return CDN_PREFIX + self.thumbnail_src.split('/')[-1]

    def to_dict(self):
        d = {}
        d['id'] = self.id
        d['owner'] = self.inst_owner
        d['secret'] = self.thumbnail_src.split('/')[-1]
        d['server'] = ''
        d['farm'] = 4
        d['title'] = self.inst_code
        d['ispublic'] = 1
        d['isfriend'] = 0
        d['isfamily'] = 0
        return d


class InstMeiMore(Base):
    __tablename__ = 'inst_mei_more'
    id = Column(Integer, primary_key=True)
    inst_owner = Column(String(32), default='', index=True)
    active = Column(Integer, default=1, index=True) #0: down #1: up
    inst_code = Column(String(16), default='', index=True)
    inst_ts = Column(Integer, default=0)
    display_src = Column(Text, default='')
    inst_id = Column(String(16), index=True)
    thumbnail_src = Column(Text, default='')
    update_time = Column(DATETIME(), default=datetime.datetime.now())
    create_time = Column(DATETIME(), default=datetime.datetime.now())

    def __repr__(self):
        return '<InstMeiMore %r>' % (self.id)

    def pic_url(self):
        return CDN_PREFIX + self.thumbnail_src.split('/')[-1]

    def to_dict(self):
        d = {}
        d['id'] = self.id
        d['owner'] = self.inst_owner
        d['secret'] = self.thumbnail_src.split('/')[-1]
        d['server'] = ''
        d['farm'] = 4
        d['title'] = self.inst_code
        d['ispublic'] = 1
        d['isfriend'] = 0
        d['isfamily'] = 0
        return d


class Dance(Base):
    __tablename__ = 'dance'
    id = Column(Integer, primary_key=True)
    category = Column(String(32), default='', index=True)
    like = Column(Integer, default=0)
    title = Column(Text, default='')
    image_url = Column(Text, default='')
    update_time = Column(DATETIME(), default=datetime.datetime.now())
    create_time = Column(DATETIME(), default=datetime.datetime.now())

    def __repr__(self):
        return '<Dance %r>' % (self.id)




class InstMeiVideo(Base):
    __tablename__ = 'inst_mei_video'
    id = Column(Integer, primary_key=True)
    inst_owner = Column(String(32), default='', index=True)
    active = Column(Integer, default=1, index=True) #0: down #1: up
    inst_code = Column(String(16), default='', index=True)
    inst_ts = Column(Integer, default=0)
    video_src = Column(Text, default='')
    inst_id = Column(String(16), index=True)
    thumbnail_src = Column(Text, default='')
    update_time = Column(DATETIME(), default=datetime.datetime.now())
    create_time = Column(DATETIME(), default=datetime.datetime.now())

    def __repr__(self):
        return '<InstMeiVideo %r>' % (self.id)

    def pic_url(self):
        return CDN_PREFIX + self.thumbnail_src.split('/')[-1]

    def video_url(self):
        return CDN_PREFIX + self.video_src.split('/')[-1]



class InstMeiVideoCount(Base):
    __tablename__ = 'inst_mei_video_count'
    id = Column(Integer, primary_key=True)
    inst_owner = Column(String(32), default='', index=True)
    count = Column(Integer, default=0)
    update_time = Column(DATETIME(), default=datetime.datetime.now())
    create_time = Column(DATETIME(), default=datetime.datetime.now())

    def __repr__(self):
        return '<InstMeiVideoCount %r>' % (self.id)

