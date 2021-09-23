from typing import Optional

from MFramework import Guild
from MFramework.database.cache_internal import models as collections

from . import base, database, guild, logging, settings

class Cache(settings.Settings, settings.Roles, database.Tasks, logging.Logging, guild.ObjectCollections, base.Commands):
    def __init__(self, bot, guild: Guild, rds: Optional[collections.Redis] = None):
        super().__init__(bot=bot, guild=guild, rds=rds)
