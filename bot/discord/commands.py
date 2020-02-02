import asyncio, re

# import inspect
from bot.utils.utils import timed, parseMention


async def Invalid(*args):
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
                commandList[g][kwargs["alias"]] = f

        # Register help message
        if "help" in kwargs:
            helpList[group[-1]][f"{f.__name__}"] = kwargs["help"]

        # Register extended help message
        if f.__doc__ != None:
            extHelpList[group[-1]][f"{f.__name__}"] = f.__doc__

        def inn(*ar, **kwar):
            r = f(*ar, **kwar)
            return r

        return inn

    return inner


async def execute(self, data):
    data["content"] = parseMention(data["content"])
    if "!" not in data["content"] and self.user_id not in data["content"] and self.username not in data["content"]:
        return 0
    if self.user_id in data["content"]:
        # NICETOHAVE: "text !command args !command2 args2". Currently works: "text !command args" (Although "text !command args text" works only partially. OPTIONAL if anyone cares)
        command = data["content"].split(f"{self.user_id} ", 1)[1]
        for mention in data["mentions"]:
            if mention["id"] == self.user_id:
                data["mentions"].remove(mention)
    elif self.username in data["content"]:
        command = data["content"].split(f"{self.username} ", 1)[1]
    elif "!" in data["content"]:
        command = data["content"].split(f"!", 1)[1]
    cmd = command.split(" ", 1)
    try:
        data["content"] = cmd[1]
    except:
        data["content"] = ""
    # .split('!',1)[1].split(' ',1)[0]
    group = self.cache.cachedRoles(data["guild_id"], data["member"]["roles"])
    if data["author"]["id"] == "273499695186444289":
        group = "System"
    if await commandList[group].get(cmd[0].casefold(), Invalid)(self, data) == None:
        return
    if await parse(self, data) == None:
        return
    return 0


@register()
async def help(self, data):
    # Commands:
    # > [Category]:
    # [trigger][command] [parameters] - [Description] #(Show only valid for user's group)
    string = "Commands:"
    for group in helpList:
        # Maybe show only commands for certain group/commands up to certain group?
        string += f"\n> __{group}__:\n"
        for one in helpList[group]:
            string += f"**!{one}** {helpList[group][one]}\n"
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
    words = self.cache.cache[server]["responses"][group]
    #    matches = words.findall(data['content'])
    for mo in words.finditer(data["content"]):
        match = mo.lastgroup
        response = await self.db.selectOne("Regex", "Response", "WHERE GuildID=? AND Name=?", [server, match])
        r = response[0].split("$")
        for command in r:
            if "execute" == command:
                res = "!" + r[r.index(command) + 1]
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
                await self.endpoints.embed(data["channel_id"], "", "")
    return 0
