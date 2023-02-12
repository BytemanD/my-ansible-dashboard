from distutils.command import install
import shutil
import os

from easy2use import fs
from easy2use.common import msgfmt


myansi = 'myansi'
I18N_DIR = 'i18n'


def _copy_vsm(static_path):
    # Copy vuetify-snackbar-message.js
    include_vsm = os.path.join('include', 'vuetify-snackbar-message.js')
    build_static_include = os.path.join(static_path, 'include')
    build_static_include_vsm = os.path.join(build_static_include,
                                            os.path.basename(include_vsm))
    if not os.path.exists(build_static_include):
        os.makedirs(build_static_include)
    if os.path.exists(build_static_include_vsm):
        fs.remove(build_static_include_vsm)
    shutil.copyfile(include_vsm, build_static_include_vsm)


def _copy_and_unzip_cdn(static_path):
    # Copy and unzip cdn.zip
    include_cdn_zip = os.path.join('include', 'cdn.zip')
    build_static_cdn_zip = os.path.join(static_path, 'include',
                                        os.path.basename(include_cdn_zip))
    build_static_cdn = os.path.join(static_path, 'include', 'cdn')

    if os.path.exists(build_static_cdn_zip):
        os.remove(build_static_cdn_zip)
    shutil.copyfile(include_cdn_zip, build_static_cdn_zip)

    if os.path.exists(build_static_cdn):
        fs.remove(build_static_cdn, recursive=True)
    fs.unzip(build_static_cdn_zip)
    fs.remove(build_static_cdn_zip)


def setup_hook(config):
    # Tell distutils not to put the data_files in platform-specific
    # installation locations.
    # Refer to the instructions in the openstack/horizon project
    for scheme in install.INSTALL_SCHEMES.values():
        scheme['data'] = scheme['purelib']

    static_path = os.path.join('myansi', 'static')
    _copy_and_unzip_cdn(static_path)
    _copy_vsm(static_path)

    msgfmt.make_i18n(myansi, I18N_DIR)
