from bot.discord.commands import register


@register(group="Vip", help="[campaign] - Mention your players")
async def session(self, data):
    if data["content"] != "":
        campaigns = data["content"].split(",")
    else:
        campaigns = [""]
    for campaign in campaigns:
        fetch = "PlayerID"
        query = "WHERE GuildID=? AND HostID=?"
        params = [data["guild_id"], data["author"]["id"]]
        if campaign == "all":
            fetch += ", Campaign"
        elif campaign != "":
            query += " AND Campaign=?"
            params += [campaign]
        players = await self.db.selectMultiple("RPSessionPlayers", fetch, query, params)
        if campaign == "all":
            final = f"Session for {players[1]}:\n"
        else:
            final = ""
        for one in players:
            if len(final) > 0 and final[-1] == ">":
                final += ", "
            final += f"<@{one[0]}>"
        await self.endpoints.message(data["channel_id"], final)


def getCampaign(data):
    c = data["content"].split(" ")
    campaign = data["author"]["username"]
    for one in c:
        if one.isdigit() is False:
            campaign = one
    return campaign


@register(group="Vip", alias="addplay", help="[@players], [campaign] - Adds player to a campaign")
async def addPlayer(self, data):
    campaign = getCampaign(data)
    for mention in data["mentions"]:
        await self.db.insert(
            "RPSessionPlayers",
            "GuildID, HostID, PlayerID, Campaign",
            [data["guild_id"], data["author"]["id"], mention["id"], campaign],
        )


@register(group="Vip", alias="delplay", help="[@players], [campaign] - Adds player to a campaign")
async def removePlayer(self, data):
    campaign = getCampaign(data)
    for mention in data["mentions"]:
        await self.db.delete(
            "RPSessionPlayers",
            "GuildID=? AND HostID=? AND PlayerID=? AND Campaign=?",
            [data["guild_id"], data["author"]["id"], mention["id"], campaign],
        )


async def rpban(self, data):
    await self.endpoints.message(
        data["channel_id"],
        "Here's the trick: Reaction roles managed through bot,\
    assign RP role and RP banned role to same group, add banned role and remove Roleplay one. The fact it's\
    written here means automatic role assigment of this thing is not done on bot side yet",
    )
