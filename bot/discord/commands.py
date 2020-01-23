import asyncio, re
#import inspect

from bot.utils import timed, parseMention


async def Invalid(*args):
    #print(f"Invalid Package: {args[0]}")
    return 0

groups = ["System","Admin","Mod","Nitro","Vip","Global"]
commandList, helpList, extHelpList = {}, {}, {}

for i in groups:
    commandList.update({i:{}})
    helpList.update({i:{}})
    extHelpList.update({i:{}})

def register(**kwargs):
    '''alias="alias"\nhelp="description of help message"\ngroup="Global|Vip|Nitro|Mod|Admin" - Default: Global\ncategory="Command's Category" - Default based on Directory'''
    def inner(f, *arg, **kwarg):

        #Set Category
    #    if 'category' not in kwargs:
            #This one should retrieve caller's category based on directory
    #        stack = inspect.stack()
    #        previous_stack_frame = stack[1]
    #        loc = str(previous_stack_frame.filename).split('command\\',1)
    #        if len(loc) > 1:
    #            category = loc[1].split('\\',1)[0]
#               group = loc[1].split('\\',1)[1]

        #Set group
        group = []
        if 'group' not in kwargs:
            kwargs['group'] = 'Global'
        for i in groups:
            group +=[i]
            if kwargs['group'] == i:
                break

        #Register to command's list
        for g in group:
            commandList[g][f"{f.__name__}"] = f
            if 'alias' in kwargs:
                commandList[group][kwargs['alias']] = f

        #Register help message
        if 'help' in kwargs:
            helpList[group[-1]][f"{f.__name__}"] = kwargs['help']

        #Register extended help message
        if f.__doc__ != None:
            extHelpList[group[-1]][f"{f.__name__}"] = f.__doc__

        def inn(*ar, **kwar):
            r = f(*ar, **kwar)
            return r
        return inn
    return inner
    

seed = {
    1:"Admin",
    2:"Mod",
    3:"Nitro",
    4:"Vip",
    5:"Global"
}
async def execute(self, data):
    data['content'] = parseMention(data['content'])
    try: #NICETOHAVE: "text !command args !command2 args2". Currently works: "text !command args" (Although "text !command args text" works only partially. OPTIONAL if anyone cares)
        command = data['content'].split(f'{self.user_id} ',1)[1]
        for mention in data['mentions']:
            if mention['id'] == self.user_id:
                data['mentions'].remove(mention)
    except:
        command = data['content'].split(f'!',1)[1]
    cmd = command.split(' ',1)
    try:
        data['content'] = cmd[1]
    except:
        data['content'] = ''#cmd[0] #No content, let's pass command for no reason
    #.split('!',1)[1].split(' ',1)[0]
    group = self.cache.cachedRoles(data['guild_id'],data['member']['roles'])
    group = seed[group]
    if data['author']['id'] == '273499695186444289':
        group = 'System'
    if await commandList[group].get(cmd[0], Invalid)(self, data) == None:
        return
    return 0

@register()
async def help(self, data):
    #Commands: 
    #> [Category]: 
    #[trigger][command] [parameters] - [Description] #(Show only valid for user's group)
    string = 'Commands:'
    for group in helpList:
        #Maybe show only commands for certain group/commands up to certain group?
        string+=f"\n> __{group}__:\n"
        for one in helpList[group]:
            string+=f"**!{one}** {helpList[group][one]}\n"
    print(string)
    await self.endpoints.message(data['channel_id'],string[:2000])

def patternsFromCache(server, user):
    return []
def getResponseFromDatabase(server, match):
    return ''

async def rege(self, data):
    #parser: 
    # $execute$command args.. # execute(data) 
    # $react$reaction # endpoints.react('reaction') 
    # $message$msg # endpoints.message('Message!')
    # $delete_match$ # endpoints.delete(data['id'])
    # $embed$ # endpoints.embed()
    # $role_mentionable$ $role_not_mentionable$
    if 'guild_id' in data:
        server = data['guild_id']
    else:
        server = 0
    words = patternsFromCache(data['guild_id'], data['author']['id']) 
#    words = getFromDatabase(server)
    #dicti={'the':20, 'a':10, 'over':2}
    #patterns=['the', 'an?'] 
    #regex_matches = [re.compile("^"+pattern+"$").match for pattern in patterns]
    #extractddicti= {k:v for k,v in dicti.items() if any (regex_match(k) for regex_match in regex_matches)} 
    #matches = [re.compile(pattern).match for pattern in patterns]
    longest_first = sorted(words, key=len, reverse=True)
    p = re.compile(r'(?:{})'.format('|'.join(map(re.escape, longest_first))))
    matches = p.findall(data['content'])
    if matches != []:
        for match in matches:
            response = getResponseFromDatabase(server, match)
            r = response.split('$')
            for command in r:
                if 'execute' == r:
                    res = '!'+r[r.index(command)+1]#.replace('','!')
                    data['content'] = data['content'].replace(match,res)
                    await execute(self, data)
                elif 'react' == r:
                    await self.endpoints.react(data['channel_id'], data['id'], r[r.index(command)+1])
                elif 'role_mentionable' == r:
                    await self.endpoints.role_update(data['guild_id'],r[r.index(command)+1],'True','Regex Mention')
                elif 'role_not_mentionable' == r:
                    await self.endpoints.role_update(data['guild_id'],r[r.index(command)+1],'False','Regex Mention')
                elif 'message' == r:
                    await self.endpoints.message(data['channel_id'], r[r.index(command)+1])
                elif 'delete_match' == r:
                    await self.endpoints.delete(data['channel_id'],data['id'],'Regex Trigger')
                elif 'embed' == r:
                    #
                    await self.endpoints.embed(data['channel_id'],'','')

