from MFramework.commands import register
from MFramework.database import alchemy as db
from MFramework.utils.utils import Embed

@register(group='Nitro', help='Fetch from store', alias='m', category='', notImpl=True)
async def meme(self, *name, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    if name == ():
        return await memestore(self, data=data, language=language, **kwargs)
    session = self.db.sql.session()
    r = session.query(db.Snippets).filter(db.Snippets.GuildID == data.guild_id).filter(db.Snippets.Type == 'meme').filter(db.Snippets.Name == ' '.join(name)).first()
    if r == None:
        return
    elif r.Image != None:
        #await self.withFile(data.channel_id, r.Image, r.Filename, content)
        await self.embed(data.channel_id, r.Response, {"image":{"url":r.Image}})
    else:
        await self.message(data.channel_id, r.Response, allowed_mentions={"parse":[]})

@register(group='Nitro', help="Shows what's stored", alias='lm', category='', notImpl=True)
async def memestore(self, *args, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    session = self.db.sql.session()
    r = session.query(db.Snippets).filter(db.Snippets.GuildID == data.guild_id).filter(db.Snippets.Type == 'meme').all()
    embed = Embed()
    images = ''
    for i in r:
        if i.Response != '':
            embed.addField(i.Name, i.Response, True)
        else:
            images += '\n' + i.Name
    if images != '':
        embed.addField('Images', images)
    await self.embed(data.channel_id, '', embed.embed)

async def fetch(self, data, typeof, newline, *names, has=None):
    session = self.db.sql.session()
    snippets = []
    for i in names:
        r = session.query(db.Snippets).filter(db.Snippets.GuildID == data.guild_id).filter(db.Snippets.Type == typeof)
        if has is None:
            r = r.filter(db.Snippets.Name == i).first()
        else:
            r = r.filter(db.Snippets.Response.match(i)).all()
            if r != []:
                snippets += [db.Snippets(Name=j.Name, Response=j.Response) for j in r]
                continue
            else:
                r = None
        #if r == None:
            #r = db.Snippets(Name=i, Response='Not found.')
        if r != None:
            snippets += [r]
    if snippets == []:
        snippets = session.query(db.Snippets).filter(db.Snippets.GuildID == data.guild_id).filter(db.Snippets.Type == typeof).filter(db.Snippets.Name == ' '.join(names)).first()
    if snippets == []:
        snippets = session.query(db.Snippets).filter(db.Snippets.GuildID == data.guild_id).filter(db.Snippets.Type == typeof).all()
    if snippets == []:
        return "Not found"
    try:
        snippets = sorted(snippets, key=lambda x: int(x.Name))
    except:
        snippets = sorted(snippets, key=lambda x: x.Name)
    snippets = '\n'.join([newline.format(name=i.Name, response=i.Response) for i in snippets])
    if snippets == '\n':
        snippets = 'None yet.'
    return snippets


@register(group='Admin', help='Loads rules based on message', alias='', category='', notImpl=True)
async def loadRules(self, messagelink, *args, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    link = messagelink.split('/')[-2:]
    channel = link[0]
    message = link[1]
    msg = await self.get_channel_message(channel, message)
    lines = msg.content.split('\n')
    s = self.db.sql.session()
    for line in lines:
        print(line)
        if ')**' in line:
            line = line.split(')**')
            name = line[0].replace('**','').strip()
            response = line[1].strip()
            r = db.Snippets(data.guild_id, data.author.id, name, response, Type='rule')
            s.add(r)
    return s.commit()

@register(group='Admin', help='Create Embed, provide embed in {json} form', alias='', category='', notImpl=True)
async def createembed(self, name, message, trigger, *embed, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    import json
    embed = json.loads(''.join(embed))
    e = db.EmbedTemplates(data.guild_id, data.author.id, name, message, embed)
    self.db.sql.add(e)

@register(group='Mod', help='Embeds', alias='', category='', notImpl=True)
async def embed(self, name, *args, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    session = self.db.sql.session()
    r = session.query(db.EmbedTemplates).filter(db.EmbedTemplates.GuildID == data.guild_id).filter(db.EmbedTemplates.Name == name).first()
    embed = r.Embed
    embed['description'] = embed['description'].format(*args)
    if 'title' in embed:
        embed['title'] = embed['title'].format(*args)
    if 'author' in embed:
        embed['author']['name'] = embed['author']['name'].format(*args)
    embed['footer'] = {"icon_url": f"https://cdn.discordapp.com/avatars/{data.author.id}/{data.author.avatar}", "text": data.author.username}
    embed['timestamp'] = data.timestamp
    await self.embed(data.channel_id, r.Message, embed)


@register(group='Nitro', help='Adds to db', alias='sm', category='')
async def add(self, name, *response, data, trigger='', type='meme', language, group, **kwargs):
    '''meme/cannedresponse/rule/snippet/spotify/rss
    if rss: response = [uri color lang avatar_url]'''
    r = db.Snippets(data.guild_id, data.author.id, name, ' '.join(response), Type=type)
    if type == 'cannedresponse' and group in ['Mod', 'Admin', 'System']:
        r.Trigger = trigger
    elif type == 'snippet' and group in ['Mod', 'Admin', 'System']:
        pass
    elif type == 'rule' and group in ['Admin', 'System']:
        pass
    elif type == 'meme':
        pass
    elif type == 'spotify' and group == 'System':
        r = db.Spotify(''.join(response), name, data.author.id)
    elif type == 'rss' and group == 'System':
        r = db.RSS(name, 0, response[0], response[1], response[2], response[3])
    else:
        await self.create_reaction(data.channel_id, data.id, self.emoji['failure'])
        return
    if data.attachments != [] and type not in ['rss', 'spotify']:
        r.Image = data.attachments[0].url
        r.Filename = data.attachments[0].filename
    self.db.sql.add(r)
    if 'cannedresponse':
        self.cache[data.guild_id].recompileCanned(self.db, data.guild_id)
    await self.create_reaction(data.channel_id, data.id, self.emoji['success'])

@register(group='Nitro', help='Removes from db', alias='del', category='')
async def delete(self, typeof='meme', *name, data, language, group, **kwargs):
    '''meme/cannedresponse/rule/snippet'''
    if group == 'System' and 'user' in kwargs:
        data.author.id = kwargs['user']
    session = self.db.sql.session()
    session.query(db.Snippets).filter(db.Snippets.GuildID == data.guild_id).filter(db.Snippets.UserID == data.author.id).filter(db.Snippets.Type == typeof.lower()).filter(db.Snippets.Name == ' '.join(name)).delete()
    session.commit()

@register(group='Nitro', help='Lists currently stored snippets', alias='meme, m, r, rule', category='')
async def ls(self, type='meme', *names, data, has=None, language, group, cmd, **kwargs):
    '''meme/cannedresponse/rule/snippet'''
    if cmd == 'rule' or cmd == 'r':
        if type != 'meme':
            names = list(names)+[type]
        type = 'rule'
    elif cmd == 'meme' or cmd == 'm':
        if type != 'meme':
            names = list(names)+[type]
        type = 'meme'
    if group == 'System' and 'cross' in kwargs:
            data.guild_id = kwargs['cross']
    if type == 'rule':
        if names != ():
            pattern = '> **{name}.** {response}'
        else:
            pattern = '**{name}.** {response}'
    else:
        if type in ['cannedresponse', 'snippet'] and group not in ['Mod', 'Admin', 'System']:
            return
        if names != ():
            pattern = '\n{response}'
        else:
            pattern = '{name}:\n{response}'
    r = await fetch(self, data, type.lower(), pattern, *names, has=has)
    if names != ():
        await self.message(data.channel_id, r)
        return
    rn = r.splitlines(True)
    s, f='', ''
    embed = Embed()
    for l in rn:
        if len(s + l[:2000]) < 2024:
            s += l
        else:
            if len(f+l[:1024]) < 1024:
                f += l
            else:
                embed.addField('\u200b', f)
                f = ''
    if f != '':
        embed.addField('\u200b', f)
    embed.setDescription(s).setTitle(type.title()+'s')
    await self.embed(data.channel_id, '', embed.embed)
