from MFramework.commands import register
from MFramework.database import alchemy as db
from MFramework.utils.utils import Embed
@register(group='Nitro', help='Add to store', alias='sm', category='')
async def addmeme(self, name, *message, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    r = db.Snippets()
    r.GuildID = data.guild_id
    r.UserID = data.author.id
    r.Name = name
    r.Response = ' '.join(message)
    if data.attachments != []:
        r.Image = data.attachments[0].url
        r.Filename = data.attachments[0].filename
    r.Type = 'meme'
    self.db.sql.add(r)
@register(group='Nitro', help='Fetch from store', alias='m', category='')
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

@register(group='Nitro', help='Delete from store', alias='delm', category='')
async def delmeme(self, *name, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    session = self.db.sql.session()
    session.query(db.Snippets).filter(db.Snippets.GuildID == data.guild_id).filter(db.Snippets.UserID == data.author.id).filter(db.Snippets.Name == ' '.join(name)).delete()
    session.commit()

@register(group='Nitro', help="Shows what's stored", alias='lm', category='')
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

async def fetch(self, data, typeof, newline, *names):
    session = self.db.sql.session()
    snippets = []
    for i in names:
        r = session.query(db.Snippets).filter(db.Snippets.GuildID == data.guild_id).filter(db.Snippets.Type == typeof).filter(db.Snippets.Name == i).first()
        if r == None:
            r = db.Snippets(Name=i, Response='Not found.')
        snippets += [r]
    if snippets == []:
        snippets = session.query(db.Snippets).filter(db.Snippets.GuildID == data.guild_id).filter(db.Snippets.Type == typeof).all()
    snippets = '\n'.join([newline.format(name=i.Name, response=i.Response) for i in snippets])
    if snippets == '\n':
        snippets = 'None yet.'
    return snippets


@register(group='Mod', help='Adds a Snippet', alias='a', category='')
async def add(self, typeof, name, *response, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    r = db.Snippets(data.guild_id, data.author.id, name, ' '.join(response), Type=typeof)
    if data.attachments != []:
        r.Image = data.attachments[0].url
        r.Filename = data.attachments[0].filename
    self.db.sql.add(r)
    await self.create_reaction(data.channel_id, data.id, self.emoji['success'])

@register(group='Mod', help='Adds a canned response', alias='', category='')
async def addcr(self, name, trigger, *response, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    r = db.Snippets(data.guild_id, data.author.id, name, ' '.join(response), Type='cannedresponse', Trigger=trigger)
    if data.attachments != []:
        r.Image = data.attachments[0].url
        r.Filename = data.attachments[0].filename
    self.db.sql.add(r)
    self.cache[data.guild_id].recompileCanned(self.db, data.guild_id)
    await self.create_reaction(data.channel_id, data.id, self.emoji['success'])

#Embeds, Modernise memes above, fix sending DMs, perhaps store Quotes in database? Also dockets as a sort of generic data, in Influx maybe? 
@register(group='Mod', help='Deletes a Snippet', alias='del', category='')
async def delete(self, typeof='snippet', *name, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    session = self.db.sql.session()
    session.query(db.Snippets).filter(db.Snippets.GuildID == data.guild_id).filter(db.Snippets.UserID == data.author.id).filter(db.Snippets.Type == typeof.lower()).filter(db.Snippets.Name == ' '.join(name)).delete()
    session.commit()

@register(group='Admin', help='Loads rules based on message', alias='', category='')
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

@register(group='Admin', help='Adds or updates specified rule', alias='ar', category='')
async def addRule(self, number, *rule, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    r = db.Snippets(data.guild_id, data.author.id, Name=number, Type='rule', Response=' '.join(rule))
    self.db.sql.add(r)
    await self.create_reaction(data.channel_id, data.id, self.emoji['success'])


@register(group='Nitro', help='Shows specified rule', alias='r', category='')
async def rule(self, *rule, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    r = await fetch(self, data, 'rule', '> **{name}.** {response}', *rule)
    await self.message(data.channel_id, r[:2000])
@register(group='Mod', help='Sends specified snippet', alias='ss', category='')
async def snippet(self, *name, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    r = await fetch(self, data, 'snippet', '\n{response}', *name)
    await self.message(data.channel_id, r)

@register(group='Admin', help='Adds or updates specified snippet', alias='as', category='')
async def addSnippet(self, name, *response, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    r = db.Snippets(data.guild_id, data.author.id, Name=name, Type='snippet', Response=''.join(response))
    self.db.sql.add(r)




@register(group='Nitro', help='Lists Rules', alias='lr', category='')
async def rules(self, *args, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    r = await fetch(self, data, 'rule', '**{name}.** {response}')
    rn = r.splitlines(True)
    s, f='', ''
    for l in rn:
        if len(s + l) < 2024:
            s += l
        else:
            f += l
    embed = Embed().setDescription(s).setTitle('Rules')
    if f != '':
        embed.addField('\u200b',f)
    await self.embed(data.channel_id, '', embed.embed)
@register(group='Mod', help='Lists available snippets', alias='ls', category='')
async def snippets(self, *args, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    r = await fetch(self, data, 'snippet', '{name}:\n{response}')
    embed = Embed().setDescription(r).setTitle('Snippets')
    await self.embed(data.channel_id, '', embed.embed)



@register(group='Admin', help='Create Embed, provide embed in {json} form', alias='', category='')
async def createembed(self, name, message, trigger, *embed, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    import json
    embed = json.loads(''.join(embed))
    e = db.EmbedTemplates(data.guild_id, data.author.id, name, message, embed)
    self.db.sql.add(e)

@register(group='Mod', help='Embeds', alias='', category='')
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
