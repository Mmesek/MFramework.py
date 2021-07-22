import datetime
import json
import random
import re
import requests
from os import path
from bs4 import BeautifulSoup

from MFramework import register, Context, Groups, Embed

from mlib.localization import tr

@register(interaction=False)
async def rd(ctx: Context, number=20, *args, **kwargs):
    '''Rolls Random Number'''
    await ctx.reply(str(number) + ": " + str(random.SystemRandom().randrange(int(number)) + 1))

@register(group=Groups.GLOBAL, interaction=False)
async def randomquote(ctx: Context, *args, **kwargs):
    '''Sends random quote'''
    if not path.isfile("data/quotes.json"):
        raw = requests.get("https://raw.githubusercontent.com/dwyl/quotes/master/quotes.json")
        with open("data/quotes.json", "wb") as file:
            file.write(raw.content)
    with open("data/quotes.json", "r", newline="", encoding="utf-8") as file:
        q = json.load(file)
    r = random.SystemRandom().randrange(len(q))
    await ctx.reply('_'+q[r]["text"] + "_\n    ~" + q[r]["author"])


def load_words():
    with open("data/words.txt", encoding="utf-8") as word_file:
        valid_words = set(word_file.read().split())
    return valid_words


@register(group=Groups.GLOBAL, interaction=False, notImpl=True)
async def anagram(ctx: Context, *args, **kwargs):
    '''Assembles english words from provided letters/solves anagrams'''
    words = load_words()

    await ctx.reply(words[0])


@register(group=Groups.GLOBAL, interaction=False)
async def word(ctx: Context, word, letter_count, *args, **kwargs):
    '''Checks if provided word exists. Use * as wildcard character'''
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
    await ctx.reply(embeds=[embed])


@register(group=Groups.SYSTEM, interaction=False)
async def how(ctx: Context, *query, **kwargs):
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
        return await ctx.reply("Error")
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
    await ctx.reply([embed])


@register(group=Groups.SYSTEM, interaction=False)
async def today(ctx: Context, *difference,language, **kwargs):
    '''Summary of what is today'''
    #s = sun.sun(lat=51.15, long=22.34)
    today = datetime.datetime.now()
    d = ""
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
        return await ctx.reply(ctx.channel_id, "Error")
    f = ""
    for p in soup.find_all("h3", class_="card__title heading"):
        if "Week" in p.text or "Month" in p.text:
            continue
        else:
            f += "\n- " + p.text
    embed = Embed().setDescription(f)  # .setTitle(f"{today.year}/{month}/{day}")
    embed = embed.setTitle(today.strftime(f"%A, %B %Y (%m/%d)"))
    embed = embed.setTimestamp(datetime.datetime.now(tz=datetime.timezone.utc).isoformat())
    random.seed(today.isoformat()[:10])  # hash(today.year / today.month + today.day))
    with open("data/quotes.json", "r", newline="", encoding="utf-8") as file:
        q = json.load(file)
    quote = random.choice(q)
    #embed.addField(tr("commands.today.sun", language), tr("commands.today.sunStates", language, rise=s.sunrise(t), noon=s.solarnoon(t), set=s.sunset(t)), True)
    # embed.addField('Moon', f"Rise:\nIllumination:\nSet:", True)
    # embed.addField("Lunar Phase", f"", True)
    color = random.randint(0, 16777215)
    embed.addField(tr("commands.today.color", language), str(hex(color)).replace("0x", "#"), True).setColor(color)
    embed.addField('\u200b', '\u200b', True)
    #alternative today sources:
    #https://www.kalbi.pl/kalendarz-swiat-nietypowych
    #https://www.kalendarzswiat.pl/dzisiaj
    game_releases_url = "https://www.gry-online.pl/daty-premier-gier.asp?PLA=1"
    if '+' in d:
        game_releases_url += "&CZA=2"
    r = requests.get(game_releases_url)
    if r.status_code == 200:
        soup = BeautifulSoup(r.content, "html.parser").find('div',class_='daty-premier-2017')
    else:
        return await ctx.reply("Error")
    games = ''
    for release in soup.find_all('a', class_='box'):
        lines = release.find_all('div')
        release_date = lines[0].text
        if str(today.day) not in release_date:
            break
        p = release.find('p', class_='box-sm')
        previous_release = None
        if p:
            previous_release = p.text.replace('PC','')
        game = lines[1].contents[0]
        platform = lines[-1].text.replace(', Pudełko','')
        games += f'\n- {game} ({platform})'
        if previous_release is not None:
            games += ' | Poprzednio wydane:\n*' + previous_release.replace('\n\n', ' - ').replace('\n', '') + '*'
    if games != '':
        embed.addField("Game releases", games[:1024], True)

    r = requests.get("https://www.ign.com/upcoming/movies",
    headers={"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0"})
    if r.status_code == 200:
        soup = BeautifulSoup(r.content, "html.parser").find('div',class_='jsx-3629687597 four-grid')
    else:
        return await ctx.reply("Error")
    movies = ''
    if soup is not None:
        for movie in soup.find_all('a', class_='card-link'):
            lines = movie.find('div', class_='jsx-2539949385 details')#.find_all('div')
            release = lines.find('div', class_='jsx-2539949385 release-date').text
            if today.strftime("%b %d, %Y").replace(' 0', ' ') not in release:
                continue
            name = lines.find('div', class_='jsx-2539949385 name').text
            platform = lines.find('div', class_='jsx-2539949385 platform').text
            movies += f'\n- {name}' #({platform})'
    if movies != '':
        embed.addField("Movie releases", movies[:1024], True)
    # embed.addField("TV Show Episodes", f"", True)
    # embed.addField("New on Spotify", f"", True)
    # embed.addField("Song for today", f"", True)
    embed.addField(tr("commands.today.quote", language), quote["text"] + "\n- " + quote["author"])
    await ctx.reply(embeds=[embed])

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

