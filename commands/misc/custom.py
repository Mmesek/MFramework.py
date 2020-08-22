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
                snippets += [db.Snippets(Name=j.Name, Response=j.Response, Image=j.Image) for j in r]
                continue
            else:
                r = None
        #if r == None:
            #r = db.Snippets(Name=i, Response='Not found.')
        if r != None:
            snippets += [r]
    if snippets == []:
        snippets = [session.query(db.Snippets).filter(db.Snippets.GuildID == data.guild_id).filter(db.Snippets.Type == typeof).filter(db.Snippets.Name == ' '.join(names)).first()]
    if snippets == [] or snippets is None or snippets == [None]:
        if names != ():
            return 'For a list of available ' + typeof + 's do not provide any arguments'
        else:
            snippets = session.query(db.Snippets).filter(db.Snippets.GuildID == data.guild_id).filter(db.Snippets.Type == typeof).all()
    if snippets == [] or snippets is None:
        return "Not found"
    try:
        snippets = sorted(snippets, key=lambda x: int(x.Name))
    except:
        snippets = sorted(snippets, key=lambda x: x.Name)
    s = []
    for i in snippets:
        ff = ''
        if i.Response:
            o = i.Response.split(' ')
            for j in o:
                if len(snippets) > 1 and '/' in j and '/' not in j[-1]:
                    ff += ' '+j.split('/')[-1]
                else:
                    ff += ' ' + j
        if len(snippets) > 1 and i.Image and '/' in i.Image:
            ff += i.Image.split('/')[-1]
        s+=[db.Snippets(Name=i.Name, Response=ff)]
    #snippets = '\n'.join([newline.format(name=i.Name, response=f"{' '.join([o.split('/')[-1] for o in i.Response.split(' ')]) if '/' in i.Response else i.Response} {i.Image.split('/')[-1] if '/' in i.Image else i.Image}" if i.Image else i.Response) for i in snippets])
    snippets = '\n'.join([newline.format(name=i.Name, response=i.Response) for i in s])
    if snippets == '\n':
        snippets = 'None yet.'
    return snippets


