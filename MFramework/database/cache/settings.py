from typing import List, Dict

from MFramework import Snowflake, Guild

from MFramework.commands import Groups

from MFramework.database import alchemy as db
from MFramework.database.alchemy import types

from .database import Database
from .guild import ObjectCollections

class Roles(Database):
    reaction_roles: Dict[str, Dict[Snowflake, Dict[str, List[Snowflake]]]]
    presence_roles: Dict[str, Dict[Snowflake, Dict[str, List[Snowflake]]]]
    level_roles: List #TODO
    def __init__(self, *, bot, guild: Guild, **kwargs) -> None:
        self.presence_roles = {}
        self.reaction_roles = {}
        self.level_roles = []
        super().__init__(bot=bot, guild=guild, **kwargs)
        with bot.db.sql.Session.begin() as s:
            self.get_Roles(s)


    def get_reaction_roles(self, roles):
        reactions = roles.filter(db.Role.settings.any(name=types.Setting.Reaction)).all()
        _reactions = {}
        for reaction in reactions:
            if types.Setting.Group in reaction.settings:
                group = reaction.settings[types.Setting.Group].str
            else:
                group = None
            message = reaction.settings[types.Setting.MessageID].snowflake
            _reaction = reaction.settings[types.Setting.Reaction].str
            if group not in _reactions:
                _reactions[group] = {}
            if message not in _reactions[group]:
                _reactions[group][message] = {}
            if reaction not in _reactions[group][message]:
                _reactions[group][message][_reaction] = []
            _reactions[group][message][_reaction].append(reaction.id)
        self.reaction_roles = _reactions

    def get_activity_roles(self, roles):
        activitites = roles.filter(db.Role.settings.any(name=types.Setting.Presence)).all()
        for presence in activitites:
            self.presence_roles[presence.settings[types.Setting.Presence].str] = presence.id

    def get_role_groups(self, roles):
        permissions = roles.filter(db.Role.settings.any(name=types.Setting.Permissions)).all()
        for permission in permissions:
            g = Groups.get(permission.settings[types.Setting.Permissions].int)
            if g in self.groups:
                self.groups[g].add(permission.id)
    
    def get_level_roles(self, roles):
        levels = roles.filter(db.Role.settings.any(name=types.Setting.Exp)).all() #TODO
        self.level_roles = sorted({role.id: role.float for role in levels}, key=lambda x: x[1])

    def get_Roles(self, session):
        roles = session.query(db.Role).filter(db.Role.server_id == self.guild_id)
        self.get_reaction_roles(roles)
        self.get_activity_roles(roles)
        self.get_role_groups(roles)
        self.get_level_roles(roles)
        breakpoint

class Settings(Database, ObjectCollections):
    disabled_channels: List[Snowflake]
    disabled_roles: List[Snowflake]

    rpg_channels: List[Snowflake]
    rpg_dices: List[str]

    nitro_channel: Snowflake
    afk_channel: Snowflake
    dynamic_channels: Dict[Snowflake, str]

    voice_link: Snowflake = None
    flags: int = 0
    permissions: int = 0
    language: str = 'en'
    allowed_duplicated_messages: int = 1
    settings: dict
    def __init__(self, *, bot, guild: Guild, **kwargs) -> None:
        self.disabled_channels = []
        self.disabled_roles = []
        self.rpg_channels = []
        self.rpg_dices = []
        self.dynamic_channels = {"channels":{}}
        super().__init__(bot=bot, guild=guild, **kwargs)
        with bot.db.sql.Session.begin() as s:
            g = self.get_guild(s)
            self.load_settings(g)
            self.get_Channels(s)
        if self.is_tracking(types.Flags.Voice):
            self.load_voice_states(guild.voice_states)

    def load_settings(self, guild):
        self.settings = guild.settings
        for setting, value in guild.settings.items():
            setattr(self, setting.name.lower(), getattr(value, setting.annotation.__name__.lower(), None))

    def get_rpg_channels(self, channels):
        rpg_channels = channels.filter(db.Channel.settings.any(name=types.Setting.RPG)).all()
        self.rpg_channels = [channel.id for channel in rpg_channels]
    
    def get_exp_settings(self, channels):
        channels = channels.filter(db.Channel.settings.any(name=types.Setting.Exp)).all()
        self.disabled_channels.extend([channel.id for channel in channels if not channel.float])
        self.exp_rates = {channel.id: channel.float for channel in channels}

    def get_Channels(self, session):
        channels = session.query(db.Channel).filter(db.Channel.server_id == self.guild_id)
        self.get_rpg_channels(channels)
        self.get_exp_settings(channels)

    def is_tracking(self, flag):
        from mlib.utils import bitflag
        return bitflag(self.flags, flag)