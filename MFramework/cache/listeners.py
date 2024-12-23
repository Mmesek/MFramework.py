import time

from mdiscord.types import Gateway_Events
from mdiscord.websocket.opcodes import DISPATCH

from MFramework import Bot, Guild, log, onDispatch

from . import check
from ._internal import models


@onDispatch
async def guild_create(bot: Bot, guild: Guild):
    if guild.id not in bot.cache:
        start = time.time()
        bot.cache[guild.id] = bot._Cache(bot=bot, guild=guild)
        async with bot.db.sql.session() as session:
            await bot.cache[guild.id].initialize(bot=bot, session=session, guild=guild)
        check(bot.cache[guild.id])
        log.info("Guild %s initialized in %s", guild.id, time.time() - start)
    if await bot.cache[guild.id].members.length() < 50:
        await bot.request_guild_members(guild.id)


methods = {
    "add": "update",
    "delete": "delete",
    "delete_bulk": "delete",
    "remove": "delete",
    "create": "store",
    "chunk": "update",
}

collections = {
    "guild_member": "members",
    "message": "messages",
    "channel": "channels",
    "guild_role": "roles",
}

attributes = {
    "guild_members_chunk": ".members",
    "guild_member_remove": ".user.id",
    "guild_role_create": ".role",
    "guild_role_update": ".role",
    "guild_role_remove": ".role_id",
    "message_delete": ".id",
}


def create_cache_listeners(Cache: object):
    for event in Gateway_Events:
        if not hasattr(event.func, "guild_id"):
            continue
        if any(i.__name__ == "_autocache" for i in DISPATCH.get(event.name.upper(), {}).get(200, [])):
            continue
        collection, method = event.name.rsplit("_", 1)
        collection = collections.get(
            collection[:-1].lower() if collection.endswith("s") else collection.lower(),
            collection.lower(),
        ).lower()

        if not hasattr(Cache, collection):
            continue
        elif not isinstance(getattr(Cache, collection), models.Collection):
            continue
        method = methods.get(method.lower(), "update")

        def create_listener(collection, method, _event):
            async def _autocache(bot: Bot, data: event.func):
                """Manages cached Guild's collections"""
                try:
                    await eval(f"bot.cache[data.guild_id].{collection}.{method}(data{attributes.get(_event, '')})")
                except AttributeError as ex:
                    log.warning(
                        f"Attempted to use {attributes.get(_event, 'object')} for {collection}.{method} but it's not part of the cache or the object!",
                        exc_info=ex,
                    )

            return _autocache

        onDispatch(
            f=create_listener(collection, method, event.name.lower()),
            priority=200,
            event=event.name,
            optional=True,
        )
        log.debug(f"Registering auto cache {method} method for {collection} on {event}")
