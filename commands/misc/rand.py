import datetime
import json
import random
import re
from os import path

import requests
from bs4 import BeautifulSoup

import MFramework.utils.sun as sun
from MFramework.commands import register
from MFramework.utils.utils import Embed

from MFramework.utils.utils import tr
@register(help="Rolls Random Number")
async def rd(self, number=20, *args, data, **kwargs):
    await self.message(data.channel_id, str(number) + ": " + str(random.SystemRandom().randrange(int(number)) + 1))


@register(group="Global", help="Sends random quote", alias="", category="")
async def randomquote(self, *args, data, **kwargs):
    if not path.isfile("data/quotes.json"):
        raw = requests.get("https://raw.githubusercontent.com/dwyl/quotes/master/quotes.json")
        with open("data/quotes.json", "wb") as file:
            file.write(raw.content)
    with open("data/quotes.json", "r", newline="", encoding="utf-8") as file:
        q = json.load(file)
    r = random.randrange(len(q))
    await self.message(data.channel_id, '_'+q[r]["text"] + "_\n    ~" + q[r]["author"])


def load_words():
    with open("data/words.txt", encoding="utf-8") as word_file:
        valid_words = set(word_file.read().split())
    return valid_words


@register(group="Global", help="Assembles english words from provided letters/solves anagrams", alias="", category="", notImpl=True)
async def anagram(self, *args, data, **kwargs):
    words = load_words()

    await self.message(data.channel_id, words[0])


@register(group="Global", help="Checks if provided word exists. Use * as wildcard character", alias="", category="")
async def word(self, word, letter_count, *args, data, **kwargs):
    dig = int(letter_count)
    m = word.replace("*", "(.+?)")
    reg = re.compile(r"(?i)" + m)
    res = []
    words = load_words()
    for _word in words:
        if len(_word) == int(dig):
            ree = reg.search(_word)
            if ree != None:
                res += [_word]
    embed = Embed().setTitle("Words matching provided criteria: "+word+f" ({letter_count})")
    field = ''
    for word in res:
        if len(field) + len(word) < 1024:
            field += ' ' + word
        else:
            embed.addField("\u200b", field)
            field = word
    if field != '':
        embed.addField('\u200b', field)
    await self.embed(data.channel_id, '', embed.embed)


@register(group="System", notImpl=True)
async def how(self, *query, data, **kwargs):
    query = "".join(query).replace(" ", "+")
    language = "en"
    limit = 4
    resp = requests.get(
        f"https://google.com/search?q=how+{query}&hl={language}&gl={language}",
        headers={"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0"},
    )
    results = []
    if resp.status_code == 200:
        soup = BeautifulSoup(resp.content, "html.parser")
    else:
        return await self.message(data.channel_id, "Error")
    for x, g in enumerate(soup.find_all("div", class_="r")):
        anchors = g.find_all("a")
        if anchors:
            link = anchors[0]["href"]
            title = g.find("h3").text
            item = {"title": title, "link": link}
            results.append(item)
    for x, s in enumerate(soup.find_all("div", class_="s")):
        desc = s.find("span", class_="st").text
        results[x]["description"] = desc

    embed = Embed()
    for x, result in enumerate(results):
        embed.addField(result["title"], f"[Link]({result['link']})\n{result['description'][:900]}")
        if x == limit:
            break
    await self.embed(data.channel_id, "", embed.embed)


