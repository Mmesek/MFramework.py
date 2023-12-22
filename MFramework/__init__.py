# -*- coding: utf-8 -*-
"""
MFramework
----------

Discord API framework with Database support.

:copyright: (c) 2020-2023 Mmesek

"""
__name__ = "MFramework"
__version__ = "5.0"
__package__ = "MFramework"
__module__ = "MFramework"

try:
    import time

    import git

    last_commit = git.Repo().remotes.origin.repo.head.commit
    ver_msg = last_commit.message
    __version__ = f"5.{last_commit.count()}"
    ver_date = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(last_commit.committed_date))
except:
    ver_date = None
    pass

import logging

from mlib import logger

log = logging.getLogger("MFramework")
log.setLevel(logger.log_level)

from mdiscord import *  # noqa: F401

from .bot import *  # noqa: F401
from .commands import *  # noqa: F401
from .commands import interactions, parser, runner  # noqa: F401


class Priority(Enum):
    Commands = 5
    """High priority. Command Function, execute ASAP"""
    Filters = 10
    """Content Filtering, payload might become invalid afterwards"""
    Parsers = 50
    """Parsing functions, there might be something in content"""
    Default = 100
    """Medium priority, execution doesn't matter"""
    Activity = 150
    """Execute only if previous steps didn't stop iteration, rewards etc"""
    Logging = 200
    """Low priority, execution doesn't matter if previous steps stopped"""
    Low = 300
    """Optional execution"""
    High = Commands
    Medium = Default
