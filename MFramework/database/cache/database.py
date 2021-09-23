import re, asyncio

from typing import List, Dict, Tuple, Union
from datetime import timedelta

from MFramework import Snowflake, Guild
from MFramework.database import alchemy as db
from MFramework.database.alchemy import types

from .guild import Guild

class Database(Guild):
    custom_emojis: Dict[str, Union[str, Tuple]]
    tracked_streams: List[str]
    canned: Dict[str, re.Pattern]
    responses: Dict[Snowflake, re.Pattern]
    cooldown_values: Dict[str, timedelta]
    blacklisted_words: re.Pattern = None
    def __init__(self, *, bot, guild: Guild, **kwargs) -> None:
        self.custom_emojis = {}
        self.tracked_streams = []
        self.canned = {}
        self.responses = {}
        self.cooldown_values = {}
        super().__init__(bot=bot, guild=guild, **kwargs)
        self.load_from_database(bot)

    def new_guild(self, s):
        return db.Server.fetch_or_add(s, id=self.guild_id)

    def get_guild(self, s) -> db.Server:
        server = db.Server.filter(s, id=self.guild_id).first()
        if server:
            return server
        print("Adding new guild...")
        return self.save_to_database(s)
        #return db.Server.fetch_or_add(s, id=self.guild_id)
    
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
    
    def get_Blacklisted_Words(self, session):
        words = db.Snippet.filter(session, server_id = self.guild_id, type = types.Snippet.Blacklisted_Word).all()
        if len(words) > 0:
            self.blacklisted_words = re.compile(r"(?i){}".format("|".join(words)))

    def get_tracked_streams(self, session):
        self.tracked_streams = [i.name for i in db.Snippet.filter(session, server_id = self.guild_id, type = types.Snippet.Stream).all()]

    def load_from_database(self, ctx):
        with ctx.db.sql.Session.begin() as s:
            self.recompile_Triggers(s)
            self.recompile_Canned(s)
            self.get_Custom_Emojis(s)
            self.get_Blacklisted_Words(s)
            self.get_tracked_streams(s)
    
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

class Tasks(Database):
    tasks: Dict[db.types.Task, Dict[Snowflake, asyncio.Task]]
    giveaway_messages: List[Snowflake]
    def __init__(self, *, guild: Guild, **kwargs) -> None:
        self.tasks = {}
        self.giveaway_messages = []
        super().__init__(guild=guild, **kwargs)