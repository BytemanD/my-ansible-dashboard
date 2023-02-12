import enum
import os
import logging

from xmlrpc.client import boolean
from requests import session

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Enum

from easy2use.common import customconfig

LOG = logging.getLogger(__name__)

TABLE_NAME = 'configs'
DB_FILE = None
SESSION = None

Base = declarative_base()


class BaseModel(object):

    def to_dict(self):
        data = {}
        for c in self.__table__.columns:
            data[c.name] = getattr(self, c.name)
            if isinstance(data[c.name], enum.Enum):
                data[c.name] = data[c.name].name
        return data


class Types(enum.Enum):
    STR = 0
    INT = 1
    BOOL = 2


class Config(Base, BaseModel):
    __tablename__ = TABLE_NAME

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(32), nullable=False)
    default = Column(String(32), nullable=True)
    value = Column(String(32), nullable=True)
    description = Column(String(32), nullable=True)
    type = Column(Enum(Types), default=Types.STR)

    def get_value(self):
        if self.type == 1:
            return int(self.value)
        elif self.type == 2:
            return boolean(self.type)
        else:
            return self.value


class DBApi(object):

    def __init__(self, items) -> None:
        for item in items:
            if self.exists(item.name):
                continue
            self.add(item)

    def add(self, item: customconfig.Item):
        if isinstance(item, customconfig.IntItem):
            item_type = Types.INT
        elif isinstance(item, customconfig.BoolItem):
            item_type = Types.BOOL
        else:
            item_type = Types.STR

        config = Config(name=item.name, default=str(item.default),
                        description=item.description,
                        type=item_type)
        SESSION.add(config)
        SESSION.commit()

    def exists(self, name):
        return SESSION.query(Config).filter_by(name=name).first() is not None

    def list(self):
        return SESSION.query(Config).all()

    def get(self, name):
        config = session.query(Config).filter_by(name=name).first()
        if not config:
            raise ValueError(f'option {name} is not exists')
        return config

    def set(self, name, value):
        config = self.get(name)
        if config.type == 1:
            value = int(value)
        elif config.type == 2:
            if not isinstance(value, bool):
                LOG.warning('value %s is not bool type')
                if isinstance(value, str):
                    value = value.lower() in ['true', '1', 'yes', 'on']
                else:
                    value = boolean(value)

        config.update({'value': value})
        SESSION.commit()

    def reset(self, name):
        config = self.get(name)
        config.update({'value': None})
        SESSION.commit()


def init(items, dbfile, engine=None, session=None, table_name=None):
    global TABLE_NAME
    global DB_FILE, ENGINE, SESSION

    DB_FILE = dbfile
    if table_name:
        TABLE_NAME = table_name

    dbfile_dir = os.path.dirname(os.path.abspath(DB_FILE))
    if not os.path.exists(dbfile_dir):
        os.makedirs(dbfile_dir)

    ENGINE = engine or create_engine('sqlite:///{}'.format(DB_FILE))
    SESSION = session or sessionmaker(bind=ENGINE)()

    Base.metadata.create_all(ENGINE, checkfirst=True)
