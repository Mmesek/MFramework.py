from bot.utils.utils import quote, Embed
from bot.discord.mbot import onDispatch
from bot.discord.commands import execute, parse


@onDispatch()
async def ready(self, data):
    self.session_id = data["session_id"]
    self.user_id = data["user"]["id"]
    self.username = data["user"]["username"]
    print("Conntected as:", data["user"]["username"])


@onDispatch()
async def resumed(self, data):
    pass


@onDispatch()
async def message_create(self, data):
    try:
        if "webhook_id" not in data and "bot" not in data["author"] and "guild_id" in data:
            if (
                "!" in data["content"] or self.user_id in data["content"] or self.username in data["content"]
            ) and await execute(self, data) != 0:
                return
            elif "discordapp.com/channels/" in data["content"]:
                pass
                return await quote(self, data)
            elif await parse(self, data) == None:
                return
            self.cache.message(data)
        #    database.AddExp(data['guild_id'],data['author']['id'],int(datetime.datetime.fromisoformat(data['timestamp']).timestamp()))
        elif "bot" not in data["author"] and "guild_id" not in data:
            embed = (
                Embed()
                .setDescription(data["content"])
                .setAuthor(
                    f"{data['author']['username']}#{data['author']['discriminator']}",
                    "",
                    f"https://cdn.discordapp.com/avatars/{data['author']['id']}/{data['author']['avatar']}.png",
                )
            )
            embed.setTimestamp(data["timestamp"].split("+", 1)[0]).setFooter(
                "", f"{data['author']['id']} - {data['author']['username']}#{data['author']['discriminator']}"
            )
            try:
                embed.setImage(data["attachments"][0]["url"])
                filename = data["attachments"][0]["filename"]
            except:
                filename = ""
            webhook = await self.db.selectOne(
                "Webhooks", "Webhook", "WHERE GuildID=? AND Source=?", ["463433273620824104", "DM"]
            )
            await self.endpoints.webhook(
                [embed.embed],
                f"<@{data['author']['id']}> {filename}",
                webhook[0],
                f"{data['author']['username']}#{data['author']['discriminator']}",
                f"https://cdn.discordapp.com/avatars/{data['author']['id']}/{data['author']['avatar']}.png",
            )
            return await self.endpoints.react(data["channel_id"], data["id"], "tipping:517814432806600704")
        return
    except Exception as ex:
        print("Message Create Error: ", ex)
        print(data)
    return


@onDispatch()
async def presence_update(self, data):
    pass


@onDispatch()
async def message_update(self, data):
    if "guild_id" not in data or "webhook_id" in data or "content" not in data:
        return
    c = self.cache.cachedMessage(data)
    embed = Embed().setTitle(f"Message edited in <#{data['channel_id']}>\nBefore:")
    if c is not None:
        embed.setDescription(c["content"]).setTimestamp(c["timestamp"]).setFooter("", f"ID: {c['author']['id']}")
        embed.setAuthor(
            f"{c['author']['username']}#{c['author']['discriminator']}",
            "",
            f"https://cdn.discordapp.com/avatars/{c['author']['id']}/{c['author']['avatar']}.png",
        )
        embed.addField("After:", data["content"][:1023])
        if len(data["content"]) > 1023:
            embed.addField("\u200b", data["content"][1023:])
        try:
            embed.addField("Attachments:", c["attachments"][0]["filename"])
        except IndexError:
            pass
        webhook = self.cache.cache[data["guild_id"]]["logging"]["all"]  # ['message_update']
        if webhook == []:
            return
        await self.endpoints.webhook([embed.embed], "", webhook[0])
    self.cache.message(data)


@onDispatch()
async def voice_server_update(self, data):
    # Voice = voice.VoiceConnection(data['token'], data['endpoint'], data['guild_id'])
    # await Voice.connection_manager()
    pass


@onDispatch()
async def voice_state_update(self, data):
    # if data["channel_id"] != None:
    #    await self.cache.voice(data)
    # else:
    #    t = int(await self.cache.cachedVoice(data) / 60 / 10)
    #    print(t)
    #    database.AddExp(data['guild_id'],data['user_id'],'','vexp',t,"joinedVC")
    pass


@onDispatch()
async def channel_create(self, data):
    pass


@onDispatch()
async def channel_update(self, data):
    pass


@onDispatch()
async def channel_delete(self, data):
    pass


