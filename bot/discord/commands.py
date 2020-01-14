import asyncio, re
import inspect

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
        if 'category' not in kwargs:
            #This one should retrieve caller's category based on directory
            stack = inspect.stack()
            previous_stack_frame = stack[1]
            loc = str(previous_stack_frame.filename).split('command\\',1)
            if len(loc) > 1:
                category = loc[1].split('\\',1)[0]
#               group = loc[1].split('\\',1)[1]

        #Set group
        group = []
        if 'group' not in kwargs:
            kwargs['group'] = 'Global'
        for i in groups:
            group +=[i]
            if kwargs['group'] == i:
                break
        print(kwargs['group'],f.__name__,group)

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
        data['content'] = cmd[0] #No content, let's pass command for no reason
    #.split('!',1)[1].split(' ',1)[0]
    group = self.cache.cachedRoles(data['guild_id'],data['member']['roles'])
    group = seed[group]
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