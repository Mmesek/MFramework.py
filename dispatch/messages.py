from MFramework import onDispatch, Bot, Message, Message_Delete

import re
EMOJI = re.compile(r":\w+:")
@onDispatch
async def message_create(self: Bot, data: Message):
    if data.author is None and data.author.bot or data.webhook_id:
        return
    if data.guild_id and data.content != "":
        from .actions import deduplicate_messages
        if await deduplicate_messages(self, data):
            return
        from .actions import egg_hunt, present_hunt, parse_reply, responder
        from .actions import roll_dice, handle_level
        for emoji in EMOJI.findall(data.content):
            await responder(self, data, emoji)
        await roll_dice(self, data)
        await parse_reply(self, data)
        await egg_hunt(self, data)
        await present_hunt(self, data)
        await handle_level(self, data)
    elif data.guild_id == 0:
        await dm_message(self, data)

async def dm_message(self: Bot, data: Message):
    await self.cache[self.primary_guild].logging["direct_message"](data)
    if data.channel_id not in self.cache[0]:
        from MFramework.database.cache import Cache
        self.cache[data.guild_id][data.channel_id] = Cache()
    self.cache[data.guild_id][data.channel_id].store(data)

@onDispatch
async def message_update(self: Bot, data: Message):
    if not data.author or data.webhook_idor or not data.guild_id or not data.content:
        return
    from .actions import roll_dice
    roll_dice(self, data, True)

    await self.cache[data.guild_id].logging["message_update"](data)
    self.cache[data.guild_id].messages.update(data)

@onDispatch
async def message_delete(self: Bot, data: Message_Delete):
    if data.guild_id:
        await self.cache[data.guild_id].logging["message_delete"](data)
        self.cache[data.guild_id].messages.delete(data.id)
