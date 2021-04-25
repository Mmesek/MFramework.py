from MFramework import Bot, Message
from typing import List
from random import SystemRandom as random

COMMANDS = {}
def command():
    def inner(f):
        COMMANDS[f.__name__] = f
        return f
    return inner

@command
async def react(ctx: Bot, data: Message, r: List[str], x: int):
    await data.react(r[x+1])

@command
async def message(ctx: Bot, data: Message, r: List[str], x: int):
    if '{OR}' in r[x+1]:
        options = r[x+1].split('{OR}')
        content = random().choice(options)
    else:
        content = r[x+1]
    await data.reply(content.format(user_id=data.author.id, 
        username=data.author.username, nick=data.member.nick))

@command
async def delete(ctx: Bot, data: Message, r: List[str], x: int):
    await data.delete()

@command
async def chance(ctx: Bot, data: Message, r: List[str], x: int) -> int:
    if random().random() < (r[x+1]/100):
        return 0
    return 1

async def parse(ctx: Bot, data: Message):
    matched = []
    cache = ctx.cache[data.guild_id]
    for role in set(data.member.roles) & set(cache.responses["triggers"]):
        triggers = cache.responses["triggers"][role]
        for matches in triggers.finditer(data.content):
            match = matches.lastgroup
            if match in matched:
                continue
            matched.append(match)
            r = cache.responses["responses"].get(match, "").split("$")
            #session = ctx.db.sql.session()
            #models.Snippet.filter(session,
            #    type = models.types.Snippet.Regex,
            #    server_id = data.guild_id, name = match)
            should_skip = 0
            for x, command in enumerate(r):
                if should_skip > 0:
                    should_skip -= 1
                    continue
                if command not in COMMANDS:
                    continue
                command = random().choice(command.split('{OR}')).lower()
                if command == 'sleep':
                    import asyncio
                    asyncio.sleep(r[x+1])
                    continue
                should_skip = await COMMANDS[command](ctx, data, r, x) or 0
