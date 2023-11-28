from . import base, guild


class Cache(
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
