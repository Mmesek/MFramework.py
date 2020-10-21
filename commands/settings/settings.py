from MFramework.commands import register, subcommand, check_if_command
from MFramework.database import alchemy as db



@register(group='Mod', help='Server settings', alias='', category='')
async def settings(self, command=None, *args, data, language, group, **kwargs):
    '''Extended description to use with detailed help command'''
    #await settings.subcmds[group].get(command, Invalid)
    _command = await check_if_command(self, settings, command, group, data)
    await _command(self, *args, data=data, language=language, group=group, **kwargs)

@subcommand(settings, 'Mod')
async def channel(self, channel_id=None, sub_channel_cmd=None, *args, data, language, group, **kwargs):
    if not channel_id.isdigit():
        args = (sub_channel_cmd, *args)
        sub_channel_cmd = channel_id
        channel_id = data.channel_id        
    _command = await check_if_command(self, channel, sub_channel_cmd, group, data)
    #await channel.subcmds[group].get(sub_channel_cmd, Invalid)
    await _command(self, *args, data=data, language=language, group=group, channel_id=channel_id, **kwargs)

@subcommand(settings, 'Mod')
async def channel_type(self, type, name='', parent_or_buffer_id='', bitrate=64000, user_limit=0, postion=0, *args, data, language, channel_id, **kwargs):
    template = None
    if type == 'dynamic':
        template = {'name': name, 'bitrate': int(bitrate), 'user_limit': user_limit, 'position': 0, 'permission_overwrites': [], 'parent_id': parent_or_buffer_id}
    elif type == 'buffer':
        template = {'buffer': parent_or_buffer_id}
    c = db.Channels(data.guild_id, channel_id, type, template)
    self.db.sql.add(c)
    if type != 'rpg':
        self.cache[data.guild_id].dynamic_channels[channel_id] = template
    else:
        self.cache[data.guild_id].rpg_channels.append(channel_id)

@subcommand(channel, "Admin")
async def language(self, new_language, *args, data, language, channel_id, **kwargs):
    s = self.db.sql.session()
    channel = s.query(db.Channels).filter(db.Channels.GuildID == data.guild_id, db.Channels.ChannelID == channel_id).first()
    if channel is not None:
        c = channel
    else:
        c = db.Channels(data.guild_id, channel_id, None)
    c.Language = new_language
    s.merge(c)
    s.commit()
    self.cache[data.guild_id].language_overwrites[int(channel_id)] = new_language

@subcommand(settings, 'Admin')
async def track(self, command, *args, data, language, group, **kwargs):
    _command = await check_if_command(self, track, command, group, data)
    await _command(self, *args, data=data, language=language, group=group, **kwargs)

@subcommand(track, 'Admin')
async def voice(self, *args, data, language, **kwargs):
    s = self.db.sql.session()
    server = s.query(db.Servers).filter(db.Servers.GuildID == data.guild_id).first()
    if server.TrackVoice:
        server.TrackVoice = False
    else:
        server.TrackVoice = True
    s.commit()
    self.cache[data.guild_id].trackVoice = server.TrackVoice

@subcommand(track, 'Admin')
async def presence(self, *args, data, language, **kwargs):
    s = self.db.sql.session()
    server = s.query(db.Servers).filter(db.Servers.GuildID == data.guild_id).first()
    if server.TrackPresence:
        server.TrackPresence = False
    else:
        server.TrackPresence = True
    s.commit()
    self.cache[data.guild_id].trackPresence = server.TrackPresence
