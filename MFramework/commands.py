import inspect, re
from .utils.utils import timed, Embed, replaceMultiple


async def Invalid(*args, **kwargs):
    print('Invalid')
#    print(args, kwargs)
    # print(f"Invalid Package: {args[0]}")
    return 0


groups = ["System", "Admin", "Mod", "Nitro", "Vip", "Global"]
commandList, helpList, extHelpList = {}, {}, {}

for i in groups:
    commandList.update({i: {}})
    helpList.update({i: {}})
    extHelpList.update({i: {}})


def register(**kwargs):
    """alias="alias"\nhelp="description of help message"\ngroup="Global|Vip|Nitro|Mod|Admin" - Default: Global\ncategory="Command's Category" - Default based on Directory"""

    def inner(f, *arg, **kwarg):

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
                    commandList[g][kwargs["alias"]] = f

        # Register help message
        sig = inspect.signature(f)
        s = str(sig).replace('(', '').replace('self, ', '').replace('*args', '').replace(')', '').replace('**kwargs', '').replace('*','\*').replace('group','').replace('_','\_').replace('language','')
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

        def inn(*ar, **kwar):
            r = f(*ar, **kwar)
            return r

        return inn

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
           #'flags': flags,
           'channel': [t for t in self.patterns['channels'].findall(data.content) if t is not None],
           'user_mentions': [t for t in self.patterns['users'].findall(data.content) if t is not None],
           'role_mentions': [t for t in self.patterns['roles'].findall(data.content) if t is not None]}
        for flag in flags:
            #print(flag)
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
        if await commandList[group].get(cmd[0].lower(), Invalid)(self, *args, **kwargs) == None:
            r = None
        elif await parse(self, data) == None:
            r = None
        #except Exception as ex:
            #import sys, traceback
            #print('REEEE', ex)
            #print(sys.exc_info())
            #print(traceback.extract_tb(sys.exc_info()[1], limit=-1))
    return r

Groups = {
    "Global": 0,
    "Vip": 1,
    "Nitro": 2,
    "Mod": 3,
    "Admin": 4,
    "System": 5
}

