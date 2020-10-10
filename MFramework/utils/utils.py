import time
import datetime

import i18n
def tr(key, language='en', **kwargs):
    return i18n.t(f'{language}.{key}', **kwargs)

class Embed:
    def __init__(self):
        self.embed = {"fields": []}
        self.total_characters = 0

    def setTitle(self, title):
        self.embed['title'] = title
        self.total_characters += len(str(title))
        return self

    def setDescription(self, description):
        self.embed['description'] = description
        self.total_characters += len(str(description))
        return self

    def setColor(self, color):
        self.embed['color'] = color
        return self

    def setUrl(self, url):
        self.embed['url'] = url
        return self

    def setImage(self, url):
        self.embed['image'] = {"url": url}
        return self

    def setThumbnail(self, url):
        self.embed['thumbnail'] = {"url": url}
        return self

    def setFooter(self, icon, text):
        self.embed['footer'] = {"icon_url": icon, "text": text}
        self.total_characters += len(str(text))
        return self

    def setTimestamp(self, timestamp):
        self.embed['timestamp'] = timestamp
        return self

    def setAuthor(self, name, url, icon):
        self.embed['author'] = {"name": name, "url": url, "icon_url": icon}
        self.total_characters += len(str(name))
        return self

    def addField(self, name, value, inline=False):
        self.embed['fields'] += [{"name": name,
                                  "value": value, "inline": inline}]
        self.total_characters += len(str(name)) + len(str(value))
        return self
    
    def addFields(self, title, text, inline=False):
        from textwrap import wrap
        for x, chunk in enumerate(wrap(text, 1024, replace_whitespace=False)):
            if len(self.fields) == 25:
                break
            if x == 0 and (len(title) + len(chunk) + self.total_characters) < 6000:
                self.addField(title, chunk, inline)
            elif (len('\u200b') + len(chunk) + self.total_characters) < 6000:
                self.addField('\u200b', chunk, inline)
        return self
    
    @property
    def fields(self):
        return self.embed.get('fields', [])

    @property
    def description(self):
        return self.embed.get('description','')


def created(snowflake: int) -> datetime.datetime:
    ms = ((int(snowflake) >> 22)+1420070400000)
    return datetime.datetime.utcfromtimestamp(ms//1000.0).replace(microsecond=ms % 1000*1000)

import inspect
def log(msg=""):
    try:
        func = inspect.stack()[1].function
        with open('data/log.log', 'a') as logf:
            logf.write(
                str(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())) + f': [Ex@{func}] {msg}\n')
        return
    except IOError:
        with open('data/log.log', 'a+') as logf:
            logf.write(str(time.strftime("%Y-%m-%d %H:%M:%S",
                                         time.gmtime())) + f': Created log file.\n')
    except Exception as ex:
        with open('data/log.log', 'a') as logf:
            logf.write(str(time.strftime("%Y-%m-%d %H:%M:%S",
                                         time.gmtime())) + f': Exception with log: {ex}\n')
        return
    return


def timed(func):
    def inner(*args, **kwargs):
        sum_seconds = 0.0
        start = time.perf_counter_ns()
        result = func(*args, **kwargs)
        finish = time.perf_counter_ns()
        #print('Content:',args[1].content)
        delta = (finish - start)
        sum_seconds += delta
        print(f"Time for {func.__name__}: {delta}")
        return result
    return inner


def replaceMultiple(mainString: str, toBeReplaces: list, newString: str) -> str:
    # Iterate over the strings to be replaced
    for elem in toBeReplaces:
        # Check if string is in the main string
        if elem in mainString:
            # Replace the string
            mainString = mainString.replace(elem, newString)

    return mainString


def parseMention(message: str) -> str:
    return replaceMultiple(message, ['<:', '@!', '#', '&', '<', ':>', '>', '@'], '')


def param(message: str) -> list:
    return replaceMultiple(message, ['<:', '@!', '#', '&', '<', ':>', '>', '@'], '').split(' ')[1:]


# @register(help="[link] - Quotes message")
async def quote(self, data):
    url = data['content'].split(' ')
    if len(url) > 1:
        url = url[1]
    else:
        url = url[0]
    mid = url.split('channels/')[1].split('/')
    message = await self.endpoints.get_message(mid[1], mid[2])
    embed = Embed().setDescription(
        '>>> '+message['content']).setTimestamp(message['timestamp'])
    embed.setAuthor(message['author']['username']+'#'+message['author']['discriminator'], url,
                    f"https://cdn.discordapp.com/avatars/{message['author']['id']}/{message['author']['avatar']}")
    embed.addField("Channel", f"<#{mid[1]}>", True).addField(
        "Quoted by", f"<@{data['author']['id']}>", True)
    if message['edited_timestamp'] is not None:
        embed.addField("Edited at", str(time.strftime("%Y-%m-%d %H:%M:%S",
                                                      datetime.datetime.fromisoformat(message['edited_timestamp']).timetuple())), True)
    await self.endpoints.embed(data['channel_id'], '', embed.embed)
    await self.endpoints.delete(data['channel_id'], data['id'])