@register(group="System", help="Summary of what is today")
async def today(self, *difference, data, language, **kwargs):
    s = sun.sun(lat=51.15, long=22.34)
    today = datetime.datetime.now(datetime.timezone.utc)
    if difference != ():
        d = ''.join(difference)
        d = '-'+d if '+' not in d else d
        today = today + datetime.timedelta(days=int(d))
    month = today.month
    day = today.day
    if month <= 9:
        month = "0" + str(month)
    if day <= 9:
        day = "0" + str(day)
    t = datetime.datetime.fromisoformat(f"{today.year}-{month}-{day}T23:59")
    query = f"https://www.daysoftheyear.com/days/{today.year}/{month}/{day}/"
    r = requests.get(
        query,
        headers={"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0"},
    )
    if r.status_code == 200:
        soup = BeautifulSoup(r.content, "html.parser")
    else:
        return await self.message(data.channel_id, "Error")
    f = ""
    for p in soup.find_all("h3", class_="card__title heading"):
        if "Week" in p.text or "Month" in p.text:
            continue
        else:
            f += "\n- " + p.text
    embed = Embed().setDescription(f)  # .setTitle(f"{today.year}/{month}/{day}")
    embed = embed.setTitle(today.strftime(f"%A, %B %Y (%m/%d)"))
    embed = embed.setTimestamp(today.isoformat())
    random.seed(today.isoformat()[:10])  # hash(today.year / today.month + today.day))
    with open("data/quotes.json", "r", newline="", encoding="utf-8") as file:
        q = json.load(file)
    quote = random.choice(q)
    embed.addField(tr("commands.today.sun", language), tr("commands.today.sunStates", language, rise=s.sunrise(t), noon=s.solarnoon(t), set=s.sunset(t)), True)
    # embed.addField('Moon', f"Rise:\nIllumination:\nSet:", True)
    # embed.addField("Lunar Phase", f"", True)
    # embed.addField("Game releases", f"", True)
    # embed.addField("Movie releases", f"", True)
    # embed.addField("TV Show Episodes", f"", True)
    # embed.addField("New on Spotify", f"", True)
    # embed.addField("Song for today", f"", True)
    color = random.randint(0, 16777215)
    embed.addField(tr("commands.today.color", language), str(hex(color)).replace("0x", "#"), True).setColor(color)
    embed.addField(tr("commands.today.quote", language), quote["text"] + "\n- " + quote["author"])
    await self.embed(data.channel_id, "", embed.embed)

async def getLink(url):
    r = requests.get(
        url,
        headers={"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0"},
    )
    if r.status_code == 200:
        return BeautifulSoup(r.content, "html.parser")
    print(r.reason)

async def getChords(self):
    print('getting chords')
    self.chords = {}
    guitar_chords = "https://chordify.net/chord-diagrams/guitar"
    r = await getLink(guitar_chords)
    for i in r.find_all("a", class_="diagram-wrap"):
        for img in i.find_all('img'):
            self.chords[img['alt']] = 'https:' + img['src']

@register(group='Global', help='Sends Diagram of provided Chord for instrument', notImpl=True)
async def chord(self, instrument='guitar', *chord, data, **kwargs):
    if not hasattr(self, 'chords'):
        await getChords(self)
    t = ':('
    l = ''
    chord = ' '.join(chord)
    for chord_ in self.chords.keys():
        if chord in chord_:
            t = chord_
            l = self.chords[chord_]
    embed = Embed().setTitle(t).setImage(l)
    await self.embed(data.channel_id, "", embed.embed)

@register(group='Global', help='Converts Ascii to Numbers', notImpl=True)
async def asciitohex(self, *ascii_, data, **kwargs):
    ascii_ = ' '.join(ascii_)
    f = Embed().setTitle('Ascii to Hex').setDescription(ascii_)
    f.addField('Dec',str(int.from_bytes(bytearray(ascii_, 'ascii'),'big'))[2:1023])
    f.addField('Bin',str(bin(int.from_bytes(bytearray(ascii_, encoding='ascii'), 'big')))[2:1023])
    f.addField('Hex',str(hex(int.from_bytes(bytearray(ascii_, encoding='ascii'), 'big')))[2:1023])
    f.addField('Oct',str(oct(int.from_bytes(bytearray(ascii_, encoding='ascii'), 'big')))[2:1023])
    await self.embed(data.channel_id, '', f.embed)

@register(group='Global', help='Converts currency', alias='cc, currency')
async def currency_exchange(self, amount='1', currency='EUR', to_currency='USD', *args, data, **kwargs):
    currency, to_currency = currency.upper(), to_currency.upper()
    r = requests.get(f'https://api.exchangeratesapi.io/latest?base={currency}&symbols={to_currency}')
    try:
        amount = float(amount.replace(',','.').replace(' ',''))
        r = "%3.2f %s from %s %s" % (amount * float(r.json()['rates'][to_currency]), to_currency, amount, currency)
    except KeyError:
        r = r.json().get('error','Error')
    await self.message(data.channel_id, r)

