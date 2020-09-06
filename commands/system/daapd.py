from MFramework.commands import register
from MFramework.utils.utils import secondsToText, Embed
import requests
rpc = "http://192.168.1.2:3689"

class BaseApi:
    base = "/api/"
    @classmethod
    def api(cls, path="", method="PUT", param=None):
        if param is not None:
            path += param
        return requests.request(method, rpc + cls.base+ path)


class Player(BaseApi):
    base = BaseApi.base+'player'
    @staticmethod
    def play():
        return Player.api("/play")
    @staticmethod
    def get_status():
        return Player.api(method="GET")
    @staticmethod
    def pause():
        return Player.api("/pause")
    @staticmethod
    def next():
        return Player.api('/next')
    @staticmethod
    def previous():
        return Player.api('/previous')
    @staticmethod
    def set_volume(volume):
        return Player.api("/volume", param=f"?volume={volume}")

class Queue(BaseApi):
    base = BaseApi.base+"queue"
    @staticmethod
    def queue():
        return Queue.api(method="GET")

@register(group='System', category='Daapd')
async def dplay(self, *args, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    Player.play()

@register(group='System', category='Daapd')
async def dpause(self, *args, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    Player.pause()
@register(group='System', category='Daapd')
async def dnext(self, *args, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    Player.next()

@register(group='System', category='Daapd')
async def dprevious(self, *args, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    Player.previous

@register(group='System', category='Daapd')
async def dvolume(self, new_volume, *args, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    Player.set_volume(new_volume)

@register(group='System', category='Daapd')
async def dplaying(self, *args, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    current = Player.get_status().json()
    q = Queue.queue().json()
    string = ""
    string2 = ""
    past = False
    i = 0
    current_at = 0
    for x, item in enumerate(q['items']):
        if current['item_id'] == item['id']:
            current_at = x
            past = True
            print(current)
            string += f"{item['artist']} - {item['title']} [{secondsToText(int(current['item_progress_ms']/1000))}/{secondsToText(int(current['item_length_ms']/1000))}]"
        elif past:
            i += 1
            string2 += f"{i}. {item['artist']} - {item['title']} [{secondsToText(int(item['length_ms']/1000))}]"+'\n'
            if i == 10:
                break
    embed = Embed().setTitle("Currently Playing").setDescription(string).addField("Next",string2[:1024]).setFooter("",f"Queue at: {x}/{len(q['items'])}").setThumbnail(rpc+'/artwork/nowplaying')
    await self.embed(data.channel_id, "", embed.embed)

@register(group='System', category='Daapd')
async def dhistory(self, *args, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    current = Player.get_status().json()
    q = Queue.queue().json()
    string = ""
    string2 = ""
    past = False
    i = 0
    current_at = 0
    for x, item in enumerate(q['items']):
        if current['item_id'] == item['id']:
            current_at = x
            past = True
            print(current)
            string += f"{item['artist']} - {item['title']} [{secondsToText(int(current['item_progress_ms']/1000))}/{secondsToText(int(current['item_length_ms']/1000))}]"
            break
    for item in q['items'][current_at-1:current_at-11:-1]:
        i += 1
        string2 += f"-{i}. {item['artist']} - {item['title']} [{secondsToText(int(item['length_ms']/1000))}]"+'\n'
        if i == 10:
            break
    embed = Embed().setTitle("Currently Playing").setDescription(string).addField("Previous",string2[:1024]).setFooter("",f"Queue at: {current_at}/{len(q['items'])}")
    await self.embed(data.channel_id, "", embed.embed)

async def getLyrics(artist, song):
    from bs4 import BeautifulSoup
    
    def azlyrics():
        nonlocal artist, song
        song2 = artist.replace('-','').replace(' ','').replace('the','').replace('The','').lower()
        song3 = song.replace('-', '').replace(' ', '').replace('the', '').lower()
        if '(' in song3:
            song3 = song3.split('(')[0]
        url = f'https://www.azlyrics.com/lyrics/{song2}/{song3}.html'
        req = requests.get(url)
        soup = BeautifulSoup(req.text,'html.parser')
        lyric = soup.find('div', class_='container main-page').find('div', class_="col-xs-12 col-lg-8 text-center").find('div', class_=None).text
        return lyric
    def glyrics():
        nonlocal artist, song
        if '(' in song:
            song = song.split('(')[0]
        song1 = [artist.replace(' ', '-').lower(), song.replace(' ', '').lower()]
        req = requests.get(f'https://genius.com/{song1[0]}-{song1[1]}-lyrics')
        soup = BeautifulSoup(req.text, 'html.parser')
        try:
            lyric = soup.find('div', class_='lyrics').text
            return lyric
        except Exception as ex:
            return str(ex.args)
    try:
        lyric = azlyrics()
        src = 'azlyrics'
    except Exception as ex:
        print(ex)
        lyric = glyrics()
        src = 'genius'
    lyric2 = lyric.replace('\r',"").replace('"','')
    lyric1 = lyric2.split("\n\n")
    lyrics = []
    i = 0
    if len(lyric1) < 25:
        for verse in lyric1:
            if len(verse) > 1024:
                verse = verse[0:1023]
            if verse == "":
                continue
            else:
                lyrics.append(verse)
                i=i+1
    return (lyrics, src)

@register(group='System', category='Daapd')
async def dlyrics(self, *args, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    current = Player.get_status().json()
    q = Queue.queue().json()
    for x, item in enumerate(q['items']):
        if current['item_id'] == item['id']:
            print(item)
            l = await getLyrics(item['artist'], item['title'])
            break
    embed = Embed().setTitle(f"{item['artist']} - {item['title']}").setFooter('',f"Source: {l[1]}")
    for verse in l[0]:
        embed.addField("\u200b", verse)
    await self.embed(data.channel_id, "", embed.embed)


@register(group='System', category='Daapd')
async def dstart(self, *args, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    d = Daapd()
    await d.connect()
    print('Connected')
    await d.msg()
    print('Done?')


import aiohttp
class Daapd:
    def __init__(self):
        pass
    async def connect(self):
        self.csession = aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False))
        hdr = {
            'content':
                {'notify': ["player"]}
            }
        self.ws = await self.csession.ws_connect(f"http://192.168.1.2:3688")  #, headers=hdr)
        await self.ws.send_json({"notify": ["player", "outputs"]})
        print('Established')
    async def msg(self):
        async for msg in self.ws:
            try:
                print(msg)
            except Exception as ex:
                print(f"Exception! {ex}\nType: {msg.type}\nData: {msg.data}\nExtra: {msg.extra}")
        print('reee?')