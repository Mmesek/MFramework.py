from MFramework.commands import register
from MFramework.database import alchemy as db
from MFramework.utils.utils import Embed, secondsToText

@register(group='Global', help='Shows Chat leaderboard', alias='', category='')
async def topchat(self, *args, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    session = self.db.sql.session()
    total = session.query(db.UserLevels).filter(db.UserLevels.GuildID == data.guild_id).order_by(db.UserLevels.EXP.desc()).limit(10).all()
    embed = Embed()
    t = ''
    for r in total:
        if r.EXP:
            t += f'\n<@{r.UserID}> - {r.EXP}'
    embed.setDescription(t).setColor(self.cache[data.guild_id].color)
    await self.embed(data.channel_id, '', embed.embed)

@register(group='Global', help='Shows Voice leaderboard', alias='', category='')
async def topvoice(self, *args, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    session = self.db.sql.session()
    total = session.query(db.UserLevels).filter(db.UserLevels.GuildID == data.guild_id).order_by(db.UserLevels.vEXP.desc()).limit(10).all()
    embed = Embed()
    t = ''
    for r in total:
        if r.vEXP:
            t += f'\n<@{r.UserID}> - {secondsToText(r.vEXP, self.cache[data.guild_id].language.upper())}'
    embed.setDescription(t).setColor(self.cache[data.guild_id].color)
    await self.embed(data.channel_id, '', embed.embed)

import re
@register(group='Global', help='Shows exp', alias='', category='')
async def exp(self, *user, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    session = self.db.sql.session()
    if user:
        user = re.search(r'\d+', data.content)
    else:
        user = data.user_id
    total = session.query(db.UserLevels).filter(db.UserLevels.GuildID == data.guild_id).filter(db.UserLevels.UserID == user).first()
    embed = Embed()
    t = ''
    for r in total:
        if r.EXP:
            t+= f'\nChat: {r.EXP}'
        if r.vEXP:
            t += f'\nVoice: {secondsToText(r.vEXP, self.cache[data.guild_id].language.upper())}'
    embed.setDescription(t).setColor(self.cache[data.guild_id].color)
    await self.embed(data.channel_id, '', embed.embed)

@register(group='Global', help='Shows leaderboard', alias='', category='')
async def top(self, *args, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    session = self.db.sql.session()
    total = session.query(db.UserLevels).filter(db.UserLevels.GuildID == data.guild_id).order_by(db.UserLevels.EXP.desc()).limit(10).all()
    embed = Embed()
    t = ''
    a = []
    for r in total:
        i = 0
        if r.EXP:
            i += r.EXP
        if r.vEXP:
            i += int((r.vEXP / 60) / 10)
        a += [(r.UserID, i)]
    a = sorted(a, key=lambda x: x[1], reverse=True)
    for x, i in enumerate(a):
        t += f'\n{x+1}. <@{i[0]}> - {i[1]}'
    embed.setDescription(t).setColor(self.cache[data.guild_id].color)
    await self.embed(data.channel_id, '', embed.embed)


'''
1 - 10
2 - 25
3 - 50 - Przybysz
4 - 100
5 - 200
6 - 300
7 - 500
8 - 750
9 - 1000 - Bywalec
10 - 1250
11 - 1750
12 - 2500
13 - 3000
14 - 4000
15 - 5000 - Stały Bywalec
16 - 6250
17 - 7500
18 - 9000
19 - 10000
20 - 12500 - Legenda

(i+x)*1.25/2*(i*i)
(i+i)*1.25/2*(i*i)?
'''