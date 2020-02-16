from bot.discord.commands import register
import asyncio

from bot.utils.utils import parseMention as parseMention
@register(group="Admin", help="Edits bot's message")
async def edit_message(self, messageID, *newMessage, channel, data, **kwargs):
    print('Hello there.')
    print(channel, messageID, *newMessage)
    #part = data["content"].replace("<", "").replace("#", "").replace(">", "").split(" ", 3)
    #await self.endpoints.edit(part[1], part[2], part[3], 0)
    await self.endpoints.edit(parseMention(channel[0]), messageID, ' '.join(newMessage))


@register(group="Admin", help="Allows only specific roles access to emoji's")
async def edit_emoji(self, emojis, roles, *args, data, **kwargs):
    for emoji in emojis:
        if "<:" in emoji:
            part2 = emoji.replace("\\<:", "").replace(">", "").replace(":", " ").split(" ", 2)
            print(
                "Modified emoji: ", await self.endpoints.modify_emoji(data["guild_id"], part2[1], part2[0], roles)
            )
            await asyncio.sleep(2.5)


@register(group="Admin", help="Sends animated emoji")
async def aemoji(self, emoji_name, *args, data, **kwargs):
    emojis = await self.endpoints.get_emoji(data["guild_id"])
    message = ""
    for emoji in emojis:
        if emoji["name"] == emoji_name:
            if emoji["animated"]:
                message += f"<a:{emoji['name']}:{emoji['id']}> "
            else:
                message += f"<:{emoji['name']}:{emoji['id']}> "
    try:
        await self.endpoints.delete(data["channel_id"], data["id"])
        await self.endpoints.message(data["channel_id"], message)
    except Exception as ex:
        print(ex)


@register(group="Admin", help="Lists all available emoji's in guild")
async def list_emoji(self, *args, data, **kwargs):
    emojis = await self.endpoints.get_emoji(data["guild_id"])
    elist = ""
    for emoji in emojis:
        if emoji["animated"]:
            elist += f"\n> <a:{emoji['name']}:{emoji['id']}> - \\<a:{emoji['name']}:{emoji['id']}>"
        elif "all" in data["content"]:
            elist += f"\n> <:{emoji['name']}:{emoji['id']}> - \\<:{emoji['name']}:{emoji['id']}>"
    await self.endpoints.message(data["channel_id"], elist[:2000])


@register(group="Admin", help="Delete's message")
async def delete(self, channel, *message, data, **kwargs):
    print(channel, *message)
    await self.endpoints.delete(channel, *message)


@register(group="Admin", help="Retrives messages from DM")
async def getmessagesfromdm(self, user, *args, data, **kwargs):
    dm = await self.endpoints.make_dm(user)
    messages = await self.endpoints.get_messages(dm["id"], dm["last_message_id"])
    message = ""
    for each in messages:
        print(each["author"], each["content"])
        message += f"[{each['id']}] - {each['author']['username']}: {each['content']}"
    await self.endpoints.embed(data["channel_id"], "", {"title": dm["id"], "description": message})


@register(group="Admin", help="Create reaction role")
async def create_rr(self, channel_slash_message, role, reaction, group='', *args, data, **kwargs):
    if len(channel_slash_message.split("/")) > 1:
        channel = channel_slash_message.split("/")
        message = channel[1]
        channel = channel[0]
    else:
        channel = data["channel_id"]
        message = channel_slash_message
    reaction= reaction.replace('<:','').replace('>','')    
    if group == "":
        g = "None"
    else:
        g = group
    if g not in self.cache.cache[data["guild_id"]]["reactionRoles"]:
        self.cache.cache[data["guild_id"]]["reactionRoles"][g] = {message: {reaction: role}}
    else:
        if message not in self.cache.cache[data["guild_id"]]["reactionRoles"][g]:
            self.cache.cache[data["guild_id"]]["reactionRoles"][g][message] = {reaction: role}
        else:
            self.cache.cache[data["guild_id"]]["reactionRoles"][g][message][reaction] = role
    await self.db.insert(
        "ReactionRoles",
        "GuildID, ChannelID, MessageID, RoleID, Reaction, RoleGroup",
        [data["guild_id"], channel, message, role, reaction, group],
    )
    await self.endpoints.react(channel, message, reaction)


@register(group="Admin", help="Remove reaction role")
async def remove_rr(self, channel, message, reaction, *args, data, **kwargs):
    params = data["content"].split(" ")
    if len(params[0].split("/")) > 1:
        channel = params[0].split("/")
        message = channel[1]
        channel = channel[0]
    else:
        channel = data["channel_id"]
        message = params[0]
    reaction = params[1]
    await self.db.delete(
        "ReactionRoles",
        "GuildID=? AND ChannelID=? AND MessageID=? AND Reaction=?",
        [data["guild_id"], channel, message, reaction],
    )
    await self.endpoints.delete_own_reaction(channel, message, reaction)


@register(group="Admin", help="Update reaction role")
async def update_rr(self, *args, data, **kwargs):
    await self.endpoints.message(
        data["channel_id"],
        "Look, remove it and then create again or make me sql query\
 for update cause, honestly: what exactly do you want to update? Add a group? Change Role? Reaction? Bro, come\
 on, be serious. !remove_rr and then !add_rr, you can do it",
    )


@register(group="Admin", help="Creates custom command/reaction", category="")
async def add_cc(self, name, trigger, response, group, *args, data, **kwargs):
    """$execute$command\n$$"""
    params = data["content"].split(";")
    name = params[0]
    trigger = params[1]
    response = params[2]
    req = params[3]
    await self.db.insert(
        "Regex",
        "GuildID, UserID, Name, Trigger, Response, ReqRole",
        [data["guild_id"], data["author"]["id"], name, trigger, response, req],
    )
    await self.cache.recompileTriggers(data)

@register(group='Admin', help='Removes custom command/reaction', category='')
async def remove_cc(self, name, trigger, *args, data, **kwargs):
    params = data["content"].split(';')
    name = params[0]
    trigger = params[1]
    await self.db.delete('Regex','GuildID=? AND Name=? AND Trigger=?',[data['guild_id'],name, trigger])
    await self.cache.recompileTriggers(data)