from MFramework.commands import register

@register(group="Admin", help="Edits bot's message", notImpl=True)
async def edit_message(self, messageID, *newMessage, channel, data, **kwargs):
    await self.edit_message(channel, messageID, ' '.join(newMessage))


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


@register(group="Admin", help="Lists all available emoji's in guild", notImpl=True)
async def list_emoji(self, *args, data, **kwargs):
    emojis = await self.list_guild_emoji(data.guild_id)
    elist = ""
    for emoji in emojis:
        if emoji.animated:
            elist += f"\n> <a:{emoji.name}:{emoji.id}> - \\<a:{emoji.name}:{emoji.id}>"
        elif "all" in data.content:
            elist += f"\n> <:{emoji.name}:{emoji.id}> - \\<:{emoji.name}:{emoji.id}>"
    await self.message(data.channel_id, elist[:2000])


@register(group="Admin", help="Delete's message", notImpl=True)
async def delete(self, channel, *message, data, **kwargs):
    await self.delete_message(channel, *message)


@register(group="Admin", help="Retrives messages from DM", notImpl=True)
async def getmessagesfromdm(self, user, *args, data, **kwargs):
    dm = await self.create_dm(user)
    messages = await self.get_channel_messages(dm.id, dm.last_message_id)
    message = ""
    for each in messages:
        print(each.author, each.content)
        message += f"[{each.id}] - {each.author.username}: {each.content}"
    await self.embed(data.channel_id, "", {"title": dm.id, "description": message})
