from mdiscord import *

from typing import Dict, List

class Cache(Dict):
    def store(self, obj: DiscordObject) -> None:
        self[obj.id] = obj
    def from_list(self, iterable: List[DiscordObject], guild_id=None) -> None:
        for i in iterable:
            if guild_id:
                i.guild_id = guild_id
            self.store(i)
        return self
    def __getitem__(self, k: Snowflake) -> DiscordObject:
        return super().__getitem__(k)
    def __contains__(self, o: object) -> bool:
        return super().__contains__(o)

from .rediscache import RDS
from datetime import timedelta
class RedisCache(Cache):
    _redis: RDS
    _expire: timedelta = None
    _cls: str
    def __init__(self, redis: RDS):
        self._redis = redis
    def _create_id(self, obj: DiscordObject) -> str:
        return self._combine(obj.id)#obj.id
    def _combine(self, *args):
        return ".".join([self.__class__.__name__]+[str(i) for i in args])

    def store(self, obj: DiscordObject):
        self._redis.add(self._create_id(obj), as_dict(obj), expire_time=self._expire)
    def __getitem__(self, id: Snowflake) -> str:
        r = self._redis.get(self._combine(id))
        if type(r) is dict:
            return self._cls(**r)
        return r
    def has(self, name):
        return self._redis.has(self._combine(name))
    def update(self, obj: DiscordObject):
        if type(obj) is list:
            for i in obj:
                return self.update(i)
        return self._redis.update(self._create_id(obj), as_dict(obj))
    def delete(self, obj_id: DiscordObject):
        return self._redis.delete(self._combine(obj_id))