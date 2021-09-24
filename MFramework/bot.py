from typing import Dict

from mdiscord import Snowflake, Application, Client, Gateway_Payload, Guild

from MFramework.database.cache import Cache
from MFramework.database.database import Database
from MFramework.context import Context

class Bot(Client):
    session_id: str = None
    start_time: float = None
    application: Application = None
    registered_commands = None
    registered: bool = False

    alias: str = "?"
    emoji: dict = dict
    primary_guild: Snowflake = 463433273620824104

    db: Database
    cache: Dict[Snowflake, Cache]

    _Cache: Cache = Cache
    _Context: Context = Context
    def __init__(self, name: str, cfg: dict, db: Database=None, cache: Cache=None, shard: int=0, total_shards: int=1):
        self.db = db
        self.cache = cache
        self.alias = cfg.get(name, {}).get('alias', '?')
        self.emoji = cfg.get('Emoji', {})
        self.primary_guild = cfg.get(name, {}).get('primary_guild', 463433273620824104)

        super().__init__(name, cfg, shard=shard, total_shards=total_shards)
    async def dispatch(self, data: Gateway_Payload):
        await super().dispatch(data)
        if hasattr(data.d, 'guild_id') or isinstance(data.d, Guild):
            id = data.d.guild_id if hasattr(data.d, 'guild_id') else data.d.id
            if id and id in self.cache:
                await self.cache[id].logging[data.t.lower()](data.d)
