import inspect, re
from bot.utils.utils import timed, parseMention, Embed


async def Invalid(*args, **kwargs):
    print(args, kwargs)
    # print(f"Invalid Package: {args[0]}")
    return# 0


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
        #    if 'category' not in kwargs:
        # This one should retrieve caller's category based on directory
        #        stack = inspect.stack()
        #        previous_stack_frame = stack[1]
        #        loc = str(previous_stack_frame.filename).split('command\\',1)
        #        if len(loc) > 1:
        #            category = loc[1].split('\\',1)[0]
        #               group = loc[1].split('\\',1)[1]

        # Set group
        group = []
        if "group" not in kwargs:
            kwargs["group"] = "Global"
        for i in groups:
            group += [i]
            if kwargs["group"] == i:
                break

        # Register to command's list
        for g in group:
            commandList[g][f"{f.__name__.lower()}"] = f
            if "alias" in kwargs:
                if kwargs['alias'] != '':
                    commandList[g][kwargs["alias"]] = f

        # Register help message
        sig = inspect.signature(f)
        sig = str(sig).replace('(','').replace('self, ','').replace('*args','').replace(')','').replace('**kwargs','').replace('data','').replace('*','\*').split(', ')
#        sig = [f'[{a}]' if '=' not in a else f"({a if any(n not in a.split('=',1)[1] for n in ['','0','False','None']) else a.split('=',1)[0]})" for a in sig if a is not '']
        sig = [f'[{a}]' if '=' not in a else f"({a})" if a.split('=',1)[1] not in ['0',"''",'None','False'] else f"({a.split('=',1)[0]})" for a in sig if a != '']
        helpList[group[-1]][f"{f.__name__}"] = {}
        helpList[group[-1]][f"{f.__name__}"]['sig'] = ' '.join(sig)
        if "help" in kwargs:
            helpList[group[-1]][f"{f.__name__}"]['msg'] = kwargs["help"]
            if "alias" in kwargs:
                if kwargs['alias'] != '':
                    helpList[group[-1]][f"{f.__name__}"]['alias'] = kwargs['alias']

        # Register extended help message
        if f.__doc__ != None:
            extHelpList[group[-1]][f"{f.__name__}"] = f.__doc__

        def inn(*ar, **kwar):
            r = f(*ar, **kwar)
            return r

        return inn

    return inner

def compilePatterns(self):
    patterns = {
        "strip_trigger":rf'<@[!?]{self.user_id}>|(?i)\b{self.username}\b|^{self.alias}',
        "args":r" ?\"(.*?)\" ?| ?'(.*?)' ?| ?```(.*?)``` ?| ",
        "channels":r"<#(\d+)>",
        "users":r"<@[\!?](\d+)>",
        "roles":r"<@&(\d+)>"
    }
    self.patterns={}
    for p in patterns:
        self.patterns[p] = re.compile(patterns[p], re.DOTALL | re.MULTILINE)
        print(self.patterns[p])

@timed
async def execute(self, data):
 #   data["content"] = parseMention(data["content"])
    r = 0
    if self.alias not in data["content"] and self.user_id not in data["mentions"] and self.username.lower() not in data["content"].lower():
        return 0
    elif any(word in data['content'].lower() for word in [self.alias, self.user_id, self.username.lower()]):
        #command = [c.strip() for c in re.split(rf'<@[!?]{self.user_id}>|\b{self.username}\b|{self.alias}(.*)\b',data["content"]) if c is not None and c is not '']
        command = [c.strip() for c in self.patterns['strip_trigger'].split(data["content"]) if c is not None and c != '']
        print(command,'\ncontent: ', data["content"])
        for mention in data['mentions']:
            if mention["id"] == self.user_id:
                data["mentions"].remove(mention)
    group = self.cache.cachedRoles(data["guild_id"], data["member"]["roles"])
    if data["author"]["id"] == "273499695186444289":
        group = "System"
    for cmd in command:
