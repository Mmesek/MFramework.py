import inspect, re
from .utils.utils import timed


async def Invalid(*args, **kwargs):
    return 0


groups = ["System", "Admin", "Mod", "Nitro", "Vip", "Global", "dm"]
commandList, helpList, extHelpList = {}, {}, {}
contextCommandList = {}

for i in groups:
    commandList.update({i: {}})
    helpList.update({i: {}})
    extHelpList.update({i: {}})
    contextCommandList.update({i: {}})

class Register:
    def __init__(self):
        pass
    def __call__(cls, group='Global', category='Uncategorized', alias='', help='', *args, **kwargs):
        def inner(cls, *args, **kwargs):
            cmds = [a.strip() for a in alias.split(',')] + [cls.__name__.lower()]
            name = str(cls.__name__.lower())

            for i in groups:
                if group == 'dm' and i != 'dm':
                    continue
                for cmd in cmds:
                    if cmd == '':
                        continue
                    contextCommandList[i][cmd] = cls
                if group.capitalize() == i:
                    break
            
            sig = inspect.signature(cls)
            s = str(sig).replace('(', '').replace('self, ', '').replace('*args', '').replace(')', '').replace('**kwargs', '').replace('*','\*').replace('group','').replace('_','\_').replace('language','').replace('cmd','').replace('bot','')
            si = s.split('data, ')
            sig = si[0].split(', ')
            sig = [f'[{a}]' if '=' not in a else f"({a})" if a.split('=', 1)[1] not in ['0', "''", 'None', 'False'] else f"({a.split('=',1)[0]})" for a in sig if a != '']
            s = si[1].split(', ') if len(si) > 1 else ''
            sig += [f"(-{i.split('=')[0]})" if '=False' in i else f"(--{i.split('=')[0]})" if '=' in i else f'[@{i}]' for i in s if i != '']

            methods = inspect.getmembers(cls, predicate=inspect.isfunction)
            methods = [i[0] for i in methods if i[0] not in ['__init__', 'execute', 'iterate', 'end']]

            helpList[group][name] = {}
            if help != '':
                helpList[group][name]['msg'] = help
            if alias != '':
                helpList[group][name]['alias'] = alias
            helpList[group][name]['category'] = category.capitalize()
            helpList[group][name]['sig'] = ' '.join(sig)
            if cls.__doc__ != None:
                extHelpList[group][name] = cls.__doc__
            helpList[group][name]['sub'] = methods

            return cls
        return inner
ctxRegister = Register()

class BaseCtx:
    def __init__(self, *args, bot, data, **kwargs):
        self.channel = data.channel_id
        self.user = data.author.id
        self.currentStep = 0
        if data.guild_id == 0:
            self.guild_id = 'dm'
            self.guild = 463433273620824104
        else:
            self.guild_id = data.guild_id
            self.guild = data.guild_id
        self.bot = bot
        print('Init BaseCtx for', self.channel, self.user)
    async def execute(self, *args, data, **kwargs):
        print("Execute wasn't implemented")
        print(self)
        print(args)
        print(data)
        print(kwargs)
    def iterate(self):
        #print('iterating')
        self.currentStep += 1
    async def end(self, *args, **kwargs):
        #print(args)
        #print(kwargs)
        self.bot.context[self.guild_id].pop((self.channel, self.user))
        print('Context Ended. Clean should go there')



