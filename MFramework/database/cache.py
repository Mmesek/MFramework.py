from mdiscord import *
from ..commands._utils import Groups
from .. import *
from ..utils.log import Log
from typing import List, Dict, Set, Tuple, Union, DefaultDict

from .cache_internal.models import *
import re
from MFramework import log
from .alchemy import models as db
from .alchemy import types

class GuildCache:
    guild_id: Snowflake
    logging: DefaultDict[str, Log]
    
    guild: Guild

    messages: Messages
    channels: Channels
    roles: Roles
    emojis: Dict[Snowflake, Emoji]
    members: Members
    voice: Dict[Snowflake, Dict[Snowflake, float]]
    #voice_states: Dict[Snowflake, Voice_State] = {} #
    #voice_states: Cache[Snowflake, Voice_State] = {} #TODO
    #voice_channels: Dict[Snowflake, Dict[Snowflake, int]] = {}
    webhooks: Dict[str, Tuple[Snowflake, str]]
    presence: Presences = {}#[Snowflake, Tuple[str, int, Snowflake]] = {}
    groups: Dict[Groups, Set[Snowflake]]

    disabled_channels: List[Snowflake]
    disabled_roles: List[Snowflake]

    rpg_channels: List[Snowflake]
    rpg_dices: List[str]

    canned: Dict[str, re.Pattern]
    responses: Dict[Snowflake, re.Pattern]
    cooldown_values: Dict[str, timedelta]
    blacklisted_words: re.Pattern = None

    nitro_channel: Snowflake
    afk_channel: Snowflake
    dynamic_channels: Dict[Snowflake, str]

    custom_emojis: Dict[str, Union[str, Tuple]]

    reaction_roles: Dict[str, Dict[Snowflake, Dict[str, List[Snowflake]]]]
    presence_roles: Dict[str, Dict[Snowflake, Dict[str, List[Snowflake]]]]
    level_roles: List #TODO

    tracked_streams: List[str]

    giveaway_messages: List[Snowflake]
    last_messages: Dict[Snowflake, Message]
    threads: Dict[Snowflake, Snowflake]

    voice_link: Snowflake = None
    flags: int = 0
    permissions: int = 0
    language: str = 'en'
    allowed_duplicated_messages: int = 1
    settings: dict

    name: str
    color: int
    alias: str = '?'

    bot: Guild_Member

    def __init__(self, bot, guild: Guild, rds: Optional[Redis] = None):
        self.guild_id = guild.id
        self.guild = guild
        self.groups = {i:set() for i in Groups}
        if not rds:
            host = bot.cfg.get("redis", {}).get("host", None)
            if host:
                r = Redis(host)
            else:
                r = Dictionary()
        else:
            r = rds
        self.members = Members().from_list(guild.members)
        self.roles = Roles().from_list(guild.roles)
        self.channels = Channels().from_list(guild.channels, guild_id = guild.id)
        #for vs in guild.voice_states:
            #from MFramework.utils.timers2 import _startTimer
            #if not vs.self_mute and not vs.self_deaf:
            #    _startTimer(self.voice_channels, vs.channel_id, vs.user_id) # Don't start if users are muted! TODO
        #self.voice_states = {i.user_id:i for i in guild.voice_states}
        self.afk_channel = guild.afk_channel_id
        self.messages = Messages(r)
        self.cooldowns = Cooldowns(r)
        self.presence = Presences()
        self.threads = {i.id: i.parent_id for i in guild.threads}
        self.cooldown_values = {}
        self.last_messages = {}
        self.voice = {}
        self.custom_emojis = {}
        self.presence_roles = {}
        self.reaction_roles = {}
        self.level_roles = []
        self.tracked_streams = []
        self.giveaway_messages = []
        self.last_messages = {}
        self.rpg_dices = []
        self.rpg_channels = []
        self.disabled_channels = []
        self.disabled_roles = []
        self.dynamic_channels = {"channels":{}}
        self.responses = {}
        self.canned = {}
        self.setBot(bot.user_id)
        self.setColor()
        self.setRoleGroups()
        self.setChannels()
        self.load_from_database(bot)
        self.set_loggers(bot)
        if self.is_tracking(types.Flags.Voice):
            self.load_voice_states(guild.voice_states)
    
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
    
    def setBot(self, user_id):
        self.bot = self.members[user_id]
        self.calculate_permissions()
    
    def new_guild(self, s):
        return db.Server.fetch_or_add(s, id=self.guild_id)

    def get_guild(self, s) -> db.Server:
        server = db.Server.filter(s, id=self.guild_id).first()
        if server:
            return server
        print("Adding new guild...")
        return self.save_to_database(s)
        #return db.Server.fetch_or_add(s, id=self.guild_id)

    def setColor(self):
        color = None
        for role_id in self.bot.roles:
            role = self.roles[role_id]
            if role.managed is True:
                color = (role.position, role.color, True)
            elif color == None:
                color = (role.position, role.color, False)
            elif role.position > color[0] and color[2] != True:
                color = (role.position, role.color, False)
        self.color = color[1] if color else None
    
    def calculate_permissions(self):
        for role in self.bot.roles:
            self.permissions |= int(self.roles[role].permissions)
    
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
    
    def cachedVoice(self, data):
        join = self.voice.pop(data.user_id, None)
        if join is not None:
            import time
            return time.time() - join
        return 0

    def cachedRoles(self, roles):
        for group in self.groups:
            if any(i in roles for i in self.groups[group]):
                return group
        return Groups.GLOBAL

    def get_Custom_Emojis(self, session):
        s = db.Snippet.filter(session, server_id = self.guild_id, type = types.Snippet.Emoji).all()
        for emoji in s:
            if not emoji.filename:
                self.custom_emojis[emoji.name.lower()] = emoji.content
            else: 
                self.custom_emojis[emoji.name.lower()] = (emoji.filename, emoji.image)
    
    def recompile_Canned(self, session):
        s = db.Snippet.filter(session, server_id = self.guild_id, type = types.Snippet.Canned_Response).all()
        import re
        self.canned = {}
        self.canned['patterns'] = re.compile('|'.join([f'(?P<{re.escape(i.name)}>{i.trigger})' for i in s]))
        self.canned['responses'] = {re.escape(i.name):i.content for i in s}
    
    def recompile_Triggers(self, session):
        responses = {}
        triggers = db.Snippet.filter(session, server_id = self.guild_id, type = types.Snippet.Regex).all()
        self.regex_responses = {}
        for trig in triggers:
            if trig.cooldown:
                self.cooldown_values[trig.name] = trig.cooldown
            self.regex_responses[trig.name] = trig.content
            if trig.group not in responses:
                responses[trig.group] = {}
            if trig.name not in responses[trig.group]:
                responses[trig.group][trig.name] = trig.trigger
            else:
                responses[trig.group] = {trig.name: trig.trigger}
        import re
        for r in responses:
            self.responses[r] = re.compile(r"(?:{})".format("|".join("(?P<{}>{})".format(k, f) for k, f in responses[r].items())))
    
    def get_Webhooks(self, session):
        webhooks = session.query(db.Webhook).filter(db.Webhook.server_id == self.guild_id, db.Webhook.subscriptions.any(db.Subscription.source.contains('logging-'))).all()
        self.webhooks = {
            sub.source.replace('logging-','').replace('_log',''): (webhook.id, webhook.token)
            for webhook in webhooks
            for sub in webhook.subscriptions if 'logging-' in sub.source
        }
    
    def get_Blacklisted_Words(self, session):
        words = db.Snippet.filter(session, server_id = self.guild_id, type = types.Snippet.Blacklisted_Word).all()
        if len(words) > 0:
            self.blacklisted_words = re.compile(r"(?i){}".format("|".join(words)))

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

    def get_tracked_streams(self, session):
        self.tracked_streams = [i.name for i in db.Snippet.filter(session, server_id = self.guild_id, type = types.Snippet.Stream).all()]

    def get_role_groups(self, roles):
        permissions = roles.filter(db.Role.settings.any(name=types.Setting.Permissions)).all()
        for permission in permissions:
            g = Groups.get(permission.settings[types.Setting.Permissions].int)
            if g in self.groups:
                self.groups[g].add(permission.id)
    
    def get_level_roles(self, roles):
        levels = roles.filter(db.Role.settings.any(name=types.Setting.Level)).all() #TODO

    def get_Roles(self, session):
        roles = session.query(db.Role).filter(db.Role.server_id == self.guild_id)
        self.get_reaction_roles(roles)
        self.get_activity_roles(roles)
        self.get_role_groups(roles)
        self.get_level_roles(roles)
        breakpoint
    
    def get_rpg_channels(self, channels):
        rpg_channels = channels.filter(db.Channel.settings.any(name=types.Setting.RPG)).all()
        self.rpg_channels = [channel.id for channel in rpg_channels]

    def get_Channels(self, session):
        channels = session.query(db.Channel).filter(db.Channel.server_id == self.guild_id)
        self.get_rpg_channels(channels)

    def set_loggers(self, ctx):
        from mlib.types import aInvalid
        from collections import defaultdict
        self.logging = defaultdict(lambda: aInvalid)
        from mlib.utils import all_subclasses
        _classes = {i.__name__.lower():i for i in all_subclasses(Log)}
        for webhook in self.webhooks:
            if webhook in _classes:
                self.logging[webhook] = _classes[webhook](ctx, self.guild_id, webhook, *self.webhooks[webhook])

    def load_from_database(self, ctx):
        with ctx.db.sql.Session.begin() as s:
            g = self.get_guild(s)
            self.load_settings(g)
            self.recompile_Triggers(s)
            self.recompile_Canned(s)
            self.get_Webhooks(s)
            self.get_Custom_Emojis(s)
            self.get_Roles(s)
            self.get_Blacklisted_Words(s)
            self.get_Channels(s)
            self.get_tracked_streams(s)

    def load_settings(self, guild):
        self.settings = guild.settings
        for setting, value in guild.settings.items():
            setattr(self, setting.name.lower(), getattr(value, setting.annotation.__name__.lower(), None))

    def save_to_database(self, s):
        #s = ctx.db.sql.Session()
        guild = self.new_guild(s)
        for channel in self.disabled_channels:
            _channel = db.Channel.fetch_or_add(s, server_id=self.guild_id, id=channel)
            _channel.add_setting(types.Setting.Exp, False)
            s.add(_channel)
        if hasattr(self, 'nitro_channel'):
            nitro_channel = db.Channel.fetch_or_add(s, server_id=self.guild_id, id=self.nitro_channel)
            nitro_channel.add_setting(types.Setting.Flags, types.Flags.Nitro)
            s.add(nitro_channel)
        for role in self.disabled_roles:
            _role = db.Role.fetch_or_add(s, server_id=self.guild_id, id=role)
            _role.add_setting(types.Setting.Exp, False)
        for group in self.groups:
            for role in self.groups[group]:
                _role = db.Role.fetch_or_add(s, server_id=self.guild_id, id=role)
                _role.add_setting(types.Setting.Permissions, group.value)
                s.add(_role)
        if self.voice_link:
            guild.add_setting(types.Setting.Voice_Link, self.voice_link)
        #s.add(guild) ?
        #s.commit()
        return guild
    
    def is_tracking(self, flag):
        from mlib.utils import bitflag
        return bitflag(self.flags, flag)


