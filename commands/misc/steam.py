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
        try:
            game = get_close_matches(game, self.index.keys(), 1)[0]
        except IndexError:
            yield 0, game
        appid = self.index[game]
        if request == "playercount":
            playercount = await steam.CurrentPlayers(appid)
            yield playercount, game
        elif request == "details":
            page = await steam.appDetails(appid, language)
            yield page[str(appid)].get("data",{"short_description": "There was an error searching for data, perhaps Steam page doesn't exist anymore?", "name":game}), appid

def isEmpty(tuple):
    if len(tuple) == 0:
        return True
    return False

@register(help="Fetches playercount for specified game(s). Separate with `,`", alias="", category="")
async def playercount(self, *game, data, language, **kwargs):
    if isEmpty(game):
        return await self.message(data.channel_id, 'Game was not provided. Example usage: `playercount game title`')
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
    if isEmpty(game):
        return await self.message(data.channel_id, 'Game was not provided. Example usage: `game game title`')
    _game = game
    async for game, appid in steamParse(self, "details", language, *game):
        embed = Embed()
        embed.setDescription(game.get("short_description")).setTitle(game.get("name"))
        embed.setUrl(f"https://store.steampowered.com/app/{appid}/").setFooter(
            "", text=tr("commands.game.release", language) + game.get("release_date",{}).get("date","")
        )
        embed.setImage(game.get("header_image",""))
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
        ach = game.get("achievements", {}).get("total",0)
        if ach is not None and ach != 0:
            embed.addField(tr("commands.game.achievements", language), ach, True)
        required_age = game.get("required_age",0)
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
        from howlongtobeatpy import HowLongToBeat
        results = await HowLongToBeat().async_search(' '.join(_game))
        if results is not None and len(results) > 0:
            if len(embed.fields) != 0 and len(embed.fields) % 3 != 0:
                while len(embed.fields) % 3 != 0:
                    if len(embed.fields) == 25:
                        break
                    embed.addField("\u200b", "\u200b", True)
            g = max(results, key=lambda element: element.similarity)
            if g.gameplay_main != -1:
                embed.addField(g.gameplay_main_label, f"{g.gameplay_main} {g.gameplay_main_unit}", True)
            if g.gameplay_main_extra != -1:
                embed.addField(g.gameplay_main_extra_label, f"{g.gameplay_main_extra} {g.gameplay_main_extra_unit}", True)
            if g.gameplay_completionist != -1:
                embed.addField(g.gameplay_completionist_label, f"{g.gameplay_completionist} {g.gameplay_completionist_unit}", True)
        embed.addField(tr("commands.game.open", language), f"steam://store/{appid}/")
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


@register(group='Global', help='Steam Calculator. Similiar to Steamdb one (With few differences). Provide Country Code for currency', alias='', category='')
async def steamcalc(self, *user, data, currency='us', language, **kwargs):
    '''Extended description to use with detailed help command'''
    await self.trigger_typing_indicator(data.channel_id)
    if user == ():
        user = data.author.username
    else:
        user = ' '.join(user)
    s = steam()
    uid = await s.resolveVanityUrl(user)
    if uid != tr('commands.steamcalc.notFound', language):
        uid = uid['response']
    else:
        return await self.message(data.channel_id, tr('commands.steamcalc.vanityURL', language))
    if uid['success'] == 1:
        user = uid['steamid']
    games = await s.OwnedGames(user)
    try:
        games = games.get('response', {'games': {}})
    except:
        return await self.message(data.channel_id, tr('commands.steamcalc.vanityURL', language))
    if games.get('games',{}) == {}:
        return await self.message(data.channel_id, tr('commands.steamcalc.privateProfile', language))
    total_playtime = 0
    total_played = 0
    game_ids = []
    for game in games['games']:
        total_playtime += game['playtime_forever']
        game_ids += [game['appid']]
        if game['playtime_forever'] != 0:
            total_played += 1
    total_price = 0
    has_price = []
    unavailable = 0
    def calcPrice(prices, total_price, has_price):
        keys = list(prices.keys())
        for x, price in enumerate(prices.values()):
            if price['success'] and price['data'] != []:
                total_price += price['data']['price_overview']['final']
                ending = price['data']['price_overview']['currency']  #['final_formatted'].split(',')[-1][2:]
                endings = {
                    'USD': '$',
                    'EUR': '€',
                    'PLN': 'zł',
                    'GBP': '£'
                }
                ending = endings.get(ending, ending)
                has_price += [int(keys[x])]
            elif not price['success']:
                nonlocal unavailable
                unavailable += 1
        return total_price, ending, has_price
    try:
        from MFramework.utils.utils import grouper
        for chunk in grouper(game_ids, 100):
            prices = await s.getPrices(chunk, currency)
            total_price, ending, has_price = calcPrice(prices, total_price, has_price)
    except Exception as ex:
        ending = ''
        print(ex)
    from MFramework.utils.utils import truncate
    total = tr('commands.steamcalc.playtime', language, hours=truncate(total_playtime/60, 2))
    if total_price != 0:
        total += tr('commands.steamcalc.prices', language, prices=f"{total_price/100} {ending}")
    if len(has_price) != 0:
        str_prices = tr('commands.steamcalc.pricetaged', language, price_taged=len(has_price))
    else:
        str_prices = ''
    str_prices += tr('commands.steamcalc.notAvailable', language, unavailable=unavailable)
    e = Embed().addField(tr('commands.steamcalc.total', language), total, True).addField(tr('commands.steamcalc.games', language), tr('commands.steamcalc.games_desc', language, game_count=games['game_count'], total_played=total_played)  + " ({:.1%})".format(total_played / games['game_count']) + str_prices, True)
    pt = 0
    pf = 0
    for game in games['games']:
        if game['appid'] in has_price:
            if game['playtime_forever'] != 0:
                pf += 1
                pt += game['playtime_forever']
    avg = tr('commands.steamcalc.hoursPerGame', language, avg=0)
    if total_playtime != 0:
        hpg = truncate(((total_playtime / 60) / total_played), 2)
        avg = tr('commands.steamcalc.hoursPerGame', language, avg=hpg)
    if total_price != 0:
        avg += tr('commands.steamcalc.pricePerGame', language, price="{:.3}".format(truncate((total_price / 100) / len(has_price)), 2) + f"{ending}")
        if pt != 0:
            avg += tr('commands.steamcalc.pricePerHour', language, price="{:.3}".format(truncate((total_price / 100) / (pt / 60), 2)) + f"{ending}")
    e.setFooter("", f"SteamID: {user}").addField(tr('commands.steamcalc.avg', language), avg, True)
    from MFramework.utils.utils import get_main_color
    profile = await s.PlayerSummaries(user)
    profile = profile['response']['players'][0]
    e.setThumbnail(profile['avatarfull']).setAuthor(profile["personaname"],profile["profileurl"],"").setColor(get_main_color(profile['avatar']))
    await self.embed(data.channel_id, '', e.embed)
