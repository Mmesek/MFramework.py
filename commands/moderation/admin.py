from MFramework.commands import register

@register(group="Admin", help="Edits bot's message")
async def edit_message(self, messageID, *newMessage, data, channel, **kwargs):
    await self.edit_message(channel[0], messageID, ' '.join(newMessage))


@register(group="Admin", help="Allows only specific roles access to emoji's")
async def edit_emoji(self, emojis, roles, *args, data, **kwargs):
    for emoji in emojis:
        if "<:" in emoji:
            part2 = emoji.replace("\\<:", "").replace(">", "").replace(":", " ").split(" ", 2)
            await self.modify_guild_emoji(data.guild_id, part2[1], part2[0], roles)


@register(group="Admin", help="Sends animated emoji", notImpl=True)
async def aemoji(self, emoji_name, *args, data, **kwargs):
    emojis = await self.endpoints.list_guild_emoji(data.guild_id)
    message = ""
    for emoji in emojis:
        if emoji.name == emoji_name:
            if emoji.animated:
                message += f"<a:{emoji.name}:{emoji.id}> "
            else:
                message += f"<:{emoji.name}:{emoji.id}> "
    await self.delete_message(data.channel_id, data.id)
    await self.message(data.channel_id, message)


@register(group="Admin", help="Lists all available emoji's in guild")
async def list_emoji(self, *args, data, all=False, regular=False, **kwargs):
    emojis = await self.list_guild_emojis(data.guild_id)
    _animated = ""
    _regular = ""
    for emoji in emojis:
        if emoji.animated and not regular:
            _animated += f"\n<a:{emoji.name}:{emoji.id}> - a:{emoji.name}:{emoji.id}"
        elif not emoji.animated and (all or regular):
            _regular += f"\n<:{emoji.name}:{emoji.id}> - {emoji.name}:{emoji.id}"
    e = Embed().setTitle("Emoji List")
    if not regular and _animated != "":
        e.addFields("Animated", _animated, False)
    if (all or regular) and _regular != "":
        if regular and (len(_regular) / 1024 <= 2):
            inline = True
        else:
            inline = False
        e.addFields("Regular", _regular, inline)
    await self.embed(data.channel_id, '', e.embed)


@register(group="Admin", help="Delete's message", notImpl=True)
async def delete(self, channel, *message, data, **kwargs):
    await self.delete_message(channel, *message)

from MFramework.utils.utils import Embed
@register(group="Admin", help="Retrives messages from DM")
async def getmessages(self, user, *args, data, **kwargs):
    dm = await self.create_dm(user)
    messages = await self.get_messages(dm.id)
    message = ""
    for each in messages:
        message += f"\n`[{each.timestamp[:19]}]` - `{each.author.username}`: {each.content}"
    e = Embed().setFooter("", f"DM ID: {dm.id}").setDescription(message[:2000])
    await self.embed(data.channel_id, "", e.embed)

@register(group='Admin', help='Shows prune count', alias='', category='', notImpl=True)
async def prunecount(self, days=7, *args, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    count = await self.get_guild_prune_count(data.guild_id, days)
    await self.message(data.channel_id, count)