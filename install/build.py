import argparse
import logging
import os
import shutil
import sys

from easy2use.command import shell

LOG_FORMAT = '%(asctime)s %(process)d %(levelname)s %(name)s:%(lineno)s ' \
             '%(message)s'
FILE_PATH = os.path.abspath(__file__)
INSTALL_DIR = os.path.dirname(FILE_PATH)

DOCKER = 'docker'
PODMAN = 'podman'

CONTAINER_CMD = None

LOG = logging.getLogger(__name__)


def main():
    global CONTAINER_CMD

    parser = argparse.ArgumentParser(description='myansi build tool')
    parser.add_argument('whl_file', help='The file of whl package')
    parser.add_argument('-r', '--push-registry', action='append', nargs='?',
                        help='The registry to push, e.g. docker.io, '
                             'registry1:5100, 125.0.0.1')
    parser.add_argument('-l', '--push-as-latest', action='store_true',
                        help='Push image to registry as latest version')
    parser.add_argument('-n', '--no-cache', action='store_true',
                        help='Force to build')
    parser.add_argument('-c', '--container-cmd', default=shell.DOCKER,
                        choices=[shell.DOCKER, shell.PODMAN],
                        help='Force to build')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='Show debug message')
    args = parser.parse_args()

    logging.basicConfig(level=args.debug and logging.DEBUG or logging.INFO,
                        format=LOG_FORMAT)

    CONTAINER_CMD = shell.get_container_impl(impl=args.container_cmd)

    whl_file_path = os.path.abspath(args.whl_file)
    LOG.info('whl file path: %s', whl_file_path)
    if not os.path.exists(whl_file_path):
        LOG.error('whl file %s is not exists', args.whl_file)
        return 1
    if not os.path.isfile(whl_file_path):
        LOG.error('invalid path %s, it must be a file')
        return 1

    whl_name = os.path.basename(whl_file_path)
    try:
        whl_version = whl_name.split('-')[1]
        LOG.debug('whl version is %s', whl_version)
    except Exception as e:
        LOG.error(e)
        return 1

    target = f'myansi:{whl_version}'
    shutil.copy(whl_file_path, INSTALL_DIR)
    requirements = 'requirements.txt'

    shutil.copy(requirements, INSTALL_DIR)

    os.chdir(INSTALL_DIR)
    LOG.info('change dir to %s', os.getcwd())

    if not os.path.exists(whl_name):
        LOG.error('file %s not exists', whl_name)
        return 1
    try:
        CONTAINER_CMD.build('./', network='host', target=target,
                            no_cache=args.no_cache,
                            build_args=[f'PACKAGE_NAME={whl_name}'])
        LOG.info('image build success')
    except Exception:
        LOG.exception('build failed!')
        return
    finally:
        for file in [os.path.join(INSTALL_DIR, requirements), whl_name]:
            if os.path.exists(file):
                LOG.debug('clean file %s', file)
                os.remove(file)

    try:
        for registry in args.push_registry or []:
            CONTAINER_CMD.tag_and_push(target, f'{registry}/{target}')

            if args.push_as_latest:
                CONTAINER_CMD.tag_and_push(target,
                                           f'{registry}/myansi:latest')

    except Exception as e:
        LOG.error('tag/push failed! %s', e)
        return 1

    LOG.info('myansi build completed.')


if __name__ == '__main__':
    sys.exit(main())
