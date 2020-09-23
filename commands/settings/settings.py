from MFramework.commands import register, subcommand, Invalid
from MFramework.database import alchemy as db
@register(group='Moderator', help='Short description to use with help command', alias='', category='')
async def settings(self, command, *args, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    await settings.subcmds.get(command, Invalid)(self, *args, data=data, language=language, **kwargs)

@subcommand(settings, 'Moderator')
@register(group='Moderator', help='Short description to use with help command', alias='', category='')
async def channel(self, sub_channel_cmd, *args, data, language, **kwargs):
    await channel.subcmds.get(sub_channel_cmd, Invalid)(self, *args, data=data, language=language, **kwargs)

#@register(group='System', help='Short description to use with help command', alias='', category='')
@subcommand(settings, 'Moderator')
async def channel_type(self, channel_id, type, name='', parent_or_buffer_id='', bitrate=64000, user_limit=0, postion=0, *args, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
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

@subcommand(channel, "Moderator")
async def set_language(self, new_language, channel_id, *args, data, language, **kwargs):
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
