from typing import List, Union
from datetime import timedelta

from mdiscord import *

from .backends import Redis, Dictionary

class Collection:
    '''Base Collection. 
    
    Default ID is composed from Class name and `.id` attribute of cached object'''
    _cache: Redis
    _expire: timedelta = None
    _cls: str
    def __init__(self, cache: Union[Dictionary, Redis]=None) -> None:
        self._cache = cache or Dictionary()
    #Dictionary-like usage
    def __setitem__(self, key, value):
        self._cache.add(self._combine(key), value, self._expire)
    def __len__(self) -> int:
        return self._cache.db_size()
    def __delitem__(self, key):
        self._cache.delete(self._create_id(key))
    def items(self):
        if type(self._cache) is Dictionary:
            return self._cache.items()
        return {}
    def keys(self):
        return self._cache.keys()
    def values(self):
        if type(self._cache) is Dictionary:
            return self._cache.values()
        return iter({})
    def __iter__(self):
        if type(self._cache) is Dictionary:
            return iter(self._cache)
        return iter({})
    def update(self, obj: DiscordObject):
        '''Update current object(s) in cache'''
        if type(obj) is list:
            for i in obj:
                self.update(i)
            return
        return self._cache.update(self._create_id(obj), obj)
    def pop(self, *args, default=None):
        return self._cache.delete(*args) or default
    def __contains__(self, o: object) -> bool:
        return self._cache.has(o)
    def __getitem__(self, id: Snowflake) -> str:
        r = self._cache.get(self._combine(id))
        if type(r) is dict:
            return self._cls(**r)
        return r
    def get(self, id: Snowflake, default=None):
        return self._cache.get(self._combine(id)) or default
    #Internal
    def _create_id(self, obj: DiscordObject) -> str:
        '''Creates ID by combining object ID with class's name'''
        if type(self._cache) is Dictionary:
            return obj.id
        return self._combine(obj.id)
    def _combine(self, *args) -> str:
        '''Combines args with class's name into a dotted key'''
        if type(self._cache) is Dictionary:
            return args[-1]
        return ".".join([self.__class__.__name__]+[str(i) for i in args])
    #External API
    def from_list(self, iterable: List[DiscordObject], guild_id=None) -> None:
        '''Fill cache from list'''
        for i in iterable:
            if guild_id:
                i.guild_id = guild_id
            self.store(i)
        return self
    def store(self, obj: DiscordObject):
        '''Store a single item'''
        self._cache.add(self._create_id(obj), obj, expire_time=self._expire)
    def has(self, name: str) -> bool:
        '''Check if provided key exisits in cache'''
        return True if self._cache.exists(self._combine(name)) else False
    def delete(self, obj_id: DiscordObject):
        '''Delete from Cache'''
        return self._cache.delete(self._combine(obj_id))

class Messages(Collection):
    _expire: timedelta = timedelta(days=1)
    _cls: Message = Message
    def _create_id(self, obj: Message) -> str:
        return self._combine(obj.guild_id, obj.channel_id, obj.id)
    def has(self, guild_id, channel_id, message_id):
        return self._cache.has(self._combine(guild_id, channel_id, message_id))
    def last(self, guild_id, channel_id):
        all = self._cache.scan(cursor=0, match=self._combine(guild_id, channel_id)+".*")
        all[1].sort()
        try:
            r = self._cache.get(all[1][-1])
        except:
            return None
        if type(r) is dict:
            return self._cls(**r)
        return r
    def size(self, guild_id, channel_id):
        return self._cache.keys(self._combine(guild_id, channel_id, '*'))

class Channels(Collection):
    _cls: Channel = Channel
    def _create_id(self, obj: Channel) -> str:
        return self._combine(obj.guild_id, obj.id)

class Roles(Collection):
    _cls: Role = Role

class Users(Collection):
    _cls: User = User

class Members(Collection):
    _cls: Guild_Member = Guild_Member
    def _create_id(self, obj: Guild_Member) -> str:
        return self._combine(obj.user.id)
    def size(self, guild_id):
        return self._cache.keys(self._combine(guild_id, '*'))

class Presences(Collection):
    _cls = tuple
    def _create_id(self, obj: Presence_Update) -> str:
        return self._combine(obj.user.id)
    def store(self, data: Presence_Update):
        self._cache.add(data.user.id, (data.activities[0].name, data.activities[0].created_at, data.activities[0].application_id), expire_time=self._expire)

class Guilds(Collection):
    _cls: Guild = Guild

class Cooldowns(Collection):
    def _create_id(self, guild_id: Snowflake, user_id: Snowflake, type: str) -> str:
        return self._combine(guild_id, user_id, type)
    def get(self, guild_id: Snowflake, user_id: Snowflake, type: str):
        r = self._cache.get(self._combine(guild_id, user_id, type))
        from datetime import timezone
        return datetime.fromtimestamp(r, tz=timezone.utc) if r else None
    def has(self, guild_id, user_id, type):
        return self._cache.has(self._combine(guild_id, user_id, type))
    def store(self, guild_id, user_id, type, expire=timedelta(seconds=60)):
        from datetime import timezone
        return self._cache.add(self._create_id(guild_id, user_id, type), datetime.now(tz=timezone.utc).timestamp(), expire_time=expire)

class Context(Collection):
    _expire: timedelta = timedelta(minutes=10)
    def _create_id(self, guild_id: Snowflake, channel_id: Snowflake, user_id: Snowflake) -> str:
        return self._combine(guild_id, channel_id, user_id)