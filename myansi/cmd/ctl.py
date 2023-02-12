import logging
import mimetypes
import os
import shutil
import sys
import subprocess

import bs4
import requests
from urllib import parse
from jinja2 import PackageLoader, Environment

from easy2use.downloader.urllib import driver
from easy2use.globals import cli
from easy2use.globals import log
from easy2use.system import OS
from easy2use import system
from easy2use.web import application

from myansi.common import conf
from myansi.common import constants
from myansi.common import exceptions
from myansi.common import player
from myansi.common import utils
from myansi.common.i18n import _
from myansi import views
from myansi.db import api as db_api
# from myansi.common import dbconf


LOG = logging.getLogger(__name__)
CONF = conf.CONF

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def download_statics_for_cdn():

    LOG.info('Check cdn static files')
    LOG.info('========================')
    env = Environment(loader=PackageLoader('myansi', 'templates'))
    template = env.get_template('requires.html')
    html = template.render(cdn=constants.CDN)
    links = []
    bs_html = bs4.BeautifulSoup(html, features="html.parser")
    for script in bs_html.find_all(name='script'):
        src = script.get('src')
        if not src or not src.startswith('http') or not src.endswith('.js'):
            continue
        links.extend((src, '{}.map'.format(src)))

    for script in bs_html.find_all(name='link'):
        src = script.get('href')
        if not src or not src.startswith('http'):
            continue
        if src.endswith('.css'):
            links.extend((src, '{}.map'.format(src)))
    for link in links:
        save_static_content(link)
    LOG.info('========================')


def save_static_content(link):
    home = os.path.abspath(os.path.dirname(os.path.pardir))
    url = parse.urlparse(link)
    local_path = os.path.join(home, 'static', 'cdn', url.path[1:])
    if os.path.exists(local_path):
        LOG.info('file exists: %s', local_path)
        return

    save_path = os.path.dirname(local_path)
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    LOG.info('Download cdn src %s to %s', link, os.path.abspath(local_path))
    resp = requests.get(link)
    try:
        resp.raise_for_status()
    except requests.exceptions.HTTPError:
        if resp.status_code == 404 and link.endswith('.map'):
            LOG.warning('%s not found, mybe it is no need.', link)
            return

    with open(local_path, 'w') as f:
        data = resp.text if isinstance(resp.content, bytes) else resp.content
        f.write(data)


class Version(cli.SubCli):
    NAME = 'version'

    def __call__(self, args):
        print(utils.get_version())


class Upgrade(cli.SubCli):
    NAME = 'upgrade'
    ARGUMENTS = [
        cli.Arg('-d', '--debug', action='store_true',
                help=_('Show debug message')),
        cli.Arg('-y', '--yes', action='store_true',
                help=_('answer yes for all questions')),
        cli.Arg('-c', '--cache', action='store_true',
                help=_('use cache if it is downloaded')),
        cli.Arg('--image', action='store_true',
                help=_('Check image version')),
    ]

    def __call__(self, args):
        if args.image:
            last_version = self.upgrade_from_image()
            return
        last_version = utils.check_last_version()
        if not last_version:
            print(_('The current version is the latest.'))
            return

        version = last_version.get('version')
        download_url = last_version.get('download_url')
        msg = f'\nA new {constants.NAME} release is available: ' \
              f'{version}\n' \
              f'Upgrade from:\n    {download_url}\n'
        print(msg)

        if not args.yes:
            while True:
                input_str = input(r'Upgrade now ? [y/n] ')
                if input_str == 'y':
                    break
                elif input_str == 'n':
                    return
                else:
                    print('Error, invalid input, must be y or n.')

        file_path = self.download(download_url, cache=args.cache)
        try:
            self.pip_install(file_path)
        except Exception as e:
            LOG.error('Install failed, error: %s', e)
            return
        print(_('Install success.'))
        print(_('Please execute the command below to restart myansi:'))
        print('    systemctl restart myansi')

    def upgrade_from_image(self):
        latest_version = utils.check_last_image_version()
        if not latest_version:
            print(_('The current version is the latest.'))
            return

        msg = f'{_("A new image is available:")} ' \
              f'{latest_version.get("version")}'
        print('\n' + msg + '\n')

    def pip_install(self, file_path, force=False):
        install_cmd = ['pip3', 'install', file_path]
        if force:
            install_cmd.append('--force-reinstall')
        LOG.info(_('start to install %s'), ' '.join(install_cmd))
        status, output = subprocess.getstatusoutput(' '.join(install_cmd))
        if status != 0:
            LOG.error(_('Install Output: %s'), output)
            raise exceptions.PipInstallFailed(package=file_path,
                                              cmd=' '.join(install_cmd))

    def download(self, url, cache=False):
        file_path = os.path.basename(url)
        tmp_dir = OS.is_windows() and os.getenv('TMP') or '/tmp'
        cached_file = os.path.join(tmp_dir, '/tmp')
        if cache and os.path.exists(cached_file):
            LOG.warning('use cache: %s', cached_file)
            return cached_file

        downloader = driver.Urllib3Driver(progress=True,
                                          cached_file=tmp_dir)
        LOG.info(_('download from %s'), url)
        downloader.download(url)
        LOG.info(_('download success'))
        return file_path


class MyAnsiApp(application.TornadoApp):

    def start(self, **kwargs):
        LOG.info('Init ...')
        hosts = os.path.join(CONF.data_path, 'hosts')

        if not os.path.exists(hosts):
            if os.path.exists(constants.ANSIBLE_HOSTS):
                shutil.copyfile(constants.ANSIBLE_HOSTS, hosts)
            else:
                with open(hosts) as f:
                    f.write('# Created by myansi')

        LOG.info('Staring server ...')
        db_api.init()
        # views.CONF_DB_API = dbconf.DBApi(conf.configs_itesm_in_db)
        super().start(**kwargs)


class Serve(cli.SubCli):
    NAME = 'serve'
    ARGUMENTS = log.get_args() + [
        cli.Arg('-p', '--port', type=int,
                help=_("Run serve with specified port")),
        cli.Arg('--develop', action='store_true',
                help=_("Run serve with develop mode")),
        cli.Arg('--container', action='store_true',
                help=_("Run serve with docker container")),
    ]

    def __call__(self, args):
        views.RUN_AS_CONTAINER = args.container
        if system.OS.is_windows():
            # NOTE(fjboy) For windows host, MIME type of .js file is
            # 'text/plain', so add this type before start http server.
            mimetypes.add_type('application/javascript', '.js')

        conf.load_configs()
        player.init()

        template_path = os.path.join(ROOT, 'templates')
        static_path = os.path.join(ROOT, 'static')
        app = MyAnsiApp(views.get_routes(), develop=args.develop,
                        template_path=template_path, static_path=static_path)
        app.start(port=args.port or CONF.port,
                  num_processes=CONF.workers)


def main():
    cli_parser = cli.SubCliParser(_('MyAnsi Command Line'),
                                  title=_('Subcommands'))
    cli_parser.register_clis(Version, Upgrade, Serve)
    cli_parser.call()


if __name__ == '__main__':
    sys.exit(main())
