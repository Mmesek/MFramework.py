import requests, json, operator, time, datetime, asyncio, aiohttp
from config import cfg as config
class Spotify:
    def __init__(self):
        self.rToken  = config['Tokens']['spotify']
        self.client  = config['Spotify']['client']
        self.secret  = config['Spotify']['secret']
        self.auth    = config['Spotify']['auth']
        self.token   = self.refresh(self.rToken)
        self.date    = str(datetime.datetime.now())

    async def spotify_call(self, path, querry, method="GET", **kwargs):
        defaults = {"headers":{"Authorization": f"Bearer {self.token}", "Accept": "application/json", "Content-Type": "application/json"}}
        kwargs = dict(defaults,**kwargs)
        response = await self.ClientSession.request(method, "https://api.spotify.com/v1/"+path+querry, **kwargs)
        try:
            return await response.json()
        except:
            return
    async def connect(self):
        self.ClientSession = aiohttp.ClientSession()
    async def disconnect(self):
        await self.ClientSession.close()
    def refresh(self, refresh_token):
        payload = {
            'grant_type': 'refresh_token',
            'refresh_token': f'{refresh_token}'
        }
        r = requests.post('https://accounts.spotify.com/api/token', data=payload,auth=(f'{self.client}', f'{self.secret}'))
        return r.json()['access_token']

    async def new(self, market='gb'):
        output = {}
        data = await self.spotify_call('browse/new-releases',f'?country={market}&limit=50&offset=0')
        for i in data.albums.items:
            album = self.check(i)
            output[album['name']] += album
        return output

    async def observed(self, db, market='gb'):
        output = {}
        artists = db.GetObservedArtists()
        for one in artists:
            data = await self.spotify_call(f'artists/{one}/albums',f'?market={market}&limit=50')
            for i in data.items:
                album = await self.check(i, one)
                if album == None:
                    continue
                elif album['name'] in output:
                    output[album['name']]['artist'] += (album['artist'])
                else:
                    output[album['name']] = album
        return output

    async def check(self, chunk, one='Various'):
        artist = ''
        if chunk['release_date'][:10] != self.date[:10]:
            return None
        for each in chunk['artists']:
            if each['name'] == 'Various Artists':
                return None#artist = artist+f"[{artist}]((https://open.spotify.com/artist/{artists[one]})"
            else:
                if artist != '':
                    artist +=', '
                artist = artist+f"[{each['name']}]({each['external_urls']['spotify']})"
        uri     = chunk['uri'].replace('spotify:album:','https://open.spotify.com/album/')
        name    = f"[{chunk['name']}]({uri})"#{artist}"
        img     = chunk['images'][0]['url']
        typ     = chunk['album_type']
        group   = chunk['album_group']
        return {"name":name,"img":img,"artist":[(artist)],"type":typ,"group":group}

    async def makeList(self, db, market='gb'):
        result = ''
        field1,field2 = '',''
        thumbnail= ''
        nr = self.new(market)
        ob = self.observed(db, market)
        for item in ob:
            if thumbnail == '':
                thumbnail = ob[0]['name']
            line=f"- {item['name']} - {item['artist']}\n"
            if len(result)+len(line) < 2024:
                result+=line
            elif len(field1) < 1024:
                field1+=line
        for item in nr:
            field2+=f"- {item['name']} - {item['artist']}"
        embed = {"description":result,"color":1947988,"author":{"name":f"New Music - {self.date[:10]}",
        "icon_url":"https://images-eu.ssl-images-amazon.com/images/I/51rttY7a%2B9L.png",
        "url":"https://open.spotify.com/browse/discover"},"thumbnail":{"url":thumbnail},"footer":{},"fields":[]}
        embed['fields'] += [{"name":'\u200b','value':field1}]
        embed['fields'] += [{"name":'\u200b','value':field2}]
        return embed

'''    async def check1(self, i, one='Various'):
        for each in i['artists']:
            if len(i['artists']) == 1 and each['name'] != 'Various Artists' and each['name'] != 'Various':
                #print(len(i['artists']), each['name'])
                artist = f"[{one}](https://open.spotify.com/artist/{artists[one]})"
            elif each['name'] == 'Various Artists':
#                return output
                artist = artist+f"[{one}](https://open.spotify.com/artist/{artists[one]})"
            else:
                if artist != '':
                    artist = artist+', '
                artist = artist+f"[{each['name']}]({each['external_urls']['spotify']})"
        if typ == 'appears_on' or typ == 'compilation':
            typ = 0
        else:
            typ = 1
        if date[0:10] == release[0:10]:
            if 'Party' not in i['name'] and'Pop' not in i['name'] and 'Club' not in i['name'] and 'Spice' not in i['name'] and 'Dance' not in i['name'] and 'Mix' not in i['name']:
                output = output+[([name],[release],[image],[typ], [artist])]#,[typ]]]
        return output'''


class Steam:
    #def __init__(self):
    token = config['Tokens']['steam']
    steam = 'http://api.steampowered.com/'
    store = 'https://store.steampowered.com/api/'
    async def api_call(self, path, querry='', method="GET", api="http://api.steampowered.com/", **kwargs):
        async with aiohttp.ClientSession() as session:
            request = await session.request(method, api+path+querry, **kwargs)
            #print(await request.json())
            try: 
                return await request.json()
            except:
                return await request.reason()
    async def OwnedGames(self,steamid):
        return await self.api_call("/IPlayerService/GetOwnedGames/v0001/",f"?key={self.token}&steamid={steamid}&format=json")
    async def PlayerSummaries(self,steamids):
        return await self.api_call("ISteamUser/GetPlayerSummaries/v2/",f"?key={self.token}&steamid={steamids}")
    async def getAppList(self):
        return await self.api_call("IStoreService/GetAppList/v1/",f"?key={self.token}&have_description_language=english")
    async def News(self,appid):
        return await self.api_call("ISteamNews/GetNewsForApp/v2/",f"?appid={appid}")
    @staticmethod
    async def CurrentPlayers(appid):
        return await Steam.api_call('ISteamUserStats/GetNumberOfCurrentPlayers/v1/',f'?appid={appid}')
    async def AppList(self):
        return await self.api_call("ISteamApps/GetAppList/v2")
    async def Featured(self):
        return await self.api_call('featured/', api=self.store)
    @staticmethod
    async def appDetails(appid):
        return await Steam.api_call('appdetails/',f'?appids={appid}&l=polish', api=Steam.store)
    
from utils import Embed
class Twitter:
    def __init__(self):
        self.token  = config['Tokens']['twitter']
        self.client = config['Twitter']['Client']
        self.secret = config['Twitter']['Secret']
        self.auth   = config['Twitter']['Auth']
    async def twitter_call(self, path,querry,method="GET", **kwargs):
        defaults = {"headers":{"Authorization": f"Bearer {self.token}", "Accept": "application/json", "Content-Type": "application/json"}}
        kwargs = dict(defaults,**kwargs)
        response = await self.ClientSession.request(method, "https://api.twitter.com/1.1/"+path+'?'+querry, **kwargs)
        try:
            return await response.json()
        except:
            return
    async def connect(self):
        self.ClientSession = aiohttp.ClientSession()
    async def disconnect(self):
        await self.ClientSession.close()
    async def user_timeline(self, db, user):
        tweet = await self.twitter_call('statuses/user_timeline.json',f'screen_name={user}&count=1&include_rts=false')
        last_tweet_id = db.GetLastTweet(user)
        if tweet[0]["id_str"] != last_tweet_id:
            embed = Embed().setDescription(tweet[0]["text"]).setAuthor(tweet[0]["user"]["name"],f"https://twitter.com/{tweet[0]['user']['screen_name']}",tweet[0]['user']['profile_image_url'])
            embed.setColor(int(tweet[0]['user']['profile_background_color'],16)).setFooter('',tweet[0]['created_at'])
            db.updateLastTweet(user, tweet[0]['id_str'])
            return embed
        return