import os
import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session

from myansi.db import models
from myansi.common import conf

CONF = conf.CONF
LOG = logging.getLogger(__name__)
ENGINE = None
SESSION = None


def init():
    global DB_FILE, ENGINE, SESSION

    DB_FILE = os.path.join(CONF.data_path, 'myansi.db')
    ENGINE = create_engine('sqlite:///{}'.format(DB_FILE))
    SESSION = scoped_session(sessionmaker(bind=ENGINE))

    LOG.info('database file is %s', DB_FILE)
    models.Base.metadata.create_all(ENGINE, checkfirst=True)

    # dbconf.init(conf.configs_items_in_db,
    #             DB_FILE, engine=ENGINE, session=SESSION)


def create_cluster(name, auth_url, auth_project, auth_user, auth_password):
    SESSION.add(
        models.Cluster(name=name, auth_url=auth_url,
                       auth_project=auth_project, auth_user=auth_user,
                       auth_password=auth_password)
    )
    SESSION.commit()


def query_cluster():
    return SESSION.query(models.Cluster).all()


def get_cluster_by_id(cluster_id):
    return SESSION.query(models.Cluster).filter_by(id=cluster_id).first()


def get_cluster_by_name(name):
    return SESSION.query(models.Cluster).filter_by(name=name).first()


def delete_cluster_by_id(cluster_id):
    deleted = SESSION.query(models.Cluster).filter_by(id=cluster_id).delete()
    SESSION.commit()
    return deleted


# image chunk
def create_image_chunk(image_id, size):
    SESSION.add(
        models.ImageChunk(image_id=image_id, size=size, cached=0, readed=0)
    )
    SESSION.commit()


def query_image_chunk():
    return SESSION.query(models.ImageChunk).all()


def get_image_chunk_by_id(image_chunk_id):
    return SESSION.query(models.ImageChunk).filter_by(
        id=image_chunk_id).first()


def get_image_chunk_by_image_id(image_id):
    return SESSION.query(
        models.ImageChunk).filter_by(image_id=image_id).first()


def add_image_chunk_cached(image_id, cached):
    image_chunk = get_image_chunk_by_image_id(image_id)
    image_chunk.cached += cached
    SESSION.commit()


def add_image_chunk_readed(image_id, readed):
    image_chunk = get_image_chunk_by_image_id(image_id)
    image_chunk.readed += readed
    SESSION.commit()


def delete_image_chunk(image_chunk_id):
    deleted = SESSION.query(
        models.ImageChunk).filter_by(id=image_chunk_id).delete()
    SESSION.commit()
    return deleted
