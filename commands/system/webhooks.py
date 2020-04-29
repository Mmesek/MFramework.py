from MFramework.commands import register
from MFramework.database.alchemy import RSS, Webhooks, Spotify


@register(group="System", help="Add RSS to watchlist")
async def add_rss(self, name, url, language, color, avatar_url=None, *args, data, **kwargs):
    s = self.db.sql.session()
    r = RSS(name, 0, url, color, language, avatar_url)
    s.add(r)
    s.commit()


@register(group="System", help="Sub current channel to a RSS source")
async def sub_rss(self, name, webhook="", content="", regex="", *args, channel, data, **kwargs):
    if "/" not in webhook:
        webhooks = await self.get_webhooks(channel)
        for wh in webhooks:
            if "user" in wh and wh.user == self.user_id:
                webhook = f"{wh.id}/{wh.token}"
                break
            elif any(s in wh.name for s in ["RSS", "DM"]):
                webhook = f"{wh.id}/{wh.token}"
                break
    if webhook == "":
        if "dm" not in data.content.casefold():
            name = "RSS"
        elif "log" in data.content.casefold():
            name = "Logging"
        else:
            name = "DM Inbox"
        wh = await self.create_webhook(channel, name, f"Requested by {data.author.username}")
        webhook = f"{wh.id}/{wh.token}"
    s = self.db.sql.session()
    w = Webhooks(data.guild_id, webhook, name, content, regex, data.author.id)
    s.add(w)
    s.commit()


@register(group="System", help="Add Artist to tracking new releases")
async def addSpotify(self, spotifyID, artist, *args, data, **kwargs):
    s = self.db.sql.session()
    spotify = Spotify(spotifyID, artist, data.author.id)
    s.add(spotify)
    s.commit()


from MFramework.utils.api import Spotify as sptfy


@register(group="System", help="Fetch new spotify releases")
async def spotify(self, *args, data, webhook=False, **kwargs):
    s = sptfy()
    await s.connect()
    try:
        embed = await s.makeList(db=self.db)
    finally:
        await s.disconnect()
    if not webhook:
        await self.embed(data.channel_id, "", embed)
    elif webhook:
        s = self.db.sql.session()
        w = s.query(Webhooks).filter(Webhooks.Source == "Spotify").all()
        for one in w:
            await self.webhook(
                [embed],
                one.Content,
                one.Webhook,
                "Spotify",
                "https://images-eu.ssl-images-amazon.com/images/I/51rttY7a%2B9L.png",
            )


from MFramework.utils.rss import rss


@register(group="System", help="Fetch RSS manually")
async def fetch_rss(self, *args, data, **kwargs):
    try:
        await rss(self, "pl")
        await rss(self, "en")
    except:
        await rss(self, "en")
