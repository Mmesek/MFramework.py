from typing import Dict
from datetime import timedelta

from MFramework import Guild
from MFramework.database import alchemy as db
from MFramework.database.alchemy import types

from .guild import Guild

class Database(Guild):
    cooldown_values: Dict[str, timedelta]
    def __init__(self, *, bot, guild: Guild, **kwargs) -> None:
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

    def load_from_database(self, ctx):
        pass
    
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
