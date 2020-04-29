from .utils import Embed

def MetaData(self, embed, c):
    embed.setDescription(c.content)
    embed.setTimestamp(c.timestamp)
    embed.setFooter("", f"ID: {c.author.id}")
    embed.setAuthor(f"{c.author.username}#{c.author.discriminator}", '', f"https://cdn.discordapp.com/avatars/{c.author.id}/{c.author.avatar}.png")

def Message(self, embed, message):
    #c = self.cache.get(message.guild_id).getMessage(message)
    c = self.cache[message.guild_id].getMessage(message.id)
    if c != None:
        MetaData(self, embed, c)
        if c.attachments != None:
            attachments = ''
            for a in c.attachments:
                attachments+=c.attachments[a]["filename"]+"\n"
            embed.addField("Attachments:", attachments)
        return embed

def MessageRemoved(self, message):
    embed = Embed().setTitle(f"Message deleted in <#{message.channel_id}>")
    return Message(self, embed, message)

def MessageUpdated(self, message):
    embed = Embed().setTitle(f"Message edited in <#{message.channel_id}>\nBefore:")
    Message(self, embed, message)
    embed.addField("After:", message.content[:1023])
    if len(message.content) > 1023:
        embed.addField("\u200b", message.content[1023:])
    return embed
from ..database import alchemy as db
async def DirectMessage(self, data):
    if hasattr(self, 'primary_guild'):
        gid = self.primary_guild
    else:
        gid = 463433273620824104#289739584546275339
    
    s = self.db.sql.session()
    webhook = s.query(db.Webhooks).filter(db.Webhooks.GuildID == gid).filter(db.Webhooks.Source == 'DM').first()
    if webhook == None:
        return

    embed = Embed().addField("From",f"<@{data.author.id}>", True).setDescription(data.content)#setDescription(f"From: <@{data.author.id}>")
    embed.setTimestamp(data.timestamp.split("+", 1)[0]).setFooter(f"https://cdn.discordapp.com/avatars/{data.author.id}/{data.author.avatar}.png", f"{data.author.id}")
    try:
        embed.setImage(data.attachments[0].url)
        filename = data.attachments[0].filename
    except:
        filename = ""
    
    
    color = self.cache[gid].color
    embed.setColor(color)

    if filename != "":
        embed.addField("Attachment",filename, True)#embed.embed['description'] += f"\nAttachment: {filename}"
    await self.webhook(
        [embed.embed],
        "",#data.content,
        webhook.Webhook,
        f"{data.author.username}#{data.author.discriminator}",
        f"https://cdn.discordapp.com/avatars/{data.author.id}/{data.author.avatar}.png",
    )
    await self.create_reaction(data.channel_id, data.id, self.emoji['success'])


def Channel(self, data, change):
    return

def Role(self, role):
    pass

def User(self, user):
    pass