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

import git, time
commits = git.Repo().heads.Interactions.log()
ver_msg = commits[-1].message
__version__ = f"4.{len(commits)}"
ver_date = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(commits[-1].time[0]))


from mdiscord import *
class Bot(Client):
    pass
from .database.database import Database
from .database.cache import Cache
from .utils.utils import log # noqa: F401

from typing import Dict

class Bot(Client):
    user_id: Snowflake = None
    session_id: str = None
    start_time: float = None

    db: Database
    cache: Dict[Snowflake, Cache]

from .commands.interactions import register, Groups, Event # noqa: F401
