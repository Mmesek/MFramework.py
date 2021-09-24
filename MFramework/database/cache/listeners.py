from MFramework import onDispatch, Bot, Guild, log

@onDispatch
async def guild_create(bot: Bot, guild: Guild):
    if guild.id not in bot.cache:
        import time
        start = time.time()
        bot.cache[guild.id] = bot._Cache(bot, guild)
        from MFramework.utils.scheduler import add_guild_tasks
        add_guild_tasks(bot, guild.id)
        log.info("Guild %s initialized in %s", guild.id, time.time() - start)
    if len(bot.cache[guild.id].members) < 50:
        await bot.request_guild_members(guild.id)

methods = {
    "add": "update",
    "delete": "delete",
    "delete_bulk": "delete",
    "remove": "delete",
    "create": "store",
    "chunk": "update"
}

collections = {
    "guild_member": "members",
    "message": "messages",
    "channel": "channels",
    "guild_role": "roles"
}

attributes = {
    "guild_members_chunk": ".members",
    "guild_member_remove": ".user.id",
    "message_delete": ".id"
}

def create_cache_listeners(Cache: object):
    from mdiscord.types import Gateway_Events
    from mdiscord.opcodes import Dispatch
    for event in Gateway_Events:
        if not hasattr(event.func, 'guild_id'):
            continue
        if any(i.__name__ == "_autocache" for i in Dispatch.get(event.name.upper(), {}).get(100, [])):
            continue
        collection, method = event.name.rsplit("_", 1)
        collection = collections.get(collection[:-1].lower() if collection.endswith("s") else collection.lower(), collection.lower()).lower()
        from MFramework.database.cache_internal import models
        if not hasattr(Cache, collection):
            continue
        elif not isinstance(getattr(Cache, collection), models.Cache):
            continue
        method = methods.get(method.lower(), "update")
        def create_listener(collection, method, _event):
            async def _autocache(bot: Bot, data: event.func):
                """Manages cached Guild's collections"""
                try:
                    exec(f"bot.cache[data.guild_id].{collection}.{method}(data{attributes.get(_event, '')})")
                except Exception as ex:
                    pass
            return _autocache
        onDispatch(f=create_listener(collection, method, event.name.lower()), event=event.name, optional=True)
        log.debug(f"Registering auto cache {method} method for {collection} on {event}")
