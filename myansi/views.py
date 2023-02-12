import json
import logging

from tornado import web

from myansi.common import conf
from myansi.common import context
from myansi.common import utils
from myansi.common import player
from myansi.db import api

LOG = logging.getLogger(__name__)
CONF = conf.CONF

CONF_DB_API = None

UPLOADING_IMAGES = {}
UPLOADING_THREADS = {}

RUN_AS_CONTAINER = False


class Index(web.RequestHandler):

    def get(self):
        self.redirect('/dashboard')


class BaseReqHandler(web.RequestHandler):

    def _get_context(self):
        return context.ClusterContext(self.get_cookie('clusterId'),
                                      region=self.get_cookie('region'))


class Dashboard(BaseReqHandler):

    def get(self):
        self.render('dashboard.html', name='MyAnsi', cluster='')


class Command(BaseReqHandler):

    def post(self):
        manager = player.MyAnsi()
        body = json.loads(self.request.body)
        host = body.get('host')
        cmd = body.get('cmd')
        result = manager.run(host, cmd)
        self.set_status(200)
        self.finish({'result': result.to_dict()})


class Configs(web.RequestHandler):

    def get(self):
        global CONF_DB_API

        self.set_status(200)
        self.finish({'configs': [
            item.to_dict() for item in CONF_DB_API.list()]
        })


class Cluster(web.RequestHandler):

    def get(self):
        cluster_list = api.query_cluster()
        self.set_status(200)
        self.finish({
            'clusters': [cluster.to_dict() for cluster in cluster_list]
        })

    def post(self):
        data = json.loads(self.request.body)
        cluster = data.get('cluster', {})
        LOG.debug('add cluster: %s', data)
        try:
            api.create_cluster(cluster.get('name'), cluster.get('authUrl'),
                               cluster.get('authProject'),
                               cluster.get('authUser'),
                               cluster.get('authPassword'))
            self.set_status(200)
            self.finish(json.dumps({}))
        except Exception as e:
            LOG.exception(e)
            self.set_status(400)
            self.finish({'error': str(e)})

    def delete(self, cluster_id):
        deleted = api.delete_cluster_by_id(cluster_id)
        if deleted >= 1:
            self.set_status(204)
            self.finish()
        else:
            self.set_status(404)
            self.finish({'error': f'cluster {cluster_id} is not found'})
        return


class Tasks(web.RequestHandler):

    def _get_uploading_tasks(self):
        uploading_tasks = []
        for image_chunk in api.query_image_chunk():
            data = {'id': image_chunk.id,
                    'image_id': image_chunk.image_id, 'size': image_chunk.size,
                    'cached': image_chunk.cached * 100 / image_chunk.size,
                    'readed': image_chunk.readed * 100 / image_chunk.size}
            uploading_tasks.append(data)
        return uploading_tasks

    def get(self):
        global UPLOADING_IMAGES
        tasks = {}
        try:
            tasks['uploading'] = self._get_uploading_tasks()
            self.set_status(201)
            self.finish({'tasks': tasks})
        except Exception as e:
            self.set_status(400)
            self.finish({'error': str(e)})

    def delete(self, task_id):
        try:
            api.delete_image_chunk(task_id)
            self.set_status(204)
            self.finish()
        except Exception:
            LOG.exception('delete image chunk %s faield', task_id)
            self.set_status(400)
            self.finish()


class Actions(web.RequestHandler):

    def check_update(self):
        global RUN_AS_CONTAINER

        if RUN_AS_CONTAINER:
            LOG.info('Check latest image version')
            last_version = utils.check_last_image_version()
        else:
            LOG.info('Check latest wheel version')
            last_version = utils.check_last_version()
        self.set_status(200)
        self.finish({'checkLastVersion': last_version or {}})

    def post(self):
        data = json.loads(self.request.body)
        LOG.debug('action body: %s', data)
        if 'checkLastVersion' in data:
            self.check_update()


def get_routes():
    return [
        (r'/', Index),
        (r'/dashboard', Dashboard),
        (r'/command', Command),
        (r'/configs', Configs),
        (r'/cluster', Cluster),
        (r'/cluster/(.*)', Cluster),
        (r'/tasks', Tasks),
        (r'/tasks/(.*)', Tasks),
        (r'/actions', Actions),
    ]