def register(**kwargs):
    """alias="alias"\nhelp="description of help message"\ngroup="Global|Vip|Nitro|Mod|Admin" - Default: Global\ncategory="Command's Category" - Default based on Directory"""

    def inner(f, *arg, **kwarg):
        if 'notImpl' in kwargs:
            return

        # Set Category
        if 'category' not in kwargs or 'group' not in kwargs:
        # This one should retrieve caller's category based on directory
            stack = inspect.stack()
            previous_stack_frame = stack[1]
            try:
                loc = str(previous_stack_frame.filename).replace('\\','/').split('commands_reworked/',1)[1].split('/', 1)
                category = loc[0]
                kwargs['category'] = category
                if 'group' not in kwargs:
                    group=loc[1][:-3]
                if group.capitalize() not in groups:
                    group = 'Global'
                kwargs['group'] = group.capitalize()
            except:
                pass

        # Set group
        group = []
        if "group" not in kwargs:
            kwargs["group"] = "Global"
        for i in groups:
            group += [i]
            if kwargs["group"].capitalize() == i:
                break

        # Register to command's list
        for g in group:
            commandList[g][f"{f.__name__.lower()}"] = f
            if "alias" in kwargs:
                if kwargs['alias'] != '':
                    a = kwargs['alias'].split(',')
                    for i in a:
                        commandList[g][i.strip()] = f

        # Register help message
        sig = inspect.signature(f)
        s = str(sig).replace('(', '').replace('self, ', '').replace('*args', '').replace(')', '').replace('**kwargs', '').replace('*','\*').replace('group','').replace('_','\_').replace('language','').replace('cmd','')
        si = s.split('data, ')
        sig = si[0].split(', ')
        sig = [f'[{a}]' if '=' not in a else f"({a})" if a.split('=', 1)[1] not in ['0', "''", 'None', 'False'] else f"({a.split('=',1)[0]})" for a in sig if a != '']
        s = si[1].split(', ')
        sig += [f"(-{i.split('=')[0]})" if '=False' in i else f"(--{i.split('=')[0]})" if '=' in i else f'[@{i}]' for i in s if i != '']
        helpList[group[-1]][f"{f.__name__}"] = {}
        helpList[group[-1]][f"{f.__name__}"]['sig'] = ' '.join(sig)
        if 'category' not in kwargs or kwargs['category'] == '':
            kwargs['category'] = 'Uncategorized'
        helpList[group[-1]][f"{f.__name__}"]['category'] = kwargs['category'].capitalize()
        if "help" in kwargs:
            helpList[group[-1]][f"{f.__name__}"]['msg'] = kwargs["help"]
            if "alias" in kwargs:
                if kwargs['alias'] != '':
                    helpList[group[-1]][f"{f.__name__}"]['alias'] = kwargs['alias']

        # Register extended help message
        if f.__doc__ != None:
            extHelpList[group[-1]][f"{f.__name__}"] = f.__doc__
        
        #with open('commands.json', 'r') as file:
        #    translated = json.load(file)
        #    if f.__name__ not in translated:
        #        with open('commands_.json','a',newline='',encoding='utf-8') as file:
        #            s = f'    "{f.__name__}' + '":{\n'
        #            s += f'        "cmd_trigger":"{f.__name__}"'
        #            for a in sig:
        #                a = a.split('=', 1)[0]
        #                a = replaceMultiple(a, ['[',']','(',')','*','-','\\'], '')
        #                s+=f',\n        "{a}":"{a}"'
        #            if 'alias' in kwargs and kwargs['alias'] != '':
        #                s += f',\n        "alias":"{kwargs["alias"]}"'
        #            if 'help' in kwargs and kwargs['help'] != '':
        #                s += f',\n        "help":"{kwargs["help"]}"'
        #            if f.__doc__ != None:
        #                s += f',\n        "extHelp":"'+f.__doc__.replace("\n","/n")+'"'
        #            s += "\n    },\n"
        #            file.write(s)

        return f

    return inner

def compilePatterns(self):
    patterns = {
        "strip_trigger":rf'<@[!?]{self.user_id}>|(?i)\b{self.username}\b|^{re.escape(self.alias)}',
        "args":r" ?\"(.*?)\" ?| ?'(.*?)' ?| ?```(.*?)``` ?| ",
        "channels":r"<#(\d+)>",
        "users":r"<@[\!?](\d+)>",
        "roles":r"<@&(\d+)>"
    }
    self.patterns={}
    for p in patterns:
        self.patterns[p] = re.compile(patterns[p], re.DOTALL | re.MULTILINE)

