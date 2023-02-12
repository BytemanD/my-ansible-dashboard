import os
import socket
import logging

from easy2use.globals import cfg

LOG = logging.getLogger(__name__)

CONF = cfg.CONF
DEFAULT_HOST = socket.gethostname()


default_options = [
    cfg.BooleanOption('debug', default=False),
    cfg.Option('log_file', default=None),
    cfg.IntOption('port', default=80),
    cfg.IntOption('workers', default=None),
    cfg.Option('data_path', default='/etc/myansi'),
    cfg.Option('inventory', default='/etc/myansi/hosts')
]


def load_configs():
    for file in ['/etc/myansi/myansi.conf',
                 os.path.join('etc', 'myansi.conf')]:
        if not os.path.exists(file):
            continue
        LOG.info('Load config file from %s', file)
        CONF.load(file)
        break
    else:
        LOG.warning('config file not found')


CONF.register_opts(default_options)