@register(group=Groups.GLOBAL, interaction=False)
async def chord(ctx: Context, instrument='guitar', *chord, **kwargs):
    '''Sends Diagram of provided Chord for instrument'''
    if not hasattr(ctx.bot, 'chords'):
        await getChords(ctx.bot)
    t = ':('
    l = ''
    chord = ' '.join(chord)
    for chord_ in ctx.bot.chords.keys():
        if chord in chord_:
            t = chord_
            l = ctx.bot.chords[chord_]
    embed = Embed().setTitle(t).setImage(l)
    await ctx.reply(embeds=[embed])

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

@register(group=Groups.GLOBAL, interaction=False)
async def lyrics(ctx: Context, artist, song, *args, **kwargs):
    '''Sends Lyrics for provided song'''
    embe = await glyrics(artist, song)
    if embe == '404':
        print('falling to azlyrics')
        embe = await azlyrics(artist, song)
    if embe != '404':
        await ctx.reply(embeds=[embe])
    else:
        await ctx.reply('404')


@register(group=Groups.GLOBAL, interaction=False)
async def xkcdpassword(ctx: Context, *args, language, **kwargs):
    '''Generates random xkcd 936 styled password'''
    import secrets
    # On standard Linux systems, use a convenient dictionary file.
    # Other platforms may need to provide their own word-list.
    with open('/usr/share/dict/words') as f:
        words = [word.strip() for word in f]
        password = ' '.join(secrets.choice(words) for i in range(4))
    await ctx.reply(password)

@register(group=Groups.GLOBAL, interaction=False)
async def fileext(ctx: Context, ext, *args, language, **kwargs):
    '''Shows file extension details'''
    url = f"https://fileinfo.com/extension/{ext}"
    r = requests.get(url)
    if r.status_code == 200:
        soup = BeautifulSoup(r.content, "html.parser")
    else:
        return await ctx.reply("Error")
    article = soup.find('article')
    header = article.find('h1').text
    ftype = article.find('h2').text.replace('File Type','')
    misc = article.find('div', class_='fileHeader').find('table').find_all('tr')
    info = article.find('div', class_='infoBox').text
    e = Embed().setTitle(header).addField('File Type', ftype, True).setDescription(info).setUrl(url)
    for i in misc:
        if 'developer' in i.text.lower():
            e.addField('Developer', i.text[9:], True)
        elif 'category' in i.text.lower():
            e.addField('Category', i.text[8:], True)
        elif 'format' in i.text.lower():
            e.addField('Format', i.text[6:], True)
    await ctx.reply(embeds=[e])

@register(group=Groups.GLOBAL, interaction=False)
async def chord(ctx: Context, *chords, language, all=False, **kwargs):
    '''Shows guitar chord(s) diagram(s)'''
    import json
    with open('data/chords.json','r',newline='',encoding='utf-8') as file:
        _chords = json.load(file)
    #_chords = {"Em": "022000", "C": "x32010", "A":"x02220", "G": "320033", "E": "022100", "D": "xx0232", "F": "x3321x", "Am": "x02210", "Dm": "xx0231"}
    base_notes = "EADGBE"
    e = Embed()
    if all:
        _all = []
        for _chord in chords:
            for x in range(7):
                if x == 0:
                    if _chord in chords:
                        _all.append(f"{_chord}")
                        for i in range(5):
                            if _chord + f'_a{i+1}' in _chords:
                                _all.append(f"{_chord}_a{i+1}")    
                if _chord + f'_{x+1}' in _chords:
                    _all.append(f"{_chord}_{x+1}")
                    for i in range(5):
                        if _chord + f'_{x+1}_a{i+1}' in _chords:
                            _all.append(f"{_chord}_{x+1}_a{i+1}")
        chords = _all
    for _chord in chords:
        text = "```\n"
        try:
            _c = _chords[_chord]
        except:
            return await ctx.reply(f"Chord {_chord} not found")
        if len(_c) > 6:
            c = _c[-6:]
        for x, string in enumerate(c):
            text += string if string == 'x' else base_notes[x]
        text+='\n'
        for fret in range(1,6):
            for string in c:
                if string == str(fret):
                    text += 'O'
                else:
                    text += '|'
            text += '\n'
        text+= '```'
        if len(_c) == 7 and _c[0] not in ['0', '1']:
            #text += "\nStarting fret: " + _c[0:-6]
            _chord += f' (Fret: {_c[0:-6]})'
        e.addField(_chord, text, True)
    await ctx.reply(embeds=[e])

@register(group=Groups.SYSTEM, interaction=False)
async def add_chord(ctx: Context, chord, *frets, language, **kwargs):
    '''Adds new chord'''
    with open('data/chords.json','r',newline='',encoding='utf-8') as file:
        _chords = json.load(file)
    _chords[chord] = ''.join(frets)
    with open('data/chords.json','w',newline='',encoding='utf-8') as file:
        json.dump(_chords, file)

@register(group=Groups.GLOBAL, interaction=False)
async def tuning(ctx: Context, *tuning, language, **kwargs):
    '''Shows chords on frets for specified tuning'''
    base = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]
    if tuning == ():
        tuning = ["E", "B", "G", "D", "A", "E"]
    else:
        tuning = [i.upper() for i in tuning]
    final = ""
    for note in tuning:
        n = base.index(note)
        final += '\n' + ' | '.join([i + ' ' if len(i) == 1 else i for i in base[n:] + base[:n+1]])
    fret_numbers = ""
    fret_numbers += ' | '.join([str(i)+' ' if len(str(i)) == 1 else str(i) for i in range(len(base)+1)])
    separator = '-' * len(fret_numbers)
    await ctx.reply(f"```md\n{fret_numbers}\n{separator}{final}```")

'''
|_E_|_A_|_C_|_G_|_B_|_E_|
| _ | _ | _ | _ | _ | _ |
| _ | O | O | _ | _ | _ |
| _ | _ | _ | _ | _ | _ |
| _ | _ | _ | _ | _ | _ |
'''

@register(group=Groups.GLOBAL)
async def urban(ctx: Context, phrase: str, *args, language, **kwargs):
    '''
    Searches Urban Dictionary for provided phrase
    Params
    ------
    phrase:
        Phrase to search definition of
    '''
    await ctx.deferred()
    url = "http://api.urbandictionary.com/v0/define?term="+phrase
    r = requests.get(url)
    r = r.json()['list'][0]
    e = (Embed()
        .setTitle(r["word"])
        .setDescription(r["definition"])
        .setUrl(r["permalink"])
        .addField("Examples", r.get("examples", '...'))
        .addField("👍", str(r.get("thumbs_up", 0)), inline=True)
        .addField("👎", str(r.get("thumbs_down", 0)), inline=True)
        .setFooter(f"by {r.get('author', 'Anonymous')}")
        .setTimestamp(r["written_on"])
        .setColor(1975351)
    )
    await ctx.reply(embeds=e)