@onDispatch()
async def channel_pins_update(self, data):
    pass


@onDispatch()
async def guild_create(self, data):
    await self.cache.server_data(data)


@onDispatch()
async def guild_update(self, data):
    pass


@onDispatch()
async def guild_delete(self, data):
    if "unavailable" in data:
        print("Unavailable guild: ", data["id"])
    else:
        print(f"I guess we don't need {data['id']} in cache anymore...")
        self.cache.pop(data["id"])


@onDispatch()
async def guild_ban_add(self, data):
    pass


@onDispatch()
async def guild_ban_remove(self, data):
    pass


@onDispatch()
async def guild_emojis_update(self, data):
    pass


@onDispatch()
async def guild_integrations_update(self, data):
    pass


@onDispatch()
async def guild_member_add(self, data):
    await self.db.influxMember(data["guild_id"], data["user"]["id"], True, data["joined_at"])


@onDispatch()
async def guild_member_remove(self, data):
    await self.db.influxMember(data["guild_id"], data["user"]["id"], False)


@onDispatch()
async def guild_member_update(self, data):
    pass


@onDispatch()
async def guild_member_chunk(self, data):
    pass


@onDispatch()
async def guild_role_create(self, data):
    pass


@onDispatch()
async def guild_role_update(self, data):
    pass


@onDispatch()
async def guild_role_delete(self, data):
    pass


@onDispatch()
async def message_delete(self, data):
    if "guild_id" not in data or "webhook_id" in data:
        return
    c = self.cache.cachedMessage(data)
    embed = {"title": f"Message deleted in <#{data['channel_id']}>", "footer": {}, "author": {}, "fields": []}
    if c != None:
        embed["description"] = c["content"]
        embed["timestamp"] = c["timestamp"]
        embed["footer"]["text"] = f"ID: {c['author']['id']}"
        embed["author"][
            "icon_url"
        ] = f"https://cdn.discordapp.com/avatars/{c['author']['id']}/{c['author']['avatar']}.png"
        embed["author"]["name"] = f"{c['author']['username']}#{c['author']['discriminator']}"
        try:
            embed["fields"] += [{"name": "Attachments:", "value": c["attachments"][0]["filename"]}]
        except:
            pass
    webhook = self.cache.cache[data["guild_id"]]["logging"]["all"]  # ['message_delete']
    if webhook == "" or webhook == None or webhook == []:
        return
    return await self.endpoints.webhook([embed], "", webhook[0])


@onDispatch()
async def message_delete_bulk(self, data):
    pass


@onDispatch()
async def message_reaction_add(self, data):
    if "guild_id" not in data:
        return
    roles = self.cache.cache[data["guild_id"]]["reactionRoles"]
    r = None
    if roles == []:
        return
    for group in roles:
        for m in roles[group]:
            if data["message_id"] == str(m):
                r = roles[group][data["message_id"]][f"{data['emoji']['name']}:{data['emoji']['id']}"]
                if r == None:
                    return
                for role in data["member"]["roles"]:
                    if group == "None":
                        continue
                    for emoji in roles[group][data["message_id"]].values():
                        if emoji == role:
                            return await self.endpoints.delete_user_reaction(
                                data["channel_id"],
                                data["message_id"],
                                f"{data['emoji']['name']}:{data['emoji']['id']}",
                                data["user_id"],
                            )
                    if r == role:
                        return
    if r == None:
        return
    return await self.endpoints.role_add(data["guild_id"], data["user_id"], r, "Reaction Role")


@onDispatch()
async def message_reaction_remove(self, data):
    if "guild_id" not in data:
        return
    roles = self.cache.cache[data["guild_id"]]["reactionRoles"]
    role = None
    if roles == None:
        return
    for group in roles:
        for g in roles[group]:
            if data["message_id"] in roles[group]:
                role = roles[group][data["message_id"]][f"{data['emoji']['name']}:{data['emoji']['id']}"]
                if role == None:
                    return
                break
    return await self.endpoints.role_remove(data["guild_id"], data["user_id"], role, "Reaction Role")


@onDispatch()
async def message_reaction_remove_all(self, data):
    pass


@onDispatch()
async def presences_replace(self, data):
    pass


@onDispatch()
async def typing_start(self, data):
    pass


@onDispatch()
async def user_update(self, data):
    pass


@onDispatch()
async def webhooks_update(self, data):
    pass
