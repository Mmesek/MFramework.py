from enum import Enum

class URL(Enum):
    STEAM = "http://api.steampowered.com/"
    STORE = "https://store.steampowered.com/api/"

class Steam:
    def __init__(self, token):
        self.token = token

    async def api_call(self=None, path="", querry="", method="GET", api=URL.STEAM, **kwargs):
        import aiohttp
        async with aiohttp.ClientSession() as session:
            request = await session.request(method, api.value + path + querry, **kwargs)
            try:
                return await request.json()
            except:
                return request.reason
    async def resolveVanityUrl(self, username):
        return await self.api_call(f"ISteamUser/ResolveVanityURL/v0001/?key={self.token}&vanityurl={username}")
    async def getPrices(self, steamids, currency):
        return await self.api_call(f"appdetails?appids={','.join([str(i) for i in steamids[:100]])}&filters=price_overview&cc={currency}", api=URL.STORE)

    async def OwnedGames(self, steamid):
        return await self.api_call("IPlayerService/GetOwnedGames/v0001/", f"?key={self.token}&steamid={steamid}&format=json")

    async def PlayerSummaries(self, steamids):
        return await self.api_call("ISteamUser/GetPlayerSummaries/v2/", f"?key={self.token}&steamids={steamids}")

    async def getAppList(self, language='english'):
        return await self.api_call("IStoreService/GetAppList/v1/", f"?key={self.token}&have_description_language={language}")

    async def News(self, appid):
        return await self.api_call("ISteamNews/GetNewsForApp/v2/", f"?appid={appid}")

    @staticmethod
    async def CurrentPlayers(appid):
        return await Steam.api_call(path="ISteamUserStats/GetNumberOfCurrentPlayers/v1/", querry=f"?appid={appid}")

    async def AppList(self):
        return await self.api_call("ISteamApps/GetAppList/v2")

    async def Featured(self):
        return await self.api_call("featured/", api=URL.STORE)

    @staticmethod
    async def appDetails(appid, language):
        if language == 'pl':
            cc = 'pl'
            l = 'polish'
        else:
            cc = 'us'
            l = 'english'
        return await Steam.api_call(path="appdetails/", querry=f"?appids={appid}&l={l}&cc={cc}", api=URL.STORE)

async def loadSteamIndex(ctx):
    with open("data/steamstoreindex.json") as fjson:
        import json
        ctx.bot.index = json.load(fjson)