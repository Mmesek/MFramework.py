from bot.discord.commands import register
import asyncio


@register(group="Admin", help="[user] [message] - Sends user DM as a bot")
async def send_dm(self, data):
    con = data["content"].split(" ", 1)
    if "mentions" in data != []:
        uid = data["mentions"][0]["id"]
    else:
        uid = con[1].replace("<", "").replace("@", "").replace(">", "").replace("&", "")
    if "\\" in con[2]:
        con[2] = con[2].replace("\\", "")
    if "a:" in con[2]:
        con[2] = con[2].replace("a:", "<a:")
    dm = await self.endpoints.make_dm(uid)
    await self.endpoints.message(dm["id"], con[1])


@register(group="Admin", help="(channel) [message] - Sends message to a channel as a bot")
async def send_message(self, data):
    part = data["content"].split(" ", 1)
    channel = part[0].replace("<", "").replace("#", "").replace(">", "")
    print(channel, part)
    await self.endpoints.message(channel, part[1])


@register(group="Admin", help="(channel) [messageID] [reaction] - Reacts to a message with emoji as a bot")
async def react(self, data):
    print("Reeeeact")
    part = data["content"].split(" ", 1)
    chap = part[1].split(" ")
    for each in chap:
        await self.endpoints.react(data["channel_id"], part[0], each.replace("<:", "").replace(">", ""))
        await asyncio.sleep(0.3)


@register(group="Admin", help="(channel) [messageID] [newMessage] - Edits bot's message")
async def edit_message(self, data):
    part = data["content"].replace("<", "").replace("#", "").replace(">", "").split(" ", 3)
    await self.endpoints.edit(part[1], part[2], part[3], 0)


@register(group="Admin", help="[emoji ..] [role] - Allows only specific role access to emoji's")
async def edit_emoji(self, data):
    part = data["content"].split(" ")
    for split in part:
        if "<:" in split:
            part2 = split.replace("\\<:", "").replace(">", "").replace(":", " ").split(" ", 2)
            print(
                "Modified emoji: ", await self.endpoints.modify_emoji(data["guild_id"], part2[1], part2[0], [part[1]])
            )
            await asyncio.sleep(2.5)


@register(group="Admin", help="[name of animated emoji] - Sends animated emoji")
async def aemoji(self, data):
    emojis = await self.endpoints.get_emoji(data["guild_id"])
    e = data["content"].split(" ")[0:]
    message = ""
    for one in e:
        for emoji in emojis:
            if emoji["name"] == one:
                if emoji["animated"]:
                    message += f"<a:{emoji['name']}:{emoji['id']}> "
                else:
                    message += f"<:{emoji['name']}:{emoji['id']}> "
    try:
        await self.endpoints.delete(data["channel_id"], data["id"])
        await self.endpoints.message(data["channel_id"], message)
    except Exception as ex:
        print(ex)


@register(group="Admin", help="- Lists all available emoji's in guild")
async def list_emoji(self, data):
    emojis = await self.endpoints.get_emoji(data["guild_id"])
    elist = ""
    for emoji in emojis:
        if emoji["animated"]:
            elist += f"\n> <a:{emoji['name']}:{emoji['id']}> - \\<a:{emoji['name']}:{emoji['id']}>"
        elif "all" in data["content"]:
            elist += f"\n> <:{emoji['name']}:{emoji['id']}> - \\<:{emoji['name']}:{emoji['id']}>"
    await self.endpoints.message(data["channel_id"], elist[:2000])


@register(group="Admin", help="(channel) [message] - Delete's message")
async def delete(self, data):
    chop = data["content"].split(" ", 1)
    channel = chop[0]
    message = chop[1]
    print(channel, message)
    await self.endpoints.delete(channel, message)


@register(group="Admin", help="Retrives messages from DM")
async def getmessagesfromdm(self, data):
    s = data["content"].split(" ", 1)
    dm = await self.endpoints.make_dm(s[0])
    print(dm)
    messages = await self.endpoints.get_messages(dm["id"], dm["last_message_id"])
    message = ""
    for each in messages:
        print(each["author"], each["content"])
        message += f"[{each['id']}] - {each['author']['username']}: {each['content']}"
    await self.endpoints.embed(data["channel_id"], "", {"title": dm["id"], "description": message})


@register(group="Admin", help="[channel/]message role reaction [group] - Create reaction role")
async def create_rr(self, data):
    params = data["content"].split(" ")
    if len(params[0].split("/")) > 1:
        channel = params[0].split("/")
        message = channel[1]
        channel = channel[0]
    else:
        channel = data["channel_id"]
        message = params[0]
    role = params[1]
    reaction = params[2]
    if len(params) > 3:
        group = params[3]
    else:
        group = ""
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


@register(group="Admin", help="[channel/]message reaction - Remove reaction role")
async def remove_rr(self, data):
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


@register(group="Admin", help=" - Update reaction role")
async def update_rr(self, data):
    await self.endpoints.message(
        data["channel_id"],
        "Look, remove it and then create again or make me sql query\
 for update cause, honestly: what exactly do you want to update? Add a group? Change Role? Reaction? Bro, come\
 on, be serious. !remove_rr and then !add_rr, you can do it",
    )
