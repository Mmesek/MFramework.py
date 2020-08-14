from MFramework.commands import register
from MFramework.database import alchemy as db

from MFramework.utils.log import Infraction

import re, datetime

types = {
    "warn": "warned",
    "tempmute":"temporarily muted",
    "mute": "muted",
    "kick": "kicked",
    "tempban":"temporarily banned",
    "ban": "banned",
    "unban": "unbanned",
    "unmute": "unmuted"
}

@register(group='Mod', help='Warns user', alias='tempmute, mute, kick, tempban, ban, unban, unmute', category='')
async def warn(self, user, *reason, data, language, cmd, **kwargs):
    '''Extended description to use with detailed help command'''
    await infract(self, data, user, reason, cmd)


async def infract(self, data, user, reason, type):
    user = re.search(r'\d\d+', user)
    if user:
        user = int(user[0])
    else:
        return await self.message(data.channel_id, "There was some error parsing user ID. Make sure to either @Mention them or provide their UserID")
    reason = ' '.join(reason)
    timestamp = datetime.datetime.fromisoformat(data.timestamp)
    r = db.Infractions(data.guild_id, user, timestamp, reason, data.author.id, None, type)
    self.db.sql.add(r)
    await Infraction(self, data, user, types[type], reason, attachments=data.attachments)
    if type in ['unban', 'unmute']:
        return
    guild = await self.get_guild(data.guild_id)
    guild = guild.name
    try:
        cid = await self.create_dm(user)
    except:
        return await self.create_reaction(data.channel_id, data.id, self.emoji['failure'])
    s = f"You've been {types[type]} in {guild} server"
    if reason != '':
        s+=f" for {reason}"
    result = await self.message(cid.id, s)
    if "code" in result or result == []:
        return await self.create_reaction(data.channel_id, data.id, self.emoji['failure'])
    await self.create_reaction(data.channel_id, data.id, self.emoji['success'])