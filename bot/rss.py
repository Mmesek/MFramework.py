import feedparser, re, requests, asyncio, time, html2text
from bs4 import BeautifulSoup as bs

async def rss(endpoints, db, language): #that definitly needs to be cleaned lol
    feeds = db.RSSGetSources(language)
    embeds = []
    for source in feeds:
        print(source)
        feed = feedparser.parse(source[1])
        last = source[2]
        i    = 0
        for entry in feed['entries']:
            i   +=1
            if i==5:
                db.RSSUpdateLastEntry(source[0], int(time.mktime(feed['entries'][0]['published_parsed'])))
                break
            elif int(time.mktime(entry['published_parsed'])) != last:
                desc = bs(entry['description'],'html.parser')
                fields = []
                if '//steam' in source[1]:
                    h2t = html2text.HTML2Text()
                    h2tl = h2t.handle(desc.prettify()).replace('\n [','[').replace('\n]',']').replace('[ ','[').replace("{LINK REMOVED}",'').replace('\n\n','\n')
                else:
                    h2tl = desc.text
                try:
                    imag = ''
                    #if desc.img['src'][-3:] == '.gif':
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
                    h2tl=h2tl.replace(f"({s})[{link}]","")
                    fields += [{"name":"Steam Store","value":f"[{s}]({link})"}]
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
                embed = {
                    "title":entry['title'],
                    "description": desc.replace(' * ','\n'),
                    "url":entry['link'],
                    "color":source[3],#%z
                    "timestamp":time.strftime("%Y-%m-%dT%H:%M:%S",entry['published_parsed']),
                    "image":{"url":''},
                    "thumbnail":{"url":''},
                    "footer":{
                        "text":ftext
                    },
                    "fields":fields
                }
                if '//steam' in source[1]:
                    embed['image']['url']=imag
                else:
                    embed['thumbnail']['url'] =imag
                print(embed)
                embeds += [embed]
            elif int(time.mktime(entry['published_parsed'])) == last:
                db.RSSUpdateLastEntry(source[0], int(time.mktime(feed['entries'][0]['published_parsed'])))
                break
        if embeds != None:
            webhooks = db.subbedWebhooks(source[0])
            for sub in webhooks:
                print(sub)
                await endpoints.e.webhook(embeds, sub[1], sub[0],f"RSS: {source[0]}")
    if embeds != None:
        webhooks = db.subbedWebhooks('all')
        for webhook in webhooks:
            print(webhook)
            if len(embeds) < 11:
                await endpoints.e.webhook(embeds, webhook[1],webhook[0],'RSS')
            else:
                for embed in embeds:
                    await endpoints.e.webhook([embed], webhook[1],webhook[0],'RSS')
                    await asyncio.sleep(1)
            await asyncio.sleep(0.5)
#            await endpoints.e.webhook(embeds,webhook[1],webhook[0])
