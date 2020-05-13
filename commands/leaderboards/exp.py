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
@register(group='Global', help='Shows exp of specified user', alias='', category='')
async def exp(self, *user, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    session = self.db.sql.session()
    user = re.search(r'\d+', data.content)
    if user:
        user = user[0]
    else:
        user = data.author.id
    r = session.query(db.UserLevels).filter(db.UserLevels.GuildID == data.guild_id).filter(db.UserLevels.UserID == user).first()
    embed = Embed()
    t = ''
    if r is not None:
        if r.EXP:
            t+= f'\nChat: {r.EXP}'
        if r.vEXP:
            t += f'\nVoice: {secondsToText(r.vEXP, self.cache[data.guild_id].language.upper())}'
    else:
        t = "User Not Found or No exp yet"
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

@register(group='Global', help='Shows most played games on server', alias='', category='')
async def topgames(self, *args, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    session = self.db.sql.session()
    total = session.query(db.Games.Title, db.Games.TotalPlayed).order_by(db.Games.TotalPlayed.desc()).limit(30).all()
    embed = Embed()
    t = ''
    a = []
    c = {}
    for r in total:
        i = 0
        if r.Title not in c:
            c[r.Title] = r.TotalPlayed
        else:
            c[r.Title] += r.TotalPlayed
    for r in c:
        a+= [(r, c[r])]
    a = sorted(a, key=lambda x: x[1], reverse=True)
    for x, i in enumerate(a):
        t += f'\n{x+1}. {i[0][:32]} - {secondsToText(i[1], self.cache[data.guild_id].language.upper())}'[:67]
    embed.setDescription(t).setColor(self.cache[data.guild_id].color)
    await self.embed(data.channel_id, '', embed.embed)

@register(group='Global', help='Shows games played by specified user', alias='', category='')
async def games(self, *args, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    session = self.db.sql.session()
    user = re.search(r'\d+', data.content)
    if user:
        user = user[0]
    else:
        user = data.author.id
    total = session.query(db.Games).filter(db.Games.UserID == user).all()
    embed = Embed()
    t = ''
    if total is not None:
        a = []
        c = {}
        i = 0
        for r in total:
            if r.Title not in c:
                c[r.Title] = r.TotalPlayed
            else:
                c[r.Title] += r.TotalPlayed
        for r in c:
            a+= [(r, c[r])]
        a = sorted(a, key=lambda x: x[1], reverse=True)
        for x, i in enumerate(a):
            l = f'\n{x+1}. {i[0][:32]} - {secondsToText(i[1], self.cache[data.guild_id].language.upper())}'[:67]
            if len(t+l) < 2024:
                t += l
            else:
                break
    else:
        t = "User Not Found or No exp yet"
    embed.setDescription(t).setColor(self.cache[data.guild_id].color)
    await self.embed(data.channel_id, '', embed.embed)

@register(group='Global', help='Shows who played specified game', alias='', category='')
async def whoplayed(self, *game, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    session = self.db.sql.session()
    r = session.query(db.Games).filter(db.Games.Title == ' '.join(game)).all()
    embed = Embed()
    t = ''
    if r is not None:
        a = []
        c = {}
        i = 0
        for i in r:
            a+=[(i.UserID, i.TotalPlayed)]
        a = sorted(a, key=lambda x: x[1], reverse=True)
        for x, i in enumerate(a):
            t += f'\n{x+1}. <@{i[0]}> - {secondsToText(i[1], self.cache[data.guild_id].language.upper())}'
    else:
        t = "Game Not Found"
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