from datetime import timedelta
from typing import List, Any, Dict
import redis

class Dictionary(Dict):
    def __init__(self, **kwargs):
        super().__init__()
    def add(self, name: str, value: str, expire_time: timedelta = None) -> str:
        '''Add new item to a cache'''
        #from datetime import datetime
        #expire = datetime.now() + expire_time
        self[name] = value
    def get(self, name: str) -> str:
        '''Get item from a cache'''
        return super().get(name, None)
    def update(self, name: str, new_value: str) -> str:
        '''Update current value in cache, return old value'''
        old_value = self.get(name)
        self[name] = new_value
        return old_value
    def delete(self, name: str) -> str:
        '''Delete item from cache'''
        return self.pop(name, None)
    def save(self) -> bool:
        return False
    def shutdown(self) -> None:
        return False
    def db_size(self) -> int:
        return len(self)
    def has(self, name) -> bool:
        return name in self
    def count(self, name) -> int:
        return len(self.keys(name))
    def keys(self, pattern=None) -> List[Any]:
        if pattern:
            import re
            p = re.compile(pattern)
            return list(filter(lambda x: p.search(x), self))
        return super().keys()

class Redis(redis.Redis):
    def _to_dict(self, value):
        if type(value) is bytes:
            import ujson
            value = ujson.loads(value)
        return value
    def _from_dict(self, value):
        from mdiscord import as_dict, DiscordObject
        if isinstance(value, DiscordObject):
            value = as_dict(value)
        if type(value) is dict:
            import ujson
            value = ujson.dumps(value)
        return value
    def add(self, name: str, value: str, expire_time: timedelta = None) -> str:
        value = self._from_dict(value)
        return self.set(name, value, ex=expire_time)
    def get(self, name: str) -> str:
        r = super().get(name)
        return self._to_dict(r)
    def update(self, name: str, new_value: str) -> str:
        new_value = self._from_dict(new_value)
        r = self.getset(name, new_value)
        return self._to_dict(r)
    def db_size(self):
        return self.dbsize()
    def has(self, name):
        return True if self.exists(name) else False
    def count(self, name):
        return self.exists(name)
