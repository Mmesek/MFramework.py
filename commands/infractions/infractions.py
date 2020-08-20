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

@register(group='Mod', help='Warns user', alias='tempmute, mute, kick, tempban, ban, unban, unmute', category='infractions')
async def warn(self, user, *reason, data, language, cmd, **kwargs):
    '''Extended description to use with detailed help command'''
    await infract(self, data, user, reason, cmd)

async def parse_id(self, data, user):
    user = re.search(r'\d\d+', user)
    if user:
        return int(user[0])
    else:
        await self.message(data.channel_id, "There was some error parsing user ID. Make sure to either @Mention them or provide their UserID")
        return

async def infract(self, data, user, reason, type):
    user = await parse_id(self, data, user)
    if user == None:
        return
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

@register(group='Mod', help='Shows user Infractions', alias='', category='infractions')
async def infractions(self, *user, data, show_all=False, language, **kwargs):
    '''Extended description to use with detailed help command'''
    from MFramework.utils.utils import Embed#, get_main_color
    if user == ():
        user = data.author.id
        avatar = data.author.avatar
        username = data.author.username
        discriminator = data.author.discriminator
    else:
        user = await parse_id(self, data, ' '.join(user))
        if data.mentions != []:
            for _user in data.mentions:
                if _user.id == user:
                    avatar = _user.avatar
                    username = _user.username
                    discriminator = _user.discriminator
        else:
            avatar = ''
            username = ''
            discriminator = 0
    if avatar is not None and avatar != '':
        avatar = f"https://cdn.discordapp.com/avatars/{user}/{avatar}.png"
    else:
        avatar = f"https://cdn.discordapp.com/embed/avatars/{int(discriminator) % 5}.png"
    session = self.db.sql.session()
    _infractions = session.query(db.Infractions)
    if not show_all:
        _infractions = _infractions.filter(db.Infractions.GuildID == data.guild_id)
    _infractions = _infractions.filter(db.Infractions.UserID == user).all()
    _infractions.reverse()
    str_infractions = ""
    for x, infraction in enumerate(_infractions):
        str_infractions += f'\n`[{infraction.Timestamp.strftime("%Y/%m/%d")}] [{infraction.InfractionType.upper()}]` - "{infraction.Reason}" by <@{infraction.ModeratorID}>'
        if x == 10:
            break
    if str_infractions != "":
        e = Embed().setAuthor(f"{username}'s infractions", "", avatar).setDescription(str_infractions)#.setColor(get_main_color(avatar))
        await self.embed(data.channel_id, "", e.embed)
    else:
        await self.create_reaction(data.channel_id, data.id, self.emoji['failure'])
