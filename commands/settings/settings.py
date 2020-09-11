from MFramework.commands import register
from MFramework.database import alchemy as db
@register(group='System', help='Short description to use with help command', alias='', category='')
async def settings(self, *args, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    pass

@register(group='System', help='Short description to use with help command', alias='', category='')
async def channel(self, channel_id, type, name='', parent_or_buffer_id='', bitrate=64000, user_limit=0, postion=0, *args, data, language, **kwargs):
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
