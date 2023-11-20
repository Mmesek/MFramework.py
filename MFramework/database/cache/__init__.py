from typing import Optional

from MFramework import Guild
from MFramework.database.cache_internal import models as collections

from . import base, guild


class Cache(
    guild.BotMeta,
    base.Commands,
):
    pass
