# -*- coding: UTF-8 -*-
import os
import gettext
import locale
import logging

LOG = logging.getLogger(__name__)


def get_translater():
    project_name = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    locale_path = os.path.join(project_name, 'locale')
    locale_language = locale.getdefaultlocale()[0]
    LOG.debug('locale language: %s', locale_language)
    try:
        return gettext.translation('myansi', locale_path,
                                   [locale_language, "en_US"]).gettext
    except FileNotFoundError:
        return gettext.gettext


_ = get_translater()
