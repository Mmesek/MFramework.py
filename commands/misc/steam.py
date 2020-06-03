import json


from MFramework.commands import register
from MFramework.utils.api import Steam as steam
from MFramework.utils.utils import Embed, tr


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


async def steamParse(self, request, language, *game):
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
            page = await steam.appDetails(appid, language)
            yield page[str(appid)]["data"], appid


@register(help="Fetches playercount for specified game(s). Separate with `,`", alias="", category="")
async def playercount(self, *game, data, language, **kwargs):
    result = tr("commands.playercount.for", language)
    async for playercount, game in steamParse(self, "playercount", language, *game):
        try:
            playercount = playercount["response"]["player_count"]
            result += f"{game}: {playercount}\n"
        except KeyError:
            result += f"{game}: "+tr("commands.playercount.error", language)
    await self.message(data.channel_id, result[:2000])


def getBazarPrice(game):
    from bs4 import BeautifulSoup
    import requests
    bazar = 'https://bazar.lowcygier.pl/?title='
    data = requests.get(bazar+game)
    soup= BeautifulSoup(data.text,'html.parser')
    lis = soup.find('div', id="w0", class_='list-view')
    sel = lis.find_all('div', class_='col-md-7 col-sm-4 col-xs-6 nopadding')
    prc = 0
    for each in sel:
        if (each.find('h4',class_='media-heading').a.text == game):
            prc = each.find('p',class_='prc').text.replace(' zł','zł')
            url = each.find('h4', class_='media-heading').a.attrs['href']
            break
    if prc != 0:
        return f"[{prc}](https://bazar.lowcygier.pl{url})"
    return 0

def getGGDealsLowPrice(game, language):
    from bs4 import BeautifulSoup
    import requests
    if language == 'en':
        language = 'eu'
    gg = f"https://gg.deals/{language}/region/switch/?return=%2Fgame%2F"#f'https://gg.deals/{language}/game/'
    name2= game.replace(' ','-').replace('!','-').replace('?','-').replace("'",'-').replace('.','').replace(':','').replace(',',' ')
    data = requests.get(gg+name2)
    soup= BeautifulSoup(data.text,'html.parser')
    lis = soup.find('div', class_='price-wrap')
    try:
        prc = lis.find('span', class_='numeric').text.replace('~', '').replace(' zł','zł')
        url2 = soup.find('div', class_='list-items').find('a', {'target': '_blank'})['href']
    except:
        prc = 0
    try:
        li = lis.find('div',class_='lowest-recorded price-widget')
        prc2 = li.find('span', class_='numeric').text.replace('~', '').replace(' zł','zł')
    except:
        prc2 = 0
    if prc != 'Free' and prc != 0:
        p1 = f"[{prc}](https://gg.deals{url2})"
    else:
        p1 = 0
    if prc2 != 0:
        p2 = prc2
    else:
        p2 = 0
    return (p1, p2)

@register(help="Shows game details", alias="", category="")
async def game(self, *game, data, language, **kwargs):
    async for game, appid in steamParse(self, "details", language, *game):
        embed = Embed()
        embed.setDescription(game["short_description"]).setTitle(game["name"])
        embed.setUrl(f"https://store.steampowered.com/app/{appid}/").setFooter(
            "", text=tr("commands.game.release", language) + game["release_date"]["date"]
        )
        embed.setImage(game["header_image"])
        prc = game.get("price_overview", {}).get("final_formatted")
        is_free = game.get("is_free", {})
        if prc is not None or is_free:
            if is_free:
                prc = tr("commands.game.f2p", language)
            embed.addField(tr("commands.game.price", language), prc, True)
        if language == "pl":
            bazar = getBazarPrice(game["name"])
            if bazar != 0:
                embed.addField(tr("commands.game.BazarPrice", language), bazar, True)
        ggdeals = getGGDealsLowPrice(game["name"], language)
        if ggdeals[0] != 0:
            embed.addField(tr("commands.game.CurrentLowPrice", language), ggdeals[0], True)
        if ggdeals[1] != 0:
            embed.addField(tr("commands.game.HistLowPrice", language), ggdeals[1], True)
        r = game.get("recommendations", {}).get("total")
        if r is not None:
            embed.addField(tr("commands.game.recommendations", language), r, True)
        cp = await steam.CurrentPlayers(appid)
        cp = cp.get("response", {}).get("player_count")
        if cp is not None:
            embed.addField(tr("commands.game.players", language), cp, True)
        ach = game.get("achievements", {}).get("total")
        if ach is not None and ach != 0:
            embed.addField(tr("commands.game.achievements", language), ach, True)
        required_age = game.get("required_age")
        if required_age != 0:
            embed.addField(tr("commands.game.age", language), required_age, True)
        dlc = len(game.get("dlc", []))
        if dlc != 0:
            embed.addField(tr("commands.game.dlc", language), dlc, True)
        f = len(embed.embed["fields"])
        if f != 0 and f % 3 != 0:
            embed.addField("\u200b", "\u200b", True)
        devs = game.get("developers")
        if devs is not None:
            embed.addField(tr("commands.game.developers", language, count=len(devs)), ", ".join(devs), True)
        publishers = game.get("publishers")
        if publishers != devs:
            embed.addField(tr("commands.game.publishers", language, count=len(publishers)), ", ".join(publishers), True)
        await self.embed(data.channel_id, "", embed.embed)


@register(group='Global', help='Lists closest matches in Steam Index', alias='', category='')
async def steamlist(self, *game, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    from difflib import get_close_matches
    game = " ".join(game)
    if not hasattr(self, "index"):
        await loadSteamIndex(self)
    game = get_close_matches(game, self.index.keys(), 10)
    t= ''
    for g in game:
        t += '\n- ' + g
    embed = Embed().setDescription(t[:2024])
    await self.embed(data.channel_id, '', embed.embed)