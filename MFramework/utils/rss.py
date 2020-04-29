import feedparser, re, asyncio, time, html2text
from bs4 import BeautifulSoup as bs
from math import ceil
from . import utils

# TODO: Sort embeds from oldest


def parseEntry(entry, last, source, feed):
    desc = bs(entry["description"], "html.parser")
    embed = (
        utils.Embed().setColor(source[3]).setTimestamp(time.strftime("%Y-%m-%dT%H:%M:%S", entry["published_parsed"]))
    )
    if "//nitter" in source[1]:
        if entry["author"] == "@DyingLightGame":
            embed.setUrl(entry["link"].replace("nitter.net", "twitter.com")).setTitle(feed["title"]).setAuthor(
                entry["author"], feed["link"].replace("nitter.net", "twitter.com"), feed["image"]["url"]
            ).setDescription(entry["title"])
        else:
            return []
    else:
        embed.setTitle(entry["title"]).setUrl(entry["link"])
    if "//steam" in source[1]:
        h2t = html2text.HTML2Text()
        h2tl = (
            h2t.handle(desc.prettify())
            .replace("\n [", "[")
            .replace("\n]", "]")
            .replace("[ ", "[")
            .replace("{LINK REMOVED}", "")
            .replace("\n\n", "\n")
        )
    else:
        h2tl = desc.text
    try:
        imag = ""
        if desc.img["src"][-4:] != ".gif":
            if "//steam" in source[1]:
                imag = desc.img["src"]
            else:
                imag = desc.find("img")["src"]
    except:
        pass
    try:
        h2tl = h2tl.replace(f"![]({imag})  \n  \n", "")
    except Exception as ex:
        pass
    links_all = re.findall(r"\((https://store.steam\S*)\)\s", h2tl)
    for link in links_all:
        s = link.split("/")[-2].replace("_", " ")
        #        print(s,link)
        h2tl = h2tl.replace(f"[\n", "[").replace(f"[{link}]({link})", "")
        embed.addField("Steam Store", f"[{s}]({link})", True)
    events = re.findall(r"\((\S*/partnerevents/view/\S*)\)\s", h2tl)
    for link in events:
        h2tl = h2tl.replace(f"[\n", "[").replace(f"[{link}]({link})", "")
        embed.addField("Steam Event", f"[View Event]({link})", True)
    images = re.findall(r"\!\[\]\(\S*\)", h2tl)
    for image in images:
        h2tl = h2tl.replace(f"{image}", "")
    try:
        desc = h2tl[:2023]
    except Exception as ex:
        print("RSS Error: ", ex)
        desc = last["summary_detail"]["value"]
    if "author" in entry:
        ftext = f"{entry['author']} @ {source[0]}"
    else:
        ftext = source[0]
    if "//nitter" not in source[1]:
        embed.setFooter("", ftext).setDescription(desc.replace(" * ", "\n").replace("______", "-")[:2023])
    if "//steam" in source[1] or "//nitter" in source[1]:
        embed.setImage(imag)
    else:
        embed.setThumbnail(imag)
    return [embed.embed]


async def rss(self, language):
    feeds = await RSSGetSources(self, language)
    for source in feeds:
        embeds = []
        feed = feedparser.parse(source[1])
        last = source[2]
        highest = last
        i = 0
        for entry in feed["entries"]:
            i += 1
            current = int(time.mktime(entry["published_parsed"]))
            if current > highest:
                highest = current
            if i == 2:
                await RSSUpdateLastEntry(self, source[0], highest)
                break
            elif current != last and current > last:
                embed = parseEntry(entry, last, source, feed["feed"])
                if embed != []:
                    embeds += embed
            elif current == last:
                await RSSUpdateLastEntry(self, source[0], highest)
                break
            elif highest == last:
                print("Uh... nothing new?")
        if embeds != []:
            webhooks = await subbedWebhooks(self, source[0])
            for sub in webhooks:
                try:
                    av = feed["feed"]["image"]["url"]
                except:
                    av = ""
                await self.endpoints.webhook(embeds, sub[1], sub[0], f"{source[0]}", av)
    if embeds != []:
        webhooks = await subbedWebhooks(self, "all")
        for webhook in webhooks:
            if len(embeds) < 11:
                await self.endpoints.webhook(embeds, webhook[1], webhook[0], "RSS")
            else:
                total = ceil(len(embeds) / 10)
                for i in range(total):
                    await self.endpoints.webhook(embeds[:10], webhook[1], webhook[0], "RSS")
                    del embeds[:10]
                    await asyncio.sleep(1)
            await asyncio.sleep(0.5)


async def subbedWebhooks(self, source):
    return await self.db.selectMultiple("Webhooks", "Webhook, Content", "WHERE Source=?", [source])


async def RSSUpdateLastEntry(self, source, last):
    await self.db.update("RSS", "Last=? WHERE Source=?", [last, source])


async def RSSGetSources(self, language):
    return await self.db.selectMultiple("RSS", "Source, URL, Last, Color", "WHERE Language=?", [language])


async def refresh(self, ref):
    while ref:
        await rss(self, "pl")
        await rss(self, "en")
        asyncio.sleep(900)