#@register(help='Sends list of commands')
async def help2(self, command=None, *category, group, data, categories=False, **kwargs):
    '''Shows detailed help message for specified command alongside it's parameters, required permission, category and example usage.\nParameters: :command: - Command to show detailed help info for - Example: command\n:category: - Categories to show commands for - Example: Category another...\n:categories: - Shows list of categories - Example: -categories'''
    if command != None and self.alias in command:
        command = command.replace(self.alias, '').lower()
        embed = Embed().setTitle('Help details for: ' + command)
        perm = None
        for _group in helpList:
            if command.casefold() in helpList[_group]:
                perm = _group
                if Groups[perm] > Groups[group]:
                    break
                category = helpList[_group][command].get('category', None)
                alias = helpList[_group][command].get('alias', None)
                sig = helpList[_group][command].get('sig', None)
                msg = helpList[_group][command].get('msg', None)
                ext = extHelpList[_group].get(command, None)
                break
        try:
            if perm is not None and Groups[perm] <= Groups[group]:
                embed.addField('Required Permission', perm, True)
            if category is not None and category != ():
                embed.addField('Category', category, True)
            if alias is not None:
                embed.addField('Alias', alias, True)
            if msg is not None:
                embed.addField('Short Description', msg)
            if sig is not None and sig != '':
                params = sig.split(' ')
                s = ''
                extparams = []
                parameters = {'Required':[], 'Optional':[], 'Multiple':[], 'Named Flag':[], 'Flag':[]}
                for param in params:
                    if '*' in param:
                        parameters['Multiple']+=[param]
                    elif '--' in param:
                        parameters['Named Flag']+=[param]
                    elif '-' in param:
                        parameters['Flag']+=[param]
                    elif '[' in param:
                        parameters['Required']+=[param]
                    elif '(' in param:
                        parameters['Optional'] += [param]
                if ext is not None:
                    ext = ext.split('Parameters: ')
                    extparams = ext[1].split('\n')
                example = self.alias + command
                orderOfParamTypes = ['Command']
                orderofParams = []
                for t in parameters:
                    if parameters[t] == []:
                        continue
                    s += '\n\n**'+t + '**:'
                    for x, param in enumerate(parameters[t]):
                        param = replaceMultiple(param, ['[', ']', '(', ')', '*', '-', '\\'],' ').strip()                        
                        if t == 'Flag':
                            orderOfParamTypes += ['Flag']
                            e ='`-'+param+'`'
                        elif t == 'Named Flag':
                            e = f'`--{param}=abc`'
                            orderOfParamTypes += ['Named Flag']
                        elif t == 'Multiple':
                            e = f'`a b c...`'
                            orderOfParamTypes += ['Multiple...']
                        else:
                            e = '`abc`'
                            if t == 'Required':
                                orderOfParamTypes += ['Required']
                            else:
                                orderOfParamTypes += ['Optional']
                        orderofParams += [param]
                        example += f' {e}'
                if extparams != []:
                    example = self.alias
                    orderOfParamTypes = []
                    for x, args in enumerate(extparams):
                        arg = args.split(' - ')
                        arg[0] = arg[0].replace(':', '').replace('  ', '')
                        if arg[0] == orderofParams[x]:
                            s+='\n'+param
                            s += ' - ' + arg[1]
                        if len(arg) > 1:
                            example += '`'+arg[2].replace('Example: ', '')+'` '
                            orderOfParamTypes += [t for t in parameters if (p for p in parameters[t] if p == arg[0])]
                example +='\n `'+'`|`'.join(orderOfParamTypes)+'`'
                embed.addField('Example Usage',example)
                embed.addField('Parameters', s[:1023])
            if ext is not None and ext[0] != '':
                embed.setDescription(ext[0][:2023].strip())
        except Exception as ex:
            print(ex)
            if perm != None:
                if Groups[perm] > Groups[group]:
                    embed.setDescription('You do not have permission to access this command.').addField('Required Permission Group', perm, True).addField('Your Permission Group', group, True)
            else:
                embed.setDescription("Command not found.")
        embed.setColor(self.cache[data.guild_id].color)
        await self.embed(data.channel_id, '', embed.embed)
        return
    elif command != None and self.alias not in command:
        category = [c for c in category]+[command]
    embed = Embed().setTitle('Commands')
    desc = f"""Trigger can be any of: <@{self.user_id}>, `{self.username}` or `{self.alias}`\n"""
    if self.cache[data.guild_id].alias != self.alias:
        desc += f"""Server's Trigger Alias is set to: `{self.cache[data.guild_id].alias}`\n"""
    desc+="""\n**Parameters:**
`[Required]`
`(optional=default value unless default is empty or 0)`
`*` Argument ends with the message. 
`(-flag)`
`(--flag=value)` provided value for flag's variable.
`[@Mention]` - Mention or Snowflake ID that defaults to relative user IDs that issued a command if not specified

**Arguments:**
If there is a single, double quote or a code block then everything inside is treated as a single argument. Mentions won't be removed from message in that case (Unless argument is just "@mention")
If your argument contains a quote, use different quote around whole: \'`"argument go here, double quote is preserved, single is stripped"`\'
Flags are removed from argument list therefore can be specifed anywhere

**Example: ** """+f"""
`{self.alias}add_cc name "trigger goes here" "and 'here' is @mention response" mod`: Will answer `and 'here' is @ mention response` to anyone that types `trigger goes here` and has right permission, in this example: only moderators """
    embed.setDescription(desc)
    g = group
    category = [c.lower().capitalize() for c in category]
    lower = False
    c = {}
    for group in helpList:
        if group == g:
            lower = True
        elif lower == False:
            continue
        string = ''
        for one in helpList[group]:
        # Maybe show only commands for certain group/commands up to certain group?
            cat = helpList[group][one].get('category', None)
            if categories and cat not in c.get(group, {}):
                string += f"{cat}\n"
                if group not in c:
                    c[group] = []
                c[group]+=[cat]
            elif categories is False and (cat != None and cat in category or len(category) == 0):
                string += f"**{self.alias}{one}** {helpList[group][one]['sig']}"
                if 'msg' in helpList[group][one]:
                    string+= f" - {helpList[group][one]['msg']}"
                if 'alias' in helpList[group][one]:
                    string+= ' - Alias: `'+helpList[group][one]['alias']+'`'
                string+='\n'
        if string != '':
            embed.addField(group, string[:1024])
    if categories:
        embed.setDescription('').setTitle('Available Categories')
    embed.setColor(self.cache[data.guild_id].color)
    await self.embed(data.channel_id, '', embed.embed)


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
        if group not in self.cache[server].responses:
            continue
        words = self.cache[server].responses[each]
        #words = self.cache[server].responses[group]
        #matches = words.findall(data['content'])
        for matches in words.finditer(data.content):
            match = matches.lastgroup
            session = self.db.sql.session()
            response = session.query(db.Regex).filter(db.Regex.GuildID == server).filter(db.Regex.Name == match).first()
            r = response[0].split('$')
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