@register(group='Admin', help='Loads rules based on message. Default detects "🔸 **1.** Rule" as separate rule', alias='', category='')#, notImpl=True)
async def loadRules(self, messagelink, separate_rules='🔸', rule_nr_ends_with=".**", *args, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    link = messagelink.split('/')[-2:]
    channel = link[0]
    message = link[1]
    msg = await self.get_channel_message(channel, message)
    lines = msg.content.split(separate_rules)
    s = self.db.sql.session()
    for line in lines:
        print(line)
        if rule_nr_ends_with in line:
            line = line.split(rule_nr_ends_with)
            name = line[0].replace('**','').strip()
            response = line[1].strip()
            r = db.Snippets(data.guild_id, data.author.id, name, response, Type='rule')
            s.merge(r)#add(r)
    return s.commit()

@register(group='Admin', help='Create Embed, provide embed in {json} form', alias='', category='', notImpl=True)
async def createembed(self, name, message, trigger, *embed, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    import json
    embed = json.loads(''.join(embed))
    e = db.EmbedTemplates(data.guild_id, data.author.id, name, message, embed)
    self.db.sql.add(e)

@register(group='Mod', help='Embeds', alias='', category='')#, notImpl=True)
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
    await self.embed(data.channel_id, r.Message, embed, {'parse':['roles']})


@register(group='Nitro', help='Adds to db', alias='sm', category='')
async def add(self, name, *response, data, trigger='', type='meme', language, group, **kwargs):
    '''meme/cannedresponse/rule/snippet/spotify/rss/regex
    if rss: response = [uri color lang avatar_url]
    if regex: response = [trigger required_role response]'''
    r = db.Snippets(data.guild_id, data.author.id, name, ' '.join(response), Type=type)
    if response == () and data.attachments == [] and type != 'spotify':
        await self.create_reaction(data.channel_id, data.id, self.emoji['failure'])
        return
    if type == 'cannedresponse' and group in ['Mod', 'Admin', 'System']:
        r.Trigger = trigger
    elif type == 'snippet' and group in ['Mod', 'Admin', 'System']:
        pass
    elif type == 'rule' and group in ['Admin', 'System']:
        pass
    elif type == 'meme':
        pass
    elif type == 'spotify' and group == 'System':
        from MFramework.utils.api import Spotify
        s = Spotify()
        await s.connect()
        res = await s.search(''.join(' '.join([name]+list(response))))
        sid = res['artists']['items'][0]['id']
        await self.message(data.channel_id, f"Added Artist {res['artists']['items'][0]['name']} with SpotifyID {sid}")
        await s.disconnect()
        r = db.Spotify(sid, name+' '+' '.join(response), data.author.id)
    elif type == 'rss' and group == 'System':
        from MFramework.utils.utils import get_main_color
        from MFramework.utils import favicon
        av = favicon.get('/'.join(response[0].split('/')[:3]))        
        color = get_main_color(av[0].url)
        if '.pl' in response[0]:
            lang = 'pl'
        else:
            lang = 'en'
        r = db.RSS(name, 0, response[0], color, lang, av[0].url)
    elif type == 'regex' and group == 'System':
        r = db.Regex(data.guild_id, data.author.id, name, response[0], ' '.join(response[2]), response[1])
    else:
        await self.create_reaction(data.channel_id, data.id, self.emoji['failure'])
        return
    if data.attachments != [] and type not in ['rss', 'spotify']:
        r.Image = data.attachments[0].url
        r.Filename = data.attachments[0].filename
    self.db.sql.add(r)
    if 'cannedresponse':
        self.cache[data.guild_id].recompileCanned(self.db, data.guild_id)
    elif 'regex':
        self.cache[data.guild_id].recompileTriggers(self.db, data.guild_id)
    await self.create_reaction(data.channel_id, data.id, self.emoji['success'])

@register(group='Nitro', help='Removes from db', alias='del, rm', category='')
async def delete(self, *name, data, typeof='meme', user='', language, group, **kwargs):
    '''meme/cannedresponse/rule/snippet'''
    if group in ['System','Admin'] and user!='':
        data.author.id = user
    session = self.db.sql.session()
    session.query(db.Snippets).filter(db.Snippets.GuildID == data.guild_id).filter(db.Snippets.UserID == data.author.id).filter(db.Snippets.Type == typeof.lower()).filter(db.Snippets.Name == ' '.join(name)).delete()
    session.commit()
    await self.create_reaction(data.channel_id, data.id, self.emoji['success'])

@register(group='Nitro', help='Lists currently stored snippets', alias='meme, m, r, rule, s, snippet', category='')
async def ls(self, type='meme', *names, data, has=None, language, group, cmd, **kwargs):
    '''meme/cannedresponse/rule/snippet'''
    if cmd == 'rule' or cmd == 'r':
        if type != 'meme':
            names = [type]+list(names)
        type = 'rule'
    elif cmd == 'meme' or cmd == 'm':
        if type != 'meme':
            names = [type]+list(names)
        type = 'meme'
    elif cmd == 's' or cmd == 'snippet':
        if type != 'meme':
            names = [type] + list(names)
        type = 'snippet'
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
            pattern = '- {name}:\n{response}\n'
    r = await fetch(self, data, type.lower(), pattern, *names, has=has)
    if names != ():
        await self.message(data.channel_id, r, allowed_mentions={"parse":[]})
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
                if f !='':
                    embed.addField('\u200b', f)
                    f = ''
    if f != '':
        embed.addField('\u200b', f)
    embed.setDescription(s).setTitle(type.title()+'s')
    await self.embed(data.channel_id, '', embed.embed)

@register(group='Nitro', help='Edits entry', alias='em', category='')
async def edit(self, name, *new_response, data, trigger='', type='meme', language, **kwargs):
    '''Extended description to use with detailed help command'''
    pass

@register(group='Nitro', help='Create self role. Only one per booster', alias='', category='')
async def role(self, hex_color, *name, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    s = self.db.sql.session()
    c = s.query(db.CustomRoles).filter(db.CustomRoles.GuildID == data.guild_id).filter(db.CustomRoles.UserID == data.author.id).first()
    if name == () and c is not None:
        name = c.Name
    else:
        name = ' '.join(name)
    reserved_colors = []
    reserved_names = []
    groups = self.cache[data.guild_id].groups
    for _role in self.cache[data.guild_id].roles:
        if _role.id in groups['Admin'] or _role.id in groups['Mod']:
            reserved_colors.append(_role.color)
            reserved_names.append(_role.name.lower())
        elif _role.id in groups['Nitro']:
            nitro_position = _role.position
    try:
        color = int(hex_color.strip('#'), 16)
    except ValueError as ex:
        await self.create_reaction(data.channel_id, data.id, self.emoji['failure'])
        return await self.message(data.channel_id, "Color has to be provided as a hexadecimal value (between 0 to F for example `#012DEF`) not `"+ str(ex).split(": '")[-1].replace("'","`"))
    if color in reserved_colors:
        await self.message(data.channel_id, "Color is too similiar to admin colors")
        color = None
    if name.lower() in reserved_names:
        return await self.message(data.channel_id, "Sorry, choose different name")
    if c != None:
        await self.modify_guild_role(data.guild_id, c.RoleID, name, 0, color=color, audit_reason="Updated Role of Nitro user")
        role = c.RoleID
    else:
        role = await self.create_guild_role(data.guild_id, name, 0, color, False, False, "Created Role for Nitro user "+data.author.username)
        role = role.id
        nitro_position = 1
        await self.modify_guild_role_positions(data.guild_id, role, nitro_position)
        await self.add_guild_member_role(data.guild_id, data.author.id, role)
    
    r = db.CustomRoles(data.guild_id, data.author.id, name, color, role)
    if c != None:
        s.merge(r)
    else:
        self.db.sql.add(r)
    await self.create_reaction(data.channel_id, data.id, self.emoji['success'])
