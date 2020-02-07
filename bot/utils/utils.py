import time
import datetime


class Embed:
    def __init__(self):
        self.embed = {"fields": []}

    def setTitle(self, title):
        self.embed['title'] = title
        return self

    def setDescription(self, description):
        self.embed['description'] = description
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
        return self

    def setTimestamp(self, timestamp):
        self.embed['timestamp'] = timestamp
        return self

    def setAuthor(self, name, url, icon):
        self.embed['author'] = {"name": name, "url": url, "icon_url": icon}
        return self

    def addField(self, name, value, inline=False):
        self.embed['fields'] += [{"name": name,
                                  "value": value, "inline": inline}]
        return self


async def created(snowflake: int) -> datetime.datetime:
    ms = ((int(snowflake) >> 22)+1420070400000)
    return datetime.datetime.utcfromtimestamp(ms//1000.0).replace(microsecond=ms % 1000*1000)


def log(msg=""):
    try:
        with open('bot/data/log.log', 'a') as logf:
            logf.write(
                str(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())) + f': {msg}\n')
        return
    except IOError:
        with open('bot/data/log.log', 'a+') as logf:
            logf.write(str(time.strftime("%Y-%m-%d %H:%M:%S",
                                         time.gmtime())) + f': Created log file.\n')
    except Exception as ex:
        with open('bot/data/log.log', 'a') as logf:
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
    return int(n*m)/m