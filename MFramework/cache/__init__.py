from MFramework import log

from . import base, guild


class Cache(
    guild.Localization,
    guild.Logging,
    guild.GuildCache,
    guild.BotMeta,
    guild.ObjectCollections,
    base.RuntimeCommands,
    base.Commands,
    base.Base,
    base.BasicCache,
):
    pass


def check(cache: Cache):
    attrs = []
    for attr in cache.__class__.__bases__:
        for a in attr.__annotations__:
            attrs.append(a)
    missing = [a for a in attrs if not hasattr(cache, a)]
    if missing:
        log.log(5, "Missing attributes %s", ", ".join(missing))
