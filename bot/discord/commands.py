import asyncio, re

from utils import timed


async def Invalid(data):
    return 0


commandList = {"Admin":{},"Mod":{},"Nitro":{},"Vip":{},"Global":{}}
helpList = {"Admin":{},"Mod":{},"Nitro":{},"Vip":{},"Global":{}}
def register(**kwargs):
    '''alias="alias"\nhelp="description of help message"\ngroup="Global|Vip|Nitro|Mod|Admin" - Default: Global'''
    def inner(f, *arg, **kwarg):
        if 'group' not in kwargs or kwargs['group'] == 'Global':
            #group = 'Global'
            group=['Admin','Mod','Nitro','Vip','Global']
        else:
            group = kwargs['group']
        if group == 'Vip':
            group=['Admin','Mod','Nitro','Vip']
        elif group == 'Nitro':
            group=['Admin','Mod','Nitro']
        elif group == 'Mod':
            group=['Admin','Mod']
        elif group == 'Admin':
            group=['Admin']
        for g in group:
            commandList[g][f"{f.__name__}"] = f
            if 'alias' in kwargs:
                commandList[group][kwargs['alias']] = f
        if 'help' in kwargs:
            helpList[group[-1]][f"{f.__name__}"] = kwargs['help']
        elif f.__doc__ != None:
            helpList[group[-1]][f"{f.__name__}"] = f.__doc__
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
    command = data['content'].split('!',1)[1].split(' ',1)[0]
    group = self.cache.cachedRoles(data['guild_id'],data['member']['roles'])
    group = seed[group]
    if await commandList[group].get(command, Invalid)(self, data) == None:
        return
    return 0

@register()
async def help(self, data):
    string = 'Commands:'
    for group in helpList:
        #Maybe show only commands for certain group/commands up to certain group?
        string+=f"\n> __{group}__:\n"
        for one in helpList[group]:
            string+=f"**!{one}** {helpList[group][one]}\n"
    print(string)
    await self.endpoints.message(data['channel_id'],string[:2000])