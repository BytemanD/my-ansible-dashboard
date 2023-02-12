from myansi.db import api


class ClusterContext(object):

    def __init__(self, cluster_id, region=None):
        self.cluster_id = cluster_id
        self.region = region
        self._cluster = None

    @property
    def cluster(self):
        if not self._cluster:
            self._cluster = api.get_cluster_by_id(self.cluster_id)
        return self._cluster
