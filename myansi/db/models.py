
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String


Base = declarative_base()


class BaseModel(object):

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Cluster(Base, BaseModel):
    __tablename__ = 'cluster'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(20))
    auth_url = Column(String(20))
    auth_project = Column(String(32))
    auth_user = Column(String(32))
    auth_password = Column(String(32))


class ImageChunk(Base, BaseModel):
    __tablename__ = 'image_chunk'

    id = Column(Integer, primary_key=True, autoincrement=True)
    image_id = Column(String(36))
    size = Column(Integer)
    cached = Column(Integer, default=0)
    readed = Column(Integer, default=0)
