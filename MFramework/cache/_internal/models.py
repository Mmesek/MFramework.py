from datetime import timedelta, timezone
from typing import Union, MutableMapping, TypeVar

from mdiscord import *

from .backends import Dictionary, Redis

KT = TypeVar("KT")
VT = TypeVar("VT")

class Collection(MutableMapping[KT, VT]):
    """Base Collection.

    Default ID is composed from Class name and `.id` attribute of cached object"""

    _cache: Redis
    _expire: timedelta = None
    _cls: str = VT

    def __init__(self, cache: Union[Dictionary, Redis] = None, value_factory: VT = None) -> None:
        self._cache = cache or Dictionary()
        if value_factory:
            self._cls = value_factory

    # Dictionary-like usage
    async def __setitem__(self, key: KT, value: VT) -> None:
        await self._cache.add(self._combine(key), value, self._expire)

    async def __len__(self) -> int:
        return await self._cache.db_size()

    async def __delitem__(self, key: KT) -> None:
        await self._cache.delete(self._create_id(key))

    def items(self) -> tuple[tuple[KT, VT]]:
        if type(self._cache) is Dictionary:
            return self._cache.items()
        return {}

    def keys(self) -> list[KT]:
        return self._cache.keys()

    def values(self):
        if type(self._cache) is Dictionary:
            return self._cache.values()
        return iter({})

    def __iter__(self):
        if type(self._cache) is Dictionary:
            return iter(self._cache)
        return iter({})
    
    async def __aiter__(self):
        if type(self._cache) is Dictionary:
            return aiter(self._cache)
        return iter({})

    async def update(self, obj: VT | list[VT]) -> str:
        """Update current object(s) in cache"""
        if type(obj) is list:
            for i in obj:
                await self.update(i)
            return
        return await self._cache.update(self._create_id(obj), obj)

    async def pop(self, *args, default: Any=None) -> int | Any:
        return await self._cache.delete(*args) or default

    async def __contains__(self, o: VT) -> bool:
        return await self._cache.has(o)

    async def __getitem__(self, id: Snowflake) -> VT:
        r = await self._cache.get(self._combine(id))
        if type(r) is dict:
            return self._cls(**r)
        return r

    async def get(self, id: Snowflake, default=None) -> VT | Any:
        return await self._cache.get(self._combine(id)) or default

    # Internal
    def _create_id(self, obj: VT) -> str:
        """Creates ID by combining object ID with class's name"""
        if type(self._cache) is Dictionary:
            return obj.id
        return self._combine(obj.id)

    def _combine(self, *args) -> str:
        """Combines args with class's name into a dotted key"""
        if type(self._cache) is Dictionary:
            return args[-1]
        return ".".join([self.__class__.__name__] + [str(i) for i in args])

    # External API
    async def from_list(self, iterable: list[VT], guild_id: Snowflake=None) -> None:
        """Fill cache from list"""
        for i in iterable:
            if guild_id:
                i.guild_id = guild_id
            await self.store(i)
        return self

    async def store(self, obj: VT) -> None:
        """Store a single item"""
        await self._cache.add(self._create_id(obj), obj, expire_time=self._expire)

    async def has(self, name: str) -> bool:
        """Check if provided key exisits in cache"""
        return True if await self._cache.exists(self._combine(name)) else False

    async def delete(self, obj_id: VT) -> int:
        """Delete from Cache"""
        return await self._cache.delete(self._combine(obj_id))


class Messages(Collection[Snowflake, Message]):
    _expire: timedelta = timedelta(days=1)
    _cls: Message = Message

    def _create_id(self, obj: Message) -> str:
        return self._combine(obj.guild_id, obj.channel_id, obj.id)

    async def has(self, guild_id: Snowflake, channel_id: Snowflake, message_id: Snowflake) -> bool:
        return await self._cache.has(self._combine(guild_id, channel_id, message_id))

    async def last(self, guild_id: Snowflake, channel_id: Snowflake) -> VT:
        all = await self._cache.scan(cursor=0, match=self._combine(guild_id, channel_id) + ".*")
        all[1].sort()
        try:
            r = await self._cache.get(all[1][-1])
        except:
            return None
        if type(r) is dict:
            return self._cls(**r)
        return r

    async def size(self, guild_id: Snowflake, channel_id: Snowflake) -> int:
        return await self._cache.keys(self._combine(guild_id, channel_id, "*"))


class Channels(Collection[Snowflake, Channel]):
    _cls: Channel = Channel

    def _create_id(self, obj: Channel) -> str:
        return self._combine(obj.guild_id, obj.id)


class Roles(Collection[Snowflake, Role]):
    _cls: Role = Role


class Members(Collection[Snowflake, Guild_Member]):
    _cls: Guild_Member = Guild_Member

    def _create_id(self, obj: Guild_Member) -> str:
        return self._combine(obj.user.id)

    def size(self, guild_id: Snowflake) -> list[KT]:
        return self._cache.keys(self._combine(guild_id, "*"))


class Presences(Collection[Snowflake, tuple[str, int, int]]):
    _cls = tuple

    def _create_id(self, obj: Presence_Update) -> str:
        return self._combine(obj.user.id)

    def store(self, data: Presence_Update):
        self._cache.add(
            data.user.id,
            (
                data.activities[0].name,
                data.activities[0].created_at,
                data.activities[0].application_id,
            ),
            expire_time=self._expire,
        )

    def update(self, data: Presence_Update):
        self._cache.update(
            data.user.id,
            (
                data.activities[0].name,
                data.activities[0].created_at,
                data.activities[0].application_id,
            ),
        )


class Cooldowns(Collection[str, str]):
    def _create_id(self, guild_id: Snowflake, user_id: Snowflake, type: str) -> str:
        return self._combine(guild_id, user_id, type)

    def get(self, guild_id: Snowflake, user_id: Snowflake, type: str) -> datetime:
        r = self._cache.get(self._combine(guild_id, user_id, type))
        return datetime.fromtimestamp(r, tz=timezone.utc) if r else None

    def has(self, guild_id: Snowflake, user_id: Snowflake, type: str) -> bool:
        return self._cache.has(self._combine(guild_id, user_id, type))

    def store(self, guild_id: Snowflake, user_id: Snowflake, type: str, expire: timedelta=timedelta(seconds=60)) -> str:
        return self._cache.add(
            self._create_id(guild_id, user_id, type),
            datetime.now(tz=timezone.utc).timestamp(),
            expire_time=expire,
        )


class Context(Collection[str, str]):
    _expire: timedelta = timedelta(minutes=10)

    def _create_id(self, guild_id: Snowflake, channel_id: Snowflake, user_id: Snowflake) -> str:
        return self._combine(guild_id, channel_id, user_id)


class KeyValue(Collection[str, str]):
    def __init__(self, cache: Union[Dictionary, Redis] = None, guild_id: int = 0) -> None:
        self.guild_id = guild_id
        super().__init__(cache)

    def store(self, key: str, value: str, expire_time: timedelta = None) -> str:
        return self._cache.add(key, value, expire_time)

    def get(self, key: str) -> str:
        return self._cache.get(key)
