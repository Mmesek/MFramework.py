from mdiscord import *

from .database.database import Database
from .database.cache import Cache
from typing import Dict

class Bot(Client):
    session_id: str = None
    start_time: float = None
    application: Application = None
    registered: bool = False

    alias: str = "?"
    emoji: dict = dict
    primary_guild: Snowflake = 463433273620824104

    db: Database
    cache: Dict[Snowflake, Cache]
    def __init__(self, name: str, cfg: dict, db: Database=None, cache: Cache=None, shard: int=0, total_shards: int=1):
        self.db = db
        self.cache = cache
        self.alias = cfg[name].get('alias', '?')
        self.emoji = cfg["Emoji"]
        self.primary_guild = cfg[name].get('primary_guild', 463433273620824104)

        super().__init__(name, cfg, shard=shard, total_shards=total_shards)
    async def dispatch(self, data: Gateway_Payload):
        await super().dispatch(data)
        if hasattr(data.d, 'guild_id') or isinstance(data.d, Guild):
            id = data.d.guild_id if hasattr(data.d, 'guild_id') else data.d.id
            if id in self.cache:
                await self.cache[id].logging[data.t.lower()](data.d)