async def azlyrics(artist, song):
    #song1 = song.split(' - ',1)
    #song2 = song1[0].replace('-','').replace(' ','').replace('the','').casefold()
    #song3 = song1[1].replace('-','').replace(' ','').replace('the','').casefold()
    song1 = (artist, song)
    song2 = artist.replace('-','').replace(' ','').replace('the','').casefold()
    song3 = song.replace('-','').replace(' ','').replace('the','').casefold()
#    print(song1, song2, song3)
    try:
        url = f'https://www.azlyrics.com/lyrics/{song3}/{song2}.html'
        song = f'{song1[1]} - {song1[0]}'
        req = requests.get(url)
        soup = BeautifulSoup(req.text,'html.parser')
        lyric = soup.find('div',class_='container main-page').find('div',class_="col-xs-12 col-lg-8 text-center").find('div', class_=None).text
    except:
        try:
            url = f'https://www.azlyrics.com/lyrics/{song2}/{song3}.html'
            song = f'{song1[0]} - {song1[1]}'
            req = requests.get(url)
            soup = BeautifulSoup(req.text,'html.parser')
            lyric = soup.find('div',class_='container main-page').find('div',class_="col-xs-12 col-lg-8 text-center").find('div', class_=None).text
        except:
            return '404' 
    with open(f'lyrics/{song}.txt','w',newline='') as file:
        file.write(lyric)
    lyric = lyric.replace('\r',"")
    lyric1 = lyric.split("\n\n")
    fields = []
    i = 0
    if len(lyric1) < 25:
        for verse in lyric1:
            if len(verse) > 1024:
                verse = verse[0:1023]
            if verse == "":
                pass
            else:
                fields.append({"name":"\u200b","value":verse})
                i=i+1
    try:
        embed = {
            "title": song,
            #"description": '\u200b',#lyric1,
            "fields": fields
        }
    except:
        return '404'
    return embed

async def glyrics(artist, song):
    song1 = (artist.lower(), song.lower())
    #song1 = song.replace(' ','-').lower().split('---',1)
    #print(song1)
    try:
        req = requests.get(f'https://genius.com/{song1[0]}-{song1[1]}-lyrics')
        song1[1] = song1[1].replace('-',' ').capitalize()
        song1[0] = song1[0].replace('-',' ').capitalize()
        song = f'{song1[0]} - {song1[1]}'
        soup = BeautifulSoup(req.text,'html.parser')
        lyric = soup.find('div',class_='lyrics').text
    except:
        try:
            req = requests.get(f'https://genius.com/{song1[1]}-{song1[0]}-lyrics')
            song1[1] = song1[1].replace('-',' ').capitalize()
            song1[0] = song1[0].replace('-',' ').capitalize()
            song = f'{song1[1]} - {song1[0]}'
            soup = BeautifulSoup(req.text,'html.parser')
            lyric = soup.find('div',class_='lyrics').text
        except:
            return '404'
    with open(f'lyrics/{song}.txt','w',newline='', encoding='utf8') as file:
        file.write(lyric)
    lyric = lyric.replace('\r',"").replace('"','')
    lyric1 = lyric.split("\n\n")
    fields = []
    i = 0
    if len(lyric1) < 25:
        for verse in lyric1:
            if len(verse) > 1024:
                verse = verse[0:1023]
            if verse == "":
                continue
            else:
                fields.append({"name":"\u200b","value":verse})
                i=i+1
    try:
        embed = {
            "title": song,
            "fields": fields
        }
    except:
        return '404'
    return embed

@register(group='Global', help='Sends Lyrics for provided song')
async def lyrics(self, artist, song, *args, data, **kwargs):
    embe = await glyrics(artist, song)
    if embe == '404':
        print('falling to azlyrics')
        embe = await azlyrics(artist, song)
    if embe != '404':
        await self.embed(data.channel_id, '', embe)
    else:
        await self.message(data.channel_id, '404')


@register(group='Global', help='Generates random xkcd 936 styled password')
async def xkcdpassword(self, *args, data, language, **kwargs):
    import secrets
    # On standard Linux systems, use a convenient dictionary file.
    # Other platforms may need to provide their own word-list.
    with open('/usr/share/dict/words') as f:
        words = [word.strip() for word in f]
        password = ' '.join(secrets.choice(words) for i in range(4))
    await self.message(data.channel_id, password)