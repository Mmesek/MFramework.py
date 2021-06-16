from MFramework import onDispatch, Bot, Message, Message_Delete

import re
EMOJI = re.compile(r":\w+:")
@onDispatch(priority=1)
async def message_create(self: Bot, data: Message):
    if not data.is_empty:
        from MFramework.commands.context import check_context
        from MFramework.commands.commands import check_command
        if any(i.id == self.user_id for i in data.mentions):
            await self.trigger_typing_indicator(data.channel_id)
        if await check_context(self, data):
            return True
        elif await check_command(self, data):
            return True
        from .actions import responder
        for emoji in EMOJI.findall(data.content):
            await responder(self, data, emoji)
        import MFramework.commands.parser as parser
        await parser.parse(self, data)

@onDispatch
async def direct_message_create(self: Bot, data: Message):
    await self.cache[self.primary_guild].logging["direct_message"](data)
    if data.channel_id not in self.cache[0]:
        from MFramework.database.cache import Cache
        self.cache[data.guild_id][data.channel_id] = Cache()
    self.cache[data.guild_id][data.channel_id].store(data)

@onDispatch
async def message_update(self: Bot, data: Message):
    if not data.author or data.webhook_id or not data.guild_id or not data.content:
        return
    from .actions import roll_dice
    await roll_dice(self, data, True)

    self.cache[data.guild_id].messages.update(data)

@onDispatch
async def message_delete(self: Bot, data: Message_Delete):
    self.cache[data.guild_id].messages.delete(data.id)
