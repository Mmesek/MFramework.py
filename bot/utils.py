import time, datetime

class Embed:
    def __init__(self):
        self.embed = {"fields":[]}
    def setTitle(self, title):
        self.embed['title'] = title
        return self
    def setDescription(self, description):
        self.embed['description'] = description
        return self
    def setColor(self, color):
        self.embed['color'] = color
        return self
    def setImage(self, url):
        self.embed['image'] = {"url":url}
        return self
    def setThumbnail(self, url):
        self.embed['thumbnail'] = {"url": url}
        return self
    def setFooter(self, url, text):
        self.embed['footer'] = {"icon_url":url, "text":text}
        return self
    def setTimestamp(self, timestamp):
        self.embed['timestamp'] = timestamp
        return self
    def setAuthor(self, name, url, icon):
        self.embed['author'] = {"name":name, "url":url, "icon_url":icon}
        return self
    def addField(self, name, value, inline=False):
        self.embed['fields'] += [{"name":name, "value":value, "inline":inline}]
        return self

async def created(snowflake):
    ms = ((int(snowflake) >> 22)+1420070400000)
    return datetime.datetime.utcfromtimestamp(ms//1000.0).replace(microsecond=ms%1000*1000)

def log(msg=""):
    try:
        with open('logs/log.log','a') as logf:
            logf.write(str(time.strftime("%Y-%m-%d %H:%M:%S",time.gmtime())) + f': {msg}\n')
        return
    except Exception as ex:
        with open('logs/log.log','a') as logf:
            logf.write(str(time.strftime("%Y-%m-%d %H:%M:%S",time.gmtime())) + f': Exception with log: {ex}\n')
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
        print (f"Time for {func.__name__}: {delta}")
        return result
    return inner

def replaceMultiple(mainString, toBeReplaces, newString):
    # Iterate over the strings to be replaced
    for elem in toBeReplaces :
        # Check if string is in the main string
        if elem in mainString :
            # Replace the string
            mainString = mainString.replace(elem, newString)
    
    return  mainString

def param(message):
    return replaceMultiple(message,['<:','@','#','&','<',':>','>','!'],'').split(' ')[1:]