import feedparser, re, requests, asyncio, time, html2text
from bs4 import BeautifulSoup as bs
from math import ceil
import bot.utils as utils
#import utils

#TODO: Sort embeds from oldest

def parseEntry(self, entry, last, source, feed):
    desc = bs(entry['description'],'html.parser')
    embed = utils.Embed().setColor(source[3]).setTimestamp(time.strftime("%Y-%m-%dT%H:%M:%S",entry['published_parsed']))
    if  '//nitter' in source[1]:
        if entry['author'] == '@DyingLightGame':
            embed.setUrl(entry['link'].replace('nitter.net','twitter.com')).setTitle(feed['title']).setAuthor(entry['author'],feed['link'].replace('nitter.net','twitter.com'),feed['image']['url']).setDescription(entry['title'])
        else:
            return []
    else:
        embed.setTitle(entry['title']).setUrl(entry['link'])
    if '//steam' in source[1]:
        h2t = html2text.HTML2Text()
        h2tl = h2t.handle(desc.prettify()).replace('\n [','[').replace('\n]',']').replace('[ ','[').replace("{LINK REMOVED}",'').replace('\n\n','\n')
    else:
        h2tl = desc.text
    try:
        imag = ''
        if desc.img['src'][-4:] != '.gif':
            if '//steam' in source[1]:
                imag = desc.img['src']
            else:
                imag=desc.find('img')['src']
    except:
        pass
    try:
        h2tl = h2tl.replace(f'![]({imag})  \n  \n','')
    except Exception as ex:
        pass
    links_all = re.findall(r'\((https://store.steam\S*)\)\s',h2tl)
    for link in links_all:
        s = link.split('/')[-2].replace('_',' ')
#        print(s,link)
        h2tl=h2tl.replace(f"[\n","[").replace(f"[{link}]({link})","")
        embed.addField("Steam Store",f"[{s}]({link})",True)
    events = re.findall(r'\((\S*/partnerevents/view/\S*)\)\s',h2tl)
    for link in events:
        h2tl=h2tl.replace(f"[\n","[").replace(f"[{link}]({link})","")
        embed.addField("Steam Event",f"[View Event]({link})",True)
    images = re.findall(r'\!\[\]\(\S*\)',h2tl)
    for image in images:
        h2tl=h2tl.replace(f"{image}",'')
    try:
        desc = h2tl[:2023]
    except Exception as ex:
        print("RSS Error: ",ex)
        desc = last['summary_detail']['value']
    if 'author' in entry:
        ftext = f"{entry['author']} @ {source[0]}"
    else:
        ftext = source[0]
    if '//nitter' not in source[1]:
        embed.setFooter('',ftext).setDescription(desc.replace(' * ','\n').replace('______','-')[:2023])
    if '//steam' in source[1] or '//nitter' in source[1]:
        embed.setImage(imag)
    else:
        embed.setThumbnail(imag)
    return [embed.embed]

async def rss(self, language):
    feeds = self.db.RSSGetSources(language)
    for source in feeds:
        embeds = []
        feed = feedparser.parse(source[1])
        last = source[2]
        highest = last
        i    = 0
        for entry in feed['entries']:
            i   +=1
            current = int(time.mktime(entry['published_parsed']))
            if current > highest:
                highest=current
            if i==2:
                self.db.RSSUpdateLastEntry(source[0], highest)
                break
            elif current != last and current > last:
                embed = parseEntry(self, entry, last, source,feed['feed'])
                if embed != []:
                    embeds += embed
            elif current == last:
                self.db.RSSUpdateLastEntry(source[0], highest)
                break
            elif highest == last:
                print('Uh... nothing new?')
        if embeds != None:
            webhooks = self.db.subbedWebhooks(source[0])
            for sub in webhooks:
                av = feed['feed']['image']['url']
                await self.endpoints.webhook(embeds, sub[1], sub[0],f"{source[0]}", av)
    if embeds != None:
        webhooks = self.db.subbedWebhooks('all')
        for webhook in webhooks:
            if len(embeds) < 11:
                await self.endpoints.webhook(embeds, webhook[1],webhook[0],'RSS')
            else:
                total = ceil(len(embeds) / 10)
                for i in range(total):
                    await self.endpoints.webhook(embeds[:10], webhook[1],webhook[0],'RSS')
                    del embeds[:10]
                    await asyncio.sleep(1)
            await asyncio.sleep(0.5)

nitter_parsed = 1578412819
steam_parsed = 0

import requests

class db():
    def __init__(self):
        pass
    def subbedWebhooks(self, source):
        if source != 'all':
#            return [('','https://discordapp.com/api/webhooks/665572342403170314/77SWAx082_agZMZa47E_3xFp4zwtuBOyHKBbUd53pxP7CGbamJh2aF15qqr0BHIRH_y3')]
            return [('','https://discordapp.com/api/webhooks/651726756234919946/rkKk-enkmYxmq6SLzReliFxOIYNLi7RZUkeE9LZBqQtdfEDL16OibBwFmnWe6L85JgXF')]
        else:
            return []
    def RSSUpdateLastEntry(self, source, last):
        print('last',last)
    def RSSGetSources(self, language):
        return [('Dying Light Twitter','https://nitter.net/DyingLightGame/rss',nitter_parsed,'16744744'),
        ('Dying Light Steam','https://steamcommunity.com/games/239140/rss/?l=english',steam_parsed,'16744744'),
        ('Dying Light 2 Steam','https://steamcommunity.com/games/534380/rss/?l=english',steam_parsed,'16744744')
        ]

class endpoints():
    def __init__(self):
        pass
    async def webhook(self, embed,webhook, content, nick, avatar=''):
        r = requests.post(
            webhook, json={"content":content,"embeds":embed, "username":nick,"avatar_url":avatar},
            headers={'Content-Type': 'application/json'}
        )
        print("Webhook status code:", r.status_code, r.text)


class Test():
    def __init__(self):
        self.db = db()
        self.endpoints = endpoints()
    async def run(self):
        await rss(self, 'pl')

if __name__ == "__main__":
    test = Test()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(test.run())
    loop.close()
