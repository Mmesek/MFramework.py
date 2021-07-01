from mdiscord import *
from .base import RedisCache, Cache
from datetime import timedelta

class Messages(RedisCache):
    _expire: timedelta = timedelta(days=1)
    _cls: Message = Message
    def _create_id(self, obj: Message) -> str:
        return self._combine(obj.guild_id, obj.channel_id, obj.id)
    def has(self, guild_id, channel_id, message_id):
        return super().has([guild_id, channel_id, message_id])
    def last(self, guild_id, channel_id):
        all = self._redis.r.scan(cursor=0, match=self._combine(guild_id, channel_id)+".*")
        all[1].sort()
        try:
            r = self._redis.get(all[1][-1])
        except:
            return None
        if type(r) is dict:
            return self._cls(**r)
        return r
    def size(self, guild_id, channel_id):
        return self._redis.keys(self._combine(guild_id, channel_id, '*'))

class Channels(RedisCache):
    _cls: Channel = Channel
    def _create_id(self, obj: Channel) -> str:
        return self._combine(obj.guild_id, obj.id)

class Roles(RedisCache):
    _cls: Role = Role

class Users(RedisCache):
    _cls: User = User

class Members(RedisCache):
    _cls: Guild_Member = Guild_Member
    def _create_id(self, obj: Guild_Member) -> str:
        return self._combine(obj.user.id)
    def size(self, guild_id):
        return self._redis.keys(self._combine(guild_id, '*'))

class Presences(Cache):
    _cls = tuple
    def _create_id(self, obj: Presence_Update) -> str:
        return self._combine(obj.user.id)
    def store(self, data: Presence_Update):
        self[data.user.id] = (data.activities[0].name, data.activities[0].created_at, data.activities[0].application_id)
        #self._redis.add(data.user.id, (data.activities[0].name, data.activities[0].created_at, data.activities[0].application_id), expire_time=self._expire)

class Guilds(RedisCache):
    _cls: Guild = Guild

class Cooldowns(RedisCache):
    def _create_id(self, guild_id: Snowflake, user_id: Snowflake, type: str) -> str:
        return self._combine(guild_id, user_id, type)
    def has(self, guild_id, user_id, type):
        return self._redis.has(self._combine(guild_id, user_id, type))
        #return super().has([guild_id, user_id, type])
    def store(self, guild_id, user_id, type, expire=timedelta(seconds=60)):
        return self._redis.add(self._create_id(guild_id, user_id, type), 1, expire_time=expire)

class Context(RedisCache):
    _expire: timedelta = timedelta(minutes=10)
    def _create_id(self, guild_id: Snowflake, channel_id: Snowflake, user_id: Snowflake) -> str:
        return self._combine(guild_id, channel_id, user_id)