#        args = [t.strip() for t in re.split(r" ?\"(.*?)\" ?| ?'(.*?)' ?| ?```(.*?)``` ?| ", data['content']) if t is not None ]
        args = [t.strip() for t in self.patterns['args'].split(cmd) if t is not None ]
        cmd = cmd.split(' ',1)
        try:
            data['content'] =cmd[1]
        except:
            data['content'] = ''
        finally:
            args.pop(0)
            print('args',args)
        kwargs = {
           'data': data,
#           'channel_mentions': [t for t in re.findall(r"<#(\d+)>", data['content']) if t is not None],
#           'user_mentions': [t for t in re.findall(r"<@[\!?](\d+)>", data['content']) if t is not None],
#           'role_mentions': [t for t in re.findall(r"<@&(\d+)>", data['content']) if t is not None]}
           'channel': [t for t in self.patterns['channels'].findall(data['content']) if t is not None],
           'user_mentions': [t for t in self.patterns['users'].findall(data['content']) if t is not None],
           'role_mentions': [t for t in self.patterns['roles'].findall(data['content']) if t is not None]}
        for c in kwargs['channel']:
            for i, a in enumerate(args):
                if args[i] in ["<#>", f"<#{c}>", c]:
                    args[i] = a.replace(f'<#{c}>','').replace(c,'')
            if '' in args:
                args.remove('')
#            if '<#>' == args:
#                args.remove('<#>')
        if kwargs['channel'] == []:
            kwargs['channel'] += [data['channel_id']]
        print(cmd[0].lower(),'\n', args)
        if await commandList[group].get(cmd[0].lower(), Invalid)(self, *args, **kwargs) == None:
            r = None
        elif await parse(self, data) == None:
            r = None
    return r
    if self.user_id in data["content"]:
        # NICETOHAVE: "text !command args !command2 args2". Currently works: "text !command args" (Although "text !command args text" works only partially. OPTIONAL if anyone cares)
        command = data["content"].split(f"{self.user_id} ", 1)
#        command = re.split(rf"<@[\!?]{self.user_id}>",data["content"])
#        command = [i.strip() for i in command]
        print(command)
        for mention in data["mentions"]:
            if mention["id"] == self.user_id:
                data["mentions"].remove(mention)
    elif self.username in data["content"]:
        command = data["content"].split(f"{self.username} ", 1)
    elif self.alias in data["content"]:
        command = data["content"].split(self.alias, 1)
    try:
        cmd = command[1].split(" ", 1)
    except IndexError:
        print('Index Error :(',data['content'])
        return
    try:
        data["content"] = cmd[1]
    except:
        data["content"] = ""
    # .split('!',1)[1].split(' ',1)[0]
    group = self.cache.cachedRoles(data["guild_id"], data["member"]["roles"])
    if data["author"]["id"] == "273499695186444289":
        group = "System"

#    args = [p for p in re.split("( |\\\".*?\\\"|'.*?')", data['content']) if p.strip()] #Keep the quotes
#    args = [''.join(t) for t in re.findall(r"""([^\s"']+)|"([^"]*)"|'([^']*)'""", data['content'])] #?
#    args = [t for t in re.split(r",?\"(.*?)\",?|,?'(.*?)',?|,", data['content']) if t is not None ] #Strip the quotes
###    args = [t.strip() for t in re.split(r" ?\"(.*?)\" ?| ?'(.*?)' ?| ", data['content']) if t is not None ] #Strip the quotes
 #   args = [t for t in re.split(r",?(\".*?\"),?|,?('.*?'),?|,", data['content']) if t is not None ] #Keep the quotes
    #arguments = []
    #print(args)
    #for arg in args:
    #    print('a: ',arg)    
    #kwargs = {
    #    'channel_mentions': [t for t in re.findall(r"<#(\d+)>", data['content']) if t is not None],
    #    'user_mentions': [t for t in re.findall(r"<@[\!?](\d+)>", data['content']) if t is not None],
    #    'role_mentions': [t for t in re.findall(r"<@&(\d+)>", data['content']) if t is not None]}
    #print(kwargs)
    if await commandList[group].get(cmd[0].casefold(), Invalid)(self, data) == None:
        return
    if await parse(self, data) == None:
        return
    return 0


