from MFramework import onDispatch, Bot, Message, Message_Delete

import re
EMOJI = re.compile(r":\w+:")
@onDispatch
async def message_create(self: Bot, data: Message):
    if data.author is None and data.author.bot or data.webhook_id:
        return
    if data.guild_id and data.content != "":
        from .actions import egg_hunt, present_hunt, parse_reply, responder
        for emoji in EMOJI.findall(data.content):
            await responder(self, data, emoji)
        if data.channel_id in self.cache[data.guild_id].rpg_channels:
            from commands.rpg import dice
            await dice.roll(self, data)
        await guild_message(self, data)
        await parse_reply(self, data)
        await egg_hunt(self, data)
        await present_hunt(self, data)
    elif data.guild_id == 0:
        await dm_message(self, data)

async def guild_message(self: Bot, data: Message):
    c = self.cache[data.guild_id].messages
    if (( #TODO
        data.channel_id in c 
        and (len(c[data.channel_id]) >= 1)) 
        and (c[data.channel_id][list(c[data.channel_id].keys())[-1]].content == data.content) 
        and (c[data.channel_id][list(c[data.channel_id].keys())[-1]].author.id == data.author.id)
    ):
        return await self.delete_message(data.channel_id, data.id)
    self.cache[data.guild_id].messages.store(data)
    if (
        data.channel_id not in self.cache[data.guild_id].disabled_channels 
        and not any(r in data.member.roles for r in self.cache[data.guild_id].disabled_roles)
    ):
        from MFramework.utils import levels
        await levels.exp(self, data)

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
    elif data.channel_id in self.cache[data.guild_id].rpg_channels:
        from commands.rpg import dice
        await dice.roll(self, data, True)

    await self.cache[data.guild_id].logging["message_update"](data)
    self.cache[data.guild_id].store(data)

@onDispatch
async def message_delete(self: Bot, data: Message_Delete):
    if data.guild_id:
        await self.cache[data.guild_id].logging["message_delete"](data)
        self.cache[data.guild_id].delete(data.id)
