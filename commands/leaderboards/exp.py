from MFramework.commands import register
from MFramework.database import alchemy as db
from MFramework.utils.utils import Embed, secondsToText, tr

import re
@register(group='Global', help='Shows exp of specified user', alias='', category='')
async def exp(self, *user_id, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    session = self.db.sql.session()
    user = getUserID(self, data, data.content)
    r = session.query(db.UserLevels).filter(db.UserLevels.GuildID == data.guild_id).filter(db.UserLevels.UserID == user).first()
    embed = Embed()
    t = ''
    if r is not None:
        if r.EXP:
            t+= tr("commands.exp.chat", language, chat=r.EXP)
        if r.vEXP:
            t += tr("commands.exp.voice", language, voice=secondsToText(r.vEXP, language.upper()))
    else:
        t = tr("commands.exp.none", language)
    embed.setDescription(t).setColor(self.cache[data.guild_id].color)
    await self.embed(data.channel_id, '', embed.embed)

def getUserID(self, data, game_or_user=''):
    user = re.search(r'\d\d\d+', game_or_user)
    if game_or_user == '':
        return data.author.id
    elif user:
        return int(user[0])
    else:
        return game_or_user

@register(group='Global', help='Shows leaderboard', alias='', category='')
async def top(self, limit=10, *args, data, games=False, voice=False, chat=False, count=False, language, **kwargs):
    '''Extended description to use with detailed help command'''
    if type(limit) != int and not limit.isdigit():
        limit = 10
    session = self.db.sql.session()
    if voice and not games and not chat:
        total = session.query(db.UserLevels).filter(db.UserLevels.GuildID == data.guild_id).order_by(db.UserLevels.vEXP.desc()).limit(limit).all()
    elif games and not voice and not chat:
        from sqlalchemy import func
        if count:
            total = session.query(db.Presences.Title, func.count(db.Presences.Title)).filter(db.Presences.GuildID == data.guild_id, db.Presences.Type == 'Game', db.Presences.AppID != None, db.Presences.AppID != 0).group_by(db.Presences.Title).order_by(func.count(db.Presences.Title).desc()).limit(limit).all()
        else:
            total = session.query(db.Presences.Title, func.sum(db.Presences.TotalPlayed), func.count(db.Presences.Title)).filter(db.Presences.GuildID == data.guild_id, db.Presences.Type == 'Game', db.Presences.AppID != None, db.Presences.AppID != 0).group_by(db.Presences.Title).order_by(func.sum(db.Presences.TotalPlayed).desc()).limit(limit).all()
    else:
        total = session.query(db.UserLevels).filter(db.UserLevels.GuildID == data.guild_id).order_by(db.UserLevels.EXP.desc()).limit(limit).all()    
        if not chat:
            t = session.query(db.UserLevels).filter(db.UserLevels.GuildID == data.guild_id).order_by(db.UserLevels.vEXP.desc()).limit(limit).all()
            nt = set(total)
            nt.update(t)
            total = list(nt)
    embed = Embed()
    t = ''
    a = []
    c = {}
    for r in total:
        i = 0
        if games and not voice and not chat:
            if not count:
                if r[2] != 1:
                    title = f'{r.Title} - {r[2]}'
                else:
                    title = r.Title
                if title not in c:
                    c[title] = r[1]#r.TotalPlayed
                else:
                    c[title] += r[1]#r.TotalPlayed
            else:
                a.append((r[0], r[1]))
        else:
            if r.EXP and not voice:
                i = r.EXP
            if r.vEXP:
                if voice:
                    i = r.vEXP
                elif not chat:
                    i += int((r.vEXP / 60) / 10)
            if i != 0:
                a += [(r.UserID, i)]
    for r in c:
        a += [(r, c[r])]
    a = sorted(a, key=lambda x: x[1], reverse=True)
    for x, i in enumerate(a):
        if x == limit:
            break
        p1 = f'<@{i[0]}>'
        if games or voice:
            if games and not voice:
                p1 = i[0]
            if not count:
                st = secondsToText(i[1], language.upper())
            else:
                st = i[1]
        else:
            st = i[1]
        l = f'\n{x+1}. {p1} - {st}'
        if (len(t) + len(l)) < 2024:
            t += l
        else:
            t+=l[:2024-len(t)]
            break
    embed.setDescription(t).setColor(self.cache[data.guild_id].color)
    await self.embed(data.channel_id, '', embed.embed)

@register(group='Global', help='Shows users that played specified game or games played by user', alias='', category='')
async def games(self, *game_or_user, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    query = getUserID(self, data, ' '.join(game_or_user))
    session = self.db.sql.session()
    r = session.query(db.Presences).filter(db.Presences.GuildID == data.guild_id).filter(db.Presences.Type == "Game")
    embed = Embed()
    d = ''
    if type(query) == str:
        r = r.filter(db.Presences.Title == query).all()
        game = True
        embed.setTitle(tr("commands.games.whoPlayed", language, query=query))
    else:
        r = r.filter(db.Presences.UserID == query).all()
        game = False
        d = tr("commands.games.playedBy", language, query=query)
    if r != []:
        t = ''
        a = []
        for i in r:
            if game:
                a += [(i.UserID, i.TotalPlayed)]
            else:
                a += [(i.Title, i.TotalPlayed)]
        a = sorted(a, key=lambda x: x[1], reverse=True)
        for x, i in enumerate(a):
            if game:
                s = f'<@{i[0]}>'
            else:
                s = i[0][:40]
            l = f'\n{x+1}. {s} - {secondsToText(i[1], language.upper())}'
            if len(t+l) < 2024:
                t += l
            else:
                break
    else:
        t = tr("commands.games.none", language)
    if d != '':
        t = d+t
    embed.setDescription(t[:2024]).setColor(self.cache[data.guild_id].color)
    await self.embed(data.channel_id, '', embed.embed)

# Przybysz - Postać || Chat+Voice 500
# Bywalec - Postać && Chat + Voice 1000 || Chat+Voice 2000
# Stały Bywalec - Postać && Chat 1000 && Voice 1000 || chat 2000 || voice 4000 + Chat 500
# Legenda - Postać && Chat 5000 && Voice 5000 || Chat 3000 Voice 10000