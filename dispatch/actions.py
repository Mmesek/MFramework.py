from MFramework import *
from MFramework.database.alchemy import types
async def _handle_reaction(ctx: Bot, data: Message, reaction: str, name: str, _type: types.Item=None, 
                    wait: bool=True, delete_own: bool=True, store_in_cache: bool=False, first_only=False, all_reactions: bool=True, 
                    logger: str=None, statistic: types.Statistic=None):
    import random, asyncio
    await asyncio.sleep(random.SystemRandom().randint(0, 10))
    await data.react(reaction)
    t = random.SystemRandom().randint(15, 60)
    if store_in_cache:
        ctx.cache[data.guild_id].special_message.store(data, expire=t, type=name, first_only=first_only)
    if not wait and not statistic:
        return
    await asyncio.sleep(t)
    if delete_own:
        await data.delete_reaction(reaction)
    
    if store_in_cache:
        ctx.cache[data.guild_id].special_message.delete(data.id) #Not needed thanks to expire flag
    
    s = ctx.db.sql.Session()
    
    from MFramework.database.alchemy import models
    if statistic:
        models.Statistic.increment(s, data.guild_id, statistic)
    if all_reactions:
        users = await data.get_reactions(reaction)
    
        from MFramework.database.alchemy import items, helpers
        item = helpers.fetch_or_add(s, items.Item, name, _type)
        i = items.Inventory(item)
        for user in users:
            helpers.add_item(s, data.guild_id, user.id, item=i)
            models.Log.claim(data.guild_id, user.id, _type)
        await ctx.cache[data.guild_id].logging[logger](data, users)
    s.commit()

from MFramework.commands.interactions import Event, Chance
@Event(month=4)
@Chance(2.5)
async def egg_hunt(ctx: Bot, data: Message):
    await _handle_reaction(ctx, data, "🥚", "Easter Egg", types.Item.EasterEgg, logger="egg_hunt", statistic=types.Statistic.Spawned_Eggs)

@Event(month=12)
@Chance(3)
async def present_hunt(ctx: Bot, data: Message):
    await _handle_reaction(ctx, data, "🎁", "Present", wait=False, delete_own=False, store_in_cache=True, first_only=True, all_reactions=False, logger="present_hunt", statistic=types.Statistic.Spawned_Presents)

@Event(month=10)
@Chance(1)
async def halloween_hunt(ctx: Bot, data: Message):
    await _handle_reaction(ctx, data, "🎃", "Pumpkin", wait=False, delete_own=False, store_in_cache=True, first_only=True, all_reactions=False, logger="halloween_hunt", statistic=types.Statistic.Spawned_Pumpkins)

async def responder(ctx: Bot, msg: Message, emoji: str):
    emoji = ctx.cache[msg.guild_id].custom_emojis.get(emoji.lower().strip(':'))
    if type(emoji) is str:
        await msg.reply(emoji)
    elif type(emoji) is tuple:
        await msg.reply(file=emoji[1], filename=emoji[0])

async def parse_reply(self: Bot, data: Message):
    from MFramework.commands._utils import detect_group, Groups
    _g = detect_group(self, data.author.id, data.guild_id, data.member.roles)
    if data.channel_id == 686371597895991327 and _g in [Groups.SYSTEM, Groups.ADMIN, Groups.MODERATOR]:
        return await dm_reply(self, data)
    if data.channel_id != 802092364008783893:
        return
    if _g not in [Groups.SYSTEM, Groups.MODERATOR, Groups.ADMIN]:
        return
    if data.referenced_message == None or data.referenced_message.id == 0:
        return
    await self.cache[data.guild_id].logging["message_replay_qna"](data)

async def dm_reply(ctx: Bot, msg: Message):
    from MFramework.utils.utils import parseMention, check_attachments
    user = parseMention(msg.referenced_message.embeds[0].footer.text)
    dm = await ctx.create_dm(user)
    await ctx.create_message(dm.id, msg.content, embed=check_attachments(msg))
    await msg.react(ctx.emoji['success'])

async def deduplicate_messages(self: Bot, data: Message) -> bool:
    c = self.cache[data.guild_id].messages
    _last_message = c[-1] #c.last_message(data.channel_id)
    if _last_message.content == data.content and _last_message.author.id == data.author.id:
        await self.delete_message(data.channel_id, data.id)
        return True
    self.cache[data.guild_id].messages.store(data)
    return False

async def roll_dice(self: Bot, data: Message, update: bool = False):
    if data.channel_id not in self.cache[data.guild_id].rpg_channels:
        return
    if update:
        m = await self.get_channel_message(data.channel_id, data.id)
        if m.reactions:
            return
    import re
    ILLEGAL_ACTIONS = re.compile(r"(?i)zabij|wyryw|mord")
    DICE_REACTIONS = ['0️⃣','1️⃣','2️⃣','3️⃣','4️⃣','5️⃣','6️⃣']
    DICE_EMOJIS = {0:'dice_0:761760091648294942',
        1:'dice_1:761760091971780628',2:'dice_2:761760091837825075',3:'dice_3:761760092206792750',
        4:'dice_4:761760092767911967',5:'dice_5:761760093435068446',6:'dice_6:761760093817143345'}
    reg = re.findall(r"(?:(?=\*)(?<!\*).+?(?!\*\*)(?=\*))", data.content)
    if reg and set(reg) != {'*'}:
        if '*' in reg:
            reg = set(reg)
            reg.remove('*')
            reg = list(reg)
        dices = self.cache[data.guild_id].rpg_dices or DICE_REACTIONS
        from random import SystemRandom as random
        v = random().randint(1, 6) if not ILLEGAL_ACTIONS.findall(reg[0]) else 0
        await self.create_reaction(data.channel_id, data.id, dices[v])

async def handle_level(self: Bot, data: Message):
    if data.channel_id not in self.cache[data.guild_id].disabled_channels and not any(r in data.member.roles for r in self.cache[data.guild_id].disabled_roles):
        from MFramework.utils import levels
        await levels.exp(self, data)