@timed
async def execute(self, data):
    if self.patterns['strip_trigger'].search(data.content) == None:
        return None
    command = [c.strip() for c in self.patterns['strip_trigger'].split(data.content)[1:] if c is not None and c != '']
    #print(command,'content:', data.content)
    
    for mention in data.mentions:
        if mention.id == self.user_id:
            data.mentions.remove(mention)
    r = 0
    
    if data.author.id != 273499695186444289:
        group = self.cache[data.guild_id].cachedRoles(data.member.roles)
    else:
        group = "System"
    
    for cmd in command:
        flags = {}
        if ' --' in cmd and '=' in cmd:
            flags_ = cmd.split(' --')[1:]
            for flag in flags_:
                f = flag.split(' ')[0]
                cmd = cmd.replace(' --'+f,'')
                flg = f.split('=')
                flag_name = flg[0]
                flag_arg = flg[1]
                flags[flag_name] = flag_arg

        if ' -'in cmd:
            bool_flags = cmd.split(' -')[1:]
            for flag in bool_flags:
                f = flag.split(' ')[0]
                cmd = cmd.replace(' -'+f,'')
                flags[f] = True
            
        args = [t.strip() for t in self.patterns['args'].split(cmd) if t is not None and t != '']
        cmd = cmd.split(' ',1)
        try:
            data.content =cmd[1]
        except:
            data.content = ''
        finally:
            args.pop(0)
        
        kwargs = {
           'data': data,
           'group': group,
           'language': self.cache[data.guild_id].language,
           'cmd': cmd[0].lower(),
           #'flags': flags,
           'channel': [t for t in self.patterns['channels'].findall(data.content) if t is not None],
           'user_mentions': [t for t in self.patterns['users'].findall(data.content) if t is not None],
           'role_mentions': [t for t in self.patterns['roles'].findall(data.content) if t is not None]}
        for flag in flags:
            kwargs[flag] = flags[flag]
        
        for c in kwargs['channel']:
            for i, a in enumerate(args):
                if args[i] in ["<#>", f"<#{c}>", c]:
                    args[i] = a.replace(f'<#{c}>','').replace(c,'')
            if '' in args:
                args.remove('')
        
        if kwargs['channel'] == []:
            kwargs['channel'] += [data.channel_id]

        print('Cmd:   ', cmd[0].lower())
        print('args:  ',args)
        print('kwargs:', kwargs)
        #try:
        if cmd[0].lower() in contextCommandList[group]:
            self.context[data.guild_id][(data.channel_id, data.author.id)] = contextCommandList[group].get(cmd[0].lower())(*args, bot=self, **kwargs)
            await self.context[data.guild_id][(data.channel_id, data.author.id)].execute(data=data)
            r = None
        elif await commandList[group].get(cmd[0].lower(), Invalid)(self, *args, **kwargs) == None:
            r = None
        #elif await parse(self, data) == None:
            #r = None
    return r

Groups = {
    "Global": 0,
    "Vip": 1,
    "Nitro": 2,
    "Mod": 3,
    "Admin": 4,
    "System": 5
}

from .database import alchemy as db
#@timed
async def parse(self, data):
    # parser:
    # $execute$command args.. # execute(data)
    # $react$reaction # react('reaction')
    # $message$msg # message('Message!')
    # $delete_match$ # delete(data['id'])
    # $embed$ # embed()
    # $role_mentionable$ $role_not_mentionable$
    server = data.guild_id
    group = self.cache[server].cachedRoles(data.member.roles)
    if group == 'Muted':
        return
    for each in Groups:
        if Groups[each] > Groups[group]:
            break
        #print('Group', Groups[each],'<=', group,'(',Groups[group],')','=',each)
        if each not in self.cache[server].responses:
            continue
        words = self.cache[server].responses[each]
        #words = self.cache[server].responses[group]
        #matches = words.findall(data['content'])
        for matches in words.finditer(data.content):
            match = matches.lastgroup
            session = self.db.sql.session()
            response = session.query(db.Regex).filter(db.Regex.GuildID == server).filter(db.Regex.Name == match).first()
            r = response.Response.split('$')
            for command in r:
                if "execute" == command:
                    res = self.alias + r[r.index(command) + 1]
                    data.content = data.content.replace(match.group(), res)
                    await execute(self, data)
                elif "react" == command:
                    await self.react(data.channel_id, data.id, r[r.index(command) + 1])
                elif "role_mentionable" == command:
                    await self.role_update(data.guild_id, r[r.index(command) + 1], "True", "Regex Mention")
                elif "role_not_mentionable" == command:
                    await self.role_update(data.guild_id, r[r.index(command) + 1], "False", "Regex Mention")
                elif "message" == command:
                    await self.message(data.channel_id, r[r.index(command) + 1])
                elif "delete_match" == command:
                    await self.delete(data.channel_id, data.id, "Regex Trigger")
                elif "embed" == command:
                    embedName = r[r.index(command) + 1].split(' ',1)[0]
                    embed = self.db.selectOne("EmbedTemplates", "Embed, Message", "WHERE GuildID=? AND Name=?",[server, embedName])[0]
                    message = embed[1].replace('{mention}',f"<@{data.author.id}>")
                    embed = embed[0]
                    embed['description'] = embed['description'].replace('{}','')
                    await self.embed(data.channel_id, message, embed)
                elif "chance" == command:
                    rng = range(100)
                    if rng > r[r.index(command) + 1]:
                        return 0
    return 0
