from MFramework.commands import register
from MFramework.database.alchemy import Webhooks


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
        if "log" in data.content.casefold():
            name = "Logging"
        elif "dm" not in data.content.casefold():
            name = "RSS"
        else:
            name = "DM Inbox"
        wh = await self.create_webhook(channel, name, f"Requested by {data.author.username}")
        webhook = f"{wh.id}/{wh.token}"
    s = self.db.sql.session()
    w = Webhooks(data.guild_id, webhook, name, content, regex, data.author.id)
    s.add(w)
    s.commit()