@register()
async def help(self, *args, data, **kwargs):
    embed=Embed().setTitle('Commands')
    embed.setDescription(
f"""Trigger can be any of: <@{self.user_id}>, `{self.username}` or `{self.alias}`
Parameters:
`[Required]`
`(optional=default value unless default is empty or 0)`
`*` Argument ends with the message. If there are any parameters after that, they either require specifing a flag or are mentions that defaults to relative user IDs that issued a command if not specified (Can be specified anywhere in message)
Arguments:
If there is a single, double quote or a code block then everything inside is treated as a single argument. Mentions won't be removed from message in that case (Unless argument is just "@mention")
If your argument contains a quote, use different quote around whole: \'`"argument go here, double quote is preserved, single is stripped"`\'
**Example:**
`!add_cc name "trigger goes here" "and 'here' is @mention response" mod`: Will answer `and 'here' is @mention response` to anyone that types `trigger goes here` and has right permission, in this example: only moderators""")
    for group in helpList:
        string = ''
        for one in helpList[group]:
            string += f"**{self.alias}{one}** {helpList[group][one]['sig']}"
            if 'msg' in helpList[group][one]:
                string+= f" - {helpList[group][one]['msg']}"
            if 'alias' in helpList[group][one]:
                string+= ' - Alias: `'+helpList[group][one]['alias']+'`'
            string+='\n'
        if string != '':
            embed.addField(group, string[:1024])
    await self.endpoints.embed(data['channel_id'], '', embed.embed)
    return
    # Commands:
    # > [Category]:
    # [trigger][command] [parameters] - [Description] #(Show only valid for user's group)
    string = "Commands:"
    for group in helpList:
        # Maybe show only commands for certain group/commands up to certain group?
        string += f"\n> __{group}__:\n"
        for one in helpList[group]:
            string += f"**{self.alias}{one}** {helpList[group][one]['msg']}\n"
            if 'alias' in helpList[group][one]:
                string+= 'Alias: `'+helpList[group][one]['alias']+'`'
    await self.endpoints.message(data["channel_id"], string[:2000])


async def parse(self, data):
    # parser:
    # $execute$command args.. # execute(data)
    # $react$reaction # endpoints.react('reaction')
    # $message$msg # endpoints.message('Message!')
    # $delete_match$ # endpoints.delete(data['id'])
    # $embed$ # endpoints.embed()
    # $role_mentionable$ $role_not_mentionable$
    if "guild_id" in data:
        server = data["guild_id"]
    else:
        server = 0
    group = self.cache.cachedRoles(data["guild_id"], data["member"]["roles"])
    if group not in self.cache.cache[server]['responses']:
        return
    words = self.cache.cache[server]["responses"][group]
    #    matches = words.findall(data['content'])
    for mo in words.finditer(data["content"]):
        match = mo.lastgroup
        response = await self.db.selectOne("Regex", "Response", "WHERE GuildID=? AND Name=?", [server, match])
        r = response[0].split("$")
        for command in r:
            if "execute" == command:
                res = self.alias + r[r.index(command) + 1]
                data["content"] = data["content"].replace(mo.group(), res)
                await execute(self, data)
            elif "react" == command:
                await self.endpoints.react(data["channel_id"], data["id"], r[r.index(command) + 1])
            elif "role_mentionable" == command:
                await self.endpoints.role_update(data["guild_id"], r[r.index(command) + 1], "True", "Regex Mention")
            elif "role_not_mentionable" == command:
                await self.endpoints.role_update(data["guild_id"], r[r.index(command) + 1], "False", "Regex Mention")
            elif "message" == command:
                await self.endpoints.message(data["channel_id"], r[r.index(command) + 1])
            elif "delete_match" == command:
                await self.endpoints.delete(data["channel_id"], data["id"], "Regex Trigger")
            elif "embed" == command:
                #
                embedName = r[r.index(command) + 1].split(' ',1)[0]
                embed = self.db.selectOne("EmbedTemplates", "Embed, Message", "WHERE GuildID=? AND Name=?",[server, embedName])[0]
                message = embed[1].replace('{mention}',f"<@{data['author']['id']}>")
                embed = embed[0]
                embed['description'] = embed['description'].replace('{}','')
                await self.endpoints.embed(data["channel_id"], message, embed)
            elif "chance" == command:
                rng = range(100)
                if rng > r[r.index(command) + 1]:
                    return 0
    return 0
