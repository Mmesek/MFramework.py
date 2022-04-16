from typing import Dict, Optional

from MFramework import Snowflake, Guild, Emoji, Message

from MFramework import log
from MFramework.commands import Groups
from MFramework.database.cache_internal import models as collections

from .base import Base

class Guild(Base):
    guild: Guild
    guild_id: Snowflake
    def __init__(self, *, guild: Guild, **kwargs) -> None:
        self.guild_id = guild.id
        self.guild = guild
        super().__init__(guild=guild, **kwargs)

class ObjectCollections(Guild):
    messages: collections.Messages = collections.Messages()
    channels: collections.Channels = collections.Channels()
    roles: collections.Roles = collections.Roles()
    emojis: Dict[Snowflake, Emoji] = {}
    members: collections.Members = collections.Members()
    voice: Dict[Snowflake, Dict[Snowflake, float]]
    #voice_states: Dict[Snowflake, Voice_State] = {} #
    #voice_states: Cache[Snowflake, Voice_State] = {} #TODO
    #voice_channels: Dict[Snowflake, Dict[Snowflake, int]] = {}
    presence: collections.Presences = collections.Presences()#[Snowflake, Tuple[str, int, Snowflake]] = {}
    last_messages: Dict[Snowflake, Message]
    threads: Dict[Snowflake, Snowflake]
    dm_threads: Dict[Snowflake, Snowflake]
    kv: collections.KeyValue = collections.KeyValue()
    def __init__(self, *, bot, guild: Guild, rds: Optional[collections.Redis] = None, **kwargs) -> None:
        if not rds:
            _redis = bot.cfg.get("redis", {})
            host = _redis.get("host", None)
            if host:
                r = collections.Redis(host, password=_redis.get("password", None), port=_redis.get("port", 6379), db=_redis.get("_db", 0))
            else:
                r = collections.Dictionary()
        else:
            r = rds
        self.members = collections.Members().from_list(guild.members)
        self.roles = collections.Roles().from_list(guild.roles)
        self.channels = collections.Channels().from_list(guild.channels, guild_id = guild.id)
        #for vs in guild.voice_states:
            #from MFramework.utils.timers2 import _startTimer
            #if not vs.self_mute and not vs.self_deaf:
            #    _startTimer(self.voice_channels, vs.channel_id, vs.user_id) # Don't start if users are muted! TODO
        #self.voice_states = {i.user_id:i for i in guild.voice_states}
        self.afk_channel = guild.afk_channel_id
        self.messages = collections.Messages(r)
        self.cooldowns = collections.Cooldowns(r)
        self.kv = collections.KeyValue(r, guild.id)
        self.presence = collections.Presences()
        self.threads = {i.id: i.parent_id for i in guild.threads}
        self.dm_threads = {i.id: int(i.name.split('-')[-1].strip()) for i in guild.threads if i.name.split('-')[-1].strip().isdigit()}
        self.last_messages = {}
        self.voice = {}
        self.responses = {}
        super().__init__(bot=bot, guild=guild, rds=rds, **kwargs)
        self.setRoleGroups()
        self.setChannels()

    def load_voice_states(self, voice_states):
        for vc in voice_states:
            if self.members[vc.user_id].user.bot:
                continue
            if vc.channel_id not in self.voice:
                self.voice[vc.channel_id] = {}
            if vc.user_id not in self.voice[vc.channel_id]:
                import time
                log.debug('init of user %s', vc.user_id)
                if vc.self_deaf:
                    i = -1
                elif len(self.voice[vc.channel_id]) > 0:
                    i = time.time()
                else:
                    i = 0
                self.voice[vc.channel_id][vc.user_id] = i
        for c in self.voice:
            u = list(self.voice[c].keys())[0]
            if len(self.voice[c]) == 1 and u > 0:
                self.voice[c][u] = 0
            elif len(self.voice[c]) > 1 and u == 0:
                self.voice[c][u] = time.time()

    def setRoleGroups(self):
        for id, role in self.roles.items():
            if role.name in {"Admin", "Administrator"}:
                _group = Groups.ADMIN
            elif role.name == "Moderator":
                _group = Groups.MODERATOR
            elif role.name == "Nitro Booster" and role.managed is True:
                _group = Groups.NITRO
            elif role.name == "Muted":
                _group = Groups.MUTED
            elif role.name.lower() in {"VIP", "Contributor"}:
                _group = Groups.VIP
            elif role.name == 'Limbo':
                _group = Groups.LIMBO
            elif role.name == "No Exp":
                self.disabled_roles.append(id)
                continue
            elif role.name == "Voice":
                self.voice_link = id
                continue
            else:
                continue
            self.groups[_group].add(id)
    
    def setChannels(self):
        for id, channel in self.channels.items():
            if "bot" in channel.name:
                self.disabled_channels.append(id)
            elif "nitro" in channel.name:
                self.nitro_channel = id
            elif channel.type == 2 and channel.name.startswith("#"):
                self.dynamic_channels[id] = id

    def cachedVoice(self, data):
        join = self.voice.pop(data.user_id, None)
        if join is not None:
            import time
            return time.time() - join
        return 0