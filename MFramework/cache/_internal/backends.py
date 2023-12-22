from datetime import timedelta
from typing import Any

import orjson
import redis.asyncio as redis

from mdiscord import DiscordObject, as_dict


class Dictionary(dict):
    def __init__(self, **kwargs):
        super().__init__()

    async def add(self, name: str, value: str, expire_time: timedelta = None) -> str:
        """Add new item to a cache"""
        # from datetime import datetime
        # expire = datetime.now() + expire_time
        self[name] = value

    async def get(self, name: str) -> str:
        """Get item from a cache"""
        return super().get(name, None)

    def update(self, name: str, new_value: str) -> str:
        """Update current value in cache, return old value"""
        old_value = self.get(name)
        self[name] = new_value
        return old_value

    def delete(self, name: str) -> str:
        """Delete item from cache"""
        return self.pop(name, None)

    def save(self) -> bool:
        return False

    def shutdown(self) -> None:
        return False

    async def db_size(self) -> int:
        return await len(self)

    def has(self, name) -> bool:
        return name in self

    def exists(self, name) -> bool:
        return name in self

    async def __contains__(self, __key: object) -> bool:
        return super().__contains__(__key)
    
    async def __anext__(self):
        return super().__next__()
    
    async def __aiter__(self):
        return self.__iter__()
    
    async def __len__(self) -> int:
        return super().__len__()

    def __len__(self) -> int:
        return super().__len__()
    
    def count(self, name) -> int:
        return len(self.keys(name))

    def keys(self, pattern=None) -> list[Any]:
        if pattern:
            import re

            p = re.compile(pattern)
            return list(filter(lambda x: p.search(x), self))
        return super().keys()


class Redis(redis.Redis):
    def _to_dict(self, value: str) -> dict:
        if type(value) is bytes:
            value = orjson.loads(value)
        return value

    def _from_dict(self, value: dict | Any) -> str:
        if isinstance(value, DiscordObject):
            value = as_dict(value)
        if type(value) is dict:
            value = orjson.dumps(value)
        return value

    async def add(self, name: str, value: str, expire_time: timedelta = None) -> str:
        value = self._from_dict(value)
        return await self.set(name, value, ex=expire_time)

    async def get(self, name: str) -> str:
        r = await super().get(name)
        return self._to_dict(r)

    async def update(self, name: str, new_value: str) -> str:
        new_value = self._from_dict(new_value)
        r = await self.getset(name, new_value)
        return self._to_dict(r)

    async def db_size(self) -> int:
        return await self.dbsize()

    async def has(self, name: str) -> bool:
        return True if await self.exists(name) else False

    async def count(self, name: str) -> bool:
        return await self.exists(name)
