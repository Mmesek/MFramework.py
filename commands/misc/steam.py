import json


from MFramework.commands import register
from MFramework.utils.api import Steam as steam
from MFramework.utils.utils import Embed


@register(group="System", help="Updates Index of Steam Games")
async def refreshAppIndex(self, *args, data, **kwargs):
    steamapi = steam()
    apps = await steamapi.AppList()
    index = {}
    for each in apps["applist"]["apps"]:
        index[each["name"]] = each["appid"]
    with open("data/steamstoreindex.json", "w", newline="", encoding="utf-8") as file:
        json.dump(index, file)


async def loadSteamIndex(self):
    with open("data/steamstoreindex.json") as fjson:
        self.index = json.load(fjson)


async def steamParse(self, request, *game):
    from difflib import get_close_matches
    game = " ".join(game)
    games = game.split(",")
    if not hasattr(self, "index"):
        await loadSteamIndex(self)
    for game in games:
        game = get_close_matches(game, self.index.keys(), 1)[0]
        appid = self.index[game]
        if request == "playercount":
            playercount = await steam.CurrentPlayers(appid)
            yield playercount, game
        elif request == "details":
            page = await steam.appDetails(appid)
            yield page[str(appid)]["data"], appid


@register(help="Fetches playercount for specified game(s). Separate with `,`", alias="", category="")
async def playercount(self, *game, data, **kwargs):
    result = "Playercount for "
    async for playercount, game in steamParse(self, "playercount", *game):
        try:
            playercount = playercount["response"]["player_count"]
            result += f"{game}: {playercount}\n"
        except KeyError:
            result += f"{game}: Not found: Game might be not available, released or an error occured\n"
    await self.message(data.channel_id, result[:2000])




@register(help="Shows game details", alias="", category="")
async def gameDetails(self, *game, data, **kwargs):
    async for game, appid in steamParse(self, "details", *game):
        embed = Embed()
        embed.setDescription(game["short_description"]).setTitle(game["name"])
        embed.setUrl(f"https://store.steampowered.com/app/{appid}/").setFooter(
            "", text="Release Date: " + game["release_date"]["date"]
        )
        embed.setImage(game["header_image"])
        prc = game.get("price_overview", {}).get("final_formatted")
        is_free = game.get("is_free", {})
        if prc is not None or is_free:
            if is_free:
                prc = "Free2Play"
            embed.addField("Price", prc, True)
        r = game.get("recommendations", {}).get("total")
        if r is not None:
            embed.addField("Recommendations", r, True)
        cp = await steam.CurrentPlayers(appid)
        cp = cp.get("response", {}).get("player_count")
        if cp is not None:
            embed.addField("Currently players", cp, True)
        ach = game.get("achievements", {}).get("total")
        if ach is not None and ach != 0:
            embed.addField("Achievements", ach, True)
        required_age = game.get("required_age")
        if required_age != 0:
            embed.addField("Required Age", required_age, True)
        dlc = len(game.get("dlc", []))
        if dlc != 0:
            embed.addField("DLC Count", dlc, True)
        f = len(embed.embed["fields"])
        if f != 0 and f % 3 != 0:
            embed.addField("\u200b", "\u200b", True)
        devs = game.get("developers")
        if devs is not None:
            embed.addField("Developers", ", ".join(devs), True)
        publishers = game.get("publishers")
        if publishers != devs:
            embed.addField("Publishers", ", ".join(publishers), True)
        await self.embed(data.channel_id, "", embed.embed)
