from random import SystemRandom as random

from MFramework import Bot, Message, onDispatch

COMMANDS = {}


def command(cls=None):
    def inner(f):
        COMMANDS[f.__name__] = f
        return f

    if cls:
        return inner(cls)
    return inner


@command
async def react(ctx: Bot, data: Message, r: list[str], x: int):
    await data.react(r[x + 1])


@command
async def message(ctx: Bot, data: Message, r: list[str], x: int):
    if "{OR}" in r[x + 1]:
        options = r[x + 1].split("{OR}")
        content = random().choice(options)
    else:
        content = r[x + 1]
    await data.send(content.format(user_id=data.author.id, username=data.author.username, nick=data.member.nick))


@command
async def reply(ctx: Bot, data: Message, r: list[str], x: int):
    if "{OR}" in r[x + 1]:
        options = r[x + 1].split("{OR}")
        content = random().choice(options)
    else:
        content = r[x + 1]
    await data.reply(content.format(user_id=data.author.id, username=data.author.username, nick=data.member.nick))


@command
async def delete(ctx: Bot, data: Message, r: list[str], x: int):
    await data.delete()


@command
async def chance(ctx: Bot, data: Message, r: list[str], x: int) -> int:
    if random().random() < (r[x + 1] / 100):
        return 0
    return 1


@onDispatch(event="message_create", priority=3)
async def parse(ctx: Bot, data: Message):
    matched = []
    cache = ctx.cache[data.guild_id]
    from ._utils import Groups, detect_group

    g = detect_group(ctx, data.author.id, data.guild_id, data.member.roles)
    # for role in set(data.member.roles) & set(cache.responses.keys()):
    groups = [i for i in Groups if g.can_use(i) and i.can_use(Groups.GLOBAL)]
    for group in groups:
        triggers = cache.responses.get(group, None)
        if not triggers:
            continue
        for matches in triggers.finditer(data.content):
            match = matches.lastgroup
            if ctx.cache[data.guild_id].triggers[match].cooldown:
                if await ctx.cache[data.guild_id].cooldowns.has(data.guild_id, 0, f"regex.{match}"):
                    continue
                await ctx.cache[data.guild_id].cooldowns.store(
                    data.guild_id,
                    0,
                    f"regex.{match}",
                    expire=int(ctx.cache[data.guild_id].triggers[match].cooldown.total_seconds()),
                )
            if match in matched:
                continue
            matched.append(match)
            r = cache.regex_responses.get(match, "").split("$")
            should_skip = 0
            for x, command in enumerate(r):
                if should_skip > 0:
                    should_skip -= 1
                    continue
                if command not in COMMANDS:
                    continue
                command = random().choice(command.split("{OR}")).lower()
                if command == "sleep":
                    import asyncio

                    asyncio.sleep(r[x + 1])
                    continue
                should_skip = await COMMANDS[command](ctx, data, r, x) or 0
            ctx.db.influx.commitCommandUsage(data.guild_id, f"parser-{match}", ctx.username, True, data.author.id)
