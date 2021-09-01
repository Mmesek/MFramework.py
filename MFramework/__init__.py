# -*- coding: utf-8 -*-
'''
MFramework
----------

Discord API framework with Database support.

:copyright: (c) 2020-2021 Mmesek

'''
__name__ = "MFramework"
__version__ = "4.0"
__package__ = "MFramework"
__module__ = "MFramework"

import i18n
i18n.load_path.append("././locale")
#i18n.set('filename_format', '{locale}.{format}')
i18n.set('filename_format','{namespace}.{format}')
i18n.set('skip_locale_root_data', True)
i18n.set('file_format', 'json')

try:
    import git, time
    commits = git.Repo().heads.Interactions.log()
    ver_msg = commits[-1].message
    __version__ = f"4.{len(commits)}"
    ver_date = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(commits[-1].time[0]))
except:
    pass

import logging
from mlib import logger
log = logging.getLogger("MFramework")
log.setLevel(logger.log_level)

from mdiscord import * # noqa: F401

from .bot import * # noqa: F401
from .commands import * # noqa: F401
from .commands import commands, interactions, parser # noqa: F401