def truncate(n, decimals=0):
    m = 10**decimals
    return int(n * m) / m
    
import os


def convert_bytes(num):
    """
    this function will convert bytes to MB.... GB... etc
    """
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0


def file_size(file_path):
    """
    this function will return the file size
    """
    if os.path.isfile(file_path):
        file_info = os.stat(file_path)
        return convert_bytes(file_info.st_size)


import sys
from types import ModuleType, FunctionType
from gc import get_referents

# Custom objects know their class.
# Function objects seem to know way too much, including modules.
# Exclude modules as well.
BLACKLIST = type, ModuleType, FunctionType


def getsize(obj):
    """sum size of object & members."""
    if isinstance(obj, BLACKLIST):
        raise TypeError('getsize() does not take argument of type: '+ str(type(obj)))
    seen_ids = set()
    size = 0
    objects = [obj]
    while objects:
        need_referents = []
        for obj in objects:
            if not isinstance(obj, BLACKLIST) and id(obj) not in seen_ids:
                seen_ids.add(id(obj))
                size += sys.getsizeof(obj)
                need_referents.append(obj)
        objects = get_referents(*need_referents)
    return size

def secondsToText2(secs):
    days = secs//86400
    hours = (secs - days*86400)//3600
    minutes = (secs - days*86400 - hours*3600)//60
    seconds = secs - days*86400 - hours*3600 - minutes*60
    result = ("{0} day{1}, ".format(days, "s" if days!=1 else "") if days else "") + \
    ("{0} hour{1}, ".format(hours, "s" if hours!=1 else "") if hours else "") + \
    ("{0} minute{1}, ".format(minutes, "s" if minutes!=1 else "") if minutes else "") + \
    ("{0} second{1}, ".format(seconds, "s" if seconds!=1 else "") if seconds else "")
    return result.strip(', ')

def pluralizeRussian(number, nom_sing, gen_sing, gen_pl):
    s_last_digit = str(number)[-1]

    if int(str(number)[-2:]) in range(11,20):
        #11-19
        return gen_pl
    elif s_last_digit == '1':
        #1
        return nom_sing
    elif int(s_last_digit) in range(2,5):
        #2,3,4
        return gen_sing
    else:
        #5,6,7,8,9,0
        return gen_pl
    return nom_sing if number == 1 else(gen_sing if abs(number) % 10 in [2, 3, 4] and number not in range(11, 20) else gen_pl)
    #if minutes or seconds:
        #s = "{}{}".format(("минут" if minutes else "секунд"), ("а" if number == 1 else("ы" if abs(number) % 10 in [2, 3, 4] and number not in range(11, 20) else "")))
def pluralizePolish(number):
    return "a" if number == 1 else("y" if abs(number) % 10 in [2, 3, 4] and number not in range(12, 15) else "")

def secondsToText(secs, lang="EN"):
    weeks = secs//604800
    days = (secs - weeks*604800)//86400
    hours = (secs - weeks*604800 - days*86400)//3600
    minutes = (secs - weeks*604800 - days*86400 - hours*3600)//60
    seconds = secs - weeks*604800 - days*86400 - hours*3600 - minutes*60

    weeks_text = "w"
    if lang == 'SHORT':
        days_text = "d"
        hours_text = "h"
        minutes_text = "m"
        seconds_text = "s"
    elif lang == "ES":
        days_text = "día{}".format("s" if days!=1 else "")
        hours_text = "hora{}".format("s" if hours!=1 else "")
        minutes_text = "minuto{}".format("s" if minutes!=1 else "")
        seconds_text = "segundo{}".format("s" if seconds!=1 else "")
    elif lang == "PL":
        weeks_text = "{}".format("tydzień" if weeks==1 else ("tygodnie" if abs(weeks) % 10 in [2,3,4] else "tygodni"))
        days_text = "{}".format("dni" if days!=1 else "dzień")
        hours_text = "godzin{}".format("a" if hours==1 else ("y" if abs(hours) % 10 in [2,3,4] and hours not in [12,13,14] else ""))
        minutes_text = "minut{}".format("a" if minutes==1 else ("y" if abs(minutes) % 10 in [2,3,4] and minutes not in [12,13,14] else ""))
        seconds_text = "sekund{}".format("a" if seconds==1 else ("y" if abs(seconds) % 10 in [2,3,4] and seconds not in [12,13,14] else ""))
    elif lang == "DE":
        days_text = "Tag{}".format("e" if days!=1 else "")
        hours_text = "Stunde{}".format("n" if hours!=1 else "")
        minutes_text = "Minute{}".format("n" if minutes!=1 else "")
        seconds_text = "Sekunde{}".format("n" if seconds!=1 else "")
    elif lang == "RU":
        days_text = pluralizeRussian(days, "день", "дня", "дней")
        hours_text = pluralizeRussian(hours, "час", "часа", "часов")
        minutes_text = pluralizeRussian(minutes, "минута", "минуты", "минут")
        seconds_text = pluralizeRussian(seconds, "секунда", "секунды", "секунд")
        days_text = "день" if days == 1 else("дня" if abs(days) % 10 in [2, 3, 4] and days not in range(11, 20) else "дней")
        hours_text = "час" if hours == 1 else("часа" if abs(hours) % 10 in [2, 3, 4] and hours not in range(11, 20) else "часов")
        minutes_text = "минута" if minutes == 1 else("минуты" if abs(minutes) % 10 in [2, 3, 4] and minutes not in range(11, 20) else "минут")
        seconds_text = "секунда" if seconds == 1 else("секунды" if abs(seconds) % 10 in [2, 3, 4] and seconds not in range(11, 20) else "секунд")
    else:
        weeks_text = "week{}".format("s" if weeks != 1 else "")
        days_text = "day{}".format("s" if days!=1 else "")
        hours_text = "hour{}".format("s" if hours!=1 else "")
        minutes_text = "minute{}".format("s" if minutes!=1 else "")
        seconds_text = "second{}".format("s" if seconds!=1 else "")

    result = ", ".join(filter(lambda x: bool(x), [
    "{0} {1}".format(weeks, weeks_text) if weeks else "",
    "{0} {1}".format(days, days_text) if days else "",
    "{0} {1}".format(hours, hours_text) if hours else "",
    "{0} {1}".format(minutes, minutes_text) if minutes and not weeks else "",
    "{0} {1}".format(seconds, seconds_text) if seconds and not weeks and not days else ""
    ]))
    return result

def bytes2human(n, format="%(value).1f%(symbol)s"):
    """Used by various scripts. See:
    http://goo.gl/zeJZl
    >>> bytes2human(10000)
    '9.8K'
    >>> bytes2human(100001221)
    '95.4M'
    """
    symbols = ('B', 'KB', 'MB', 'GB', 'TB', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols[1:]):
        prefix[s] = 1 << (i + 1) * 10
    for symbol in reversed(symbols[1:]):
        if n >= prefix[symbol]:
            value = float(n) / prefix[symbol]
            return format % locals()
    return format % dict(symbol=symbols[0], value=n)

def getIfromRGB(rgb : tuple):
    red = rgb[0]
    green = rgb[1]
    blue = rgb[2]
    RGBint = (red<<16) + (green<<8) + blue
    return RGBint
#int from hex: int('ff0000', 16)

def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

def ColorDistance(rgb1,rgb2):
    '''d = {} distance between two colors(3)'''
    import numpy
    rgb1 = numpy.array(rgb1)
    rgb2 = numpy.array(rgb2)
    rm = 0.5*(rgb1[0]+rgb2[0])
    d = sum((2+rm,4,3-rm)*(rgb1-rgb2)**2)**0.5
    return d

from PIL import ImageFile
import urllib
def get_main_color(img):
    file = urllib.request.urlopen(urllib.request.Request(img, headers={'User-Agent': 'Mozilla'}))#/JustCheckingImgSize'}))
    #img = Image.open(file)
    
    p = ImageFile.Parser()

    while 1:
        s = file.read(1024)
        if not s:
            break
        p.feed(s)

    im = p.close()
    try:
        r, g, b = im.getpixel((0, 0))
    except Exception as ex:
        print(img)
        r, g, b = 0,0,0
    return getIfromRGB((r, g, b))
    #colors = img.getcolors(1024*1024) #put a higher value if there are many colors in your image
    #max_occurence, most_present = 0, 0
    #try:
    #    for c in colors:
    #        if c[0] > max_occurence:
    #            if c[1] == (0, 0, 0):
    #                continue
    #            (max_occurence, most_present) = c
        #return most_present
    #except TypeError:
    #    return 0
        #raise Exception("Too many colors in the image")

def sliceindex(x):
    i = 0
    for c in x:
        if c.isalpha():
            i = i + 1
            return i
        i = i + 1

def upperfirst(x):
    i = sliceindex(x)
    if i == None:
        return x
    return x[:i].upper() + x[i:]

def grouper(iterable, n, fillvalue=None):
    from itertools import zip_longest
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)

async def get_all_reactions(self, channel_id, message_id, emoji='🎉'):
    msg = await self.get_channel_message(channel_id, message_id)
    for reaction in msg.reactions:
        if reaction.emoji.name == emoji:
            count = reaction.count
    users = []
    last_id = None
    for chunk in range(int(count / 100) + (count % 100 > 0)):
        users += await self.getreactions(channel_id, message_id, '🎉', when="after", snowflake=last_id)
        last_id = users[-1].id
    users = [i for i in users if i.id != self.user_id]
    return list(set(users))

currencies = {'€': 'EUR', '$': 'USD', '£': 'GBP'}

def get_avatar(author):
    if author.avatar:
        return f"https://cdn.discordapp.com/avatars/{author.id}/{author.avatar}.png"
    else:
        return f"https://cdn.discordapp.com/embed/avatars/{int(author.discriminator) % 5}.png"