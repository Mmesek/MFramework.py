import requests
import datetime
import aiohttp

spotify_token = ''
class Spotify:
    def __init__(self, config={}):
        self.rToken = config.get("Tokens", {}).get("spotify", None)
        self.client = config.get("Spotify", {}).get("client", None)
        self.secret = config.get("Spotify", {}).get("secret", None)
        self.auth = config.get("Spotify", {}).get("auth", None)
        self.token = self.refresh(self.rToken)
        self.date = str(datetime.datetime.now())

    async def spotify_call(self, path, querry, method="GET", **kwargs):
        defaults = {
            "headers": {
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        }
        kwargs = dict(defaults, **kwargs)
        response = await self.ClientSession.request(method, "https://api.spotify.com/v1/" + path + querry, **kwargs)
        try:
            return await response.json()
        except:
            self.token = self.refresh(self.rToken, True)
            return await self.spotify_call(path, querry, method, kwargs)

    async def connect(self):
        self.ClientSession = aiohttp.ClientSession()

    async def disconnect(self):
        await self.ClientSession.close()

    def refresh(self, refresh_token, force=False):
        global spotify_token
        if spotify_token != '' and force==False:
            return spotify_token
        payload = {"grant_type": "refresh_token", "refresh_token": f"{refresh_token}"}
        print('REFRESHING!!!!!!!!!')
        r = requests.post(
            "https://accounts.spotify.com/api/token", data=payload, auth=(f"{self.client}", f"{self.secret}")
        )
        spotify_token = r.json()["access_token"]
        return r.json()["access_token"]
    
    async def search(self, query, type='artist', additional=''):
        return await self.spotify_call("search", f"?q={query.replace(' ','+')}&type={type}{additional}")

    async def searchNew(self, query, type='artist', additional=''):
        return await self.spotify_call("search", f"?q={query.replace(' ','+')}%20tag:new&type=albums{additional}")
        

    async def new(self, market="gb"):
        output = []
        data = await self.spotify_call("browse/new-releases", f"?country={market}&limit=50&offset=0")
        for i in data["albums"]["items"]:
            album = await self.check(i)
            if album is not None:
                output += [album]
                # output[album['name']] = album
        return output

    async def observed(self, db, market="gb"):
        output = []
        artists = await db.GetObservedArtists()
        for one in artists:
            data = await self.spotify_call(f"artists/{one[0]}/albums", f"?market={market}&limit=50")
            for i in data["items"]:
                album = await self.check(i, one[1])
                if album is None:
                    continue
                elif album["name"] in output:
                    # output[album['name']]['artist'] += (album['artist'])
                    output += [album]
                else:
                    output += [album]
        #                    output[album['name']] = album
        return output

    async def check(self, chunk, one="Various"):
        artist = ""
        if chunk["release_date"][:10] != self.date[:10]:
            return None
        for each in chunk["artists"]:
            if each["name"] == "Various Artists":
                # artist = artist+f"[{artist}]((https://open.spotify.com/artist/{artists[one]})"
                return None
            else:
                if artist != "":
                    artist += ", "
                artist = artist + f"[{each['name']}]({each['external_urls']['spotify']})"
        uri = chunk["uri"].replace("spotify:album:", "https://open.spotify.com/album/")
        name = f"[{chunk['name']}]({uri})"  # {artist}"
        img = chunk["images"][0]["url"]
        typ = chunk["album_type"]
        group = chunk["album_type"]
        return {"name": name, "img": img, "artist": [(artist)], "type": typ, "group": group}

    async def makeList(self, db, market="gb"):
        result = ""
        field1, field2 = "", ""
        thumbnail = ""
        nr = await self.new(market)
        ob = await self.observed(db, market)
        for item in ob:
            if thumbnail == "":
                thumbnail = ob[0]["img"]
            line = f"- {item['name']} - {item['artist'][0]}\n"
            if len(result) + len(line) < 2024:
                result += line
            elif len(field1) < 1024:
                field1 += line
        for item in nr:
            field2 += f"- {item['name']} - {item['artist'][0]}\n"
        embed = {
            "description": result,
            "color": 1947988,
            "author": {
                "name": f"New Music - {self.date[:10]}",
                "icon_url": "https://images-eu.ssl-images-amazon.com/images/I/51rttY7a%2B9L.png",
                "url": "https://open.spotify.com/browse/discover",
            },
            "thumbnail": {"url": thumbnail},
            "footer": {},
            "fields": [],
        }
        if field1 != "":
            embed["fields"] += [{"name": "\u200b", "value": field1}]
        embed["fields"] += [{"name": "Popular", "value": field2}]
        return embed


"""    async def check1(self, i, one='Various'):
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
        return output"""