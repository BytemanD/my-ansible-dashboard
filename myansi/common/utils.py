import re
from pbr import version
import queue
import logging

import requests

from easy2use.common import pkg

from myansi.common import constants
from myansi.common.i18n import _
from myansi.db import api

LOG = logging.getLogger(__name__)


def get_version():
    info = version.VersionInfo(constants.NAME)
    return info.release_string()


def check_last_version():
    try:
        releases = requests.get(constants.RELEASES_API).json()
    except Exception as e:
        LOG.error('Check releases failed, %s', e)
        return

    if not releases:
        LOG.info('No release found.')
        return
    current_version = get_version()
    LOG.debug(_('Current version is: %s'), current_version)
    latest = releases[0]
    LOG.debug(_('Latest release version: %s'), latest.get('tag_name'))

    v1 = pkg.PackageVersion(current_version)
    v2 = pkg.PackageVersion(latest.get('tag_name'))
    if v1 >= v2:
        return
    asset = latest.get('assets')[0] if latest.get('assets') else None
    if not asset:
        LOG.error('assets not found')
        return
    download_url = asset.get("browser_download_url")
    return {'version': '.'.join(v2.version), 'download_url': download_url}


def check_last_image_version():
    try:
        tags = requests.get(constants.IMAGE_TAGS_API).json().get('results')
    except Exception as e:
        LOG.error('get tags failed, %s', e)
        return

    if not tags:
        LOG.info('no repository tags found.')
        return
    current_version = get_version()
    LOG.debug(_('Current version is: %s'), current_version)

    v1 = pkg.PackageVersion(current_version)

    latest_version = v1
    for tag in tags:
        if tag.get('name') == 'latest':
            continue
        v2 = pkg.PackageVersion(tag.get('name'))
        if v2 > latest_version:
            latest_version = v2

    if latest_version > v1:
        version_string = '.'.join(latest_version.version)
        return {
            'version': version_string,
            'pull_url': f'fjboy/{constants.NAME}:${version_string}'
        }


class ImageChunk(object):

    def __init__(self, url, size):
        matched = re.match(r'/(.*)/images/(.*)/file', url)
        self.size = int(size)
        self.chunks = queue.Queue()
        self.image_id = matched.group(2)
        api.create_image_chunk(self.image_id, self.size)

    def add(self, chunk, size):
        self.chunks.put((chunk, int(size)))
        LOG.info('chunk cached: + %.2f', self.size)

    def read(self, *args, **kwargs):
        if self.chunks.empty() and self.all_cached():
            return None
        chunk = self.chunks.get()
        LOG.info('read chunk, empty: %s all cached: %s',
                 self.chunks.empty(), self.all_cached())

        api.add_image_chunk_readed(self.image_id, chunk[1])
        return chunk[0]

    def all_cached(self):
        image_chunk = api.get_image_chunk_by_image_id(self.image_id)
        return image_chunk.cached >= self.size

    def __len__(self):
        return self.size
