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
import re
async def DirectMessage(self, data):
    if hasattr(self, 'primary_guild'):
        gid = self.primary_guild
    else:
        gid = 463433273620824104#289739584546275339
    
    s = self.db.sql.session()
    webhook = s.query(db.Webhooks).filter(db.Webhooks.GuildID == gid).filter(db.Webhooks.Source == 'DM').first()
    if webhook == None:
        self.message(data.channel_id, "Hey, it looks like no channel was specified to send a DM to therefore the whole DM forwarding is disabled")
        return

    embed = Embed().addField("From",f"<@{data.author.id}>", True).setDescription(data.content)#setDescription(f"From: <@{data.author.id}>")
    embed.setTimestamp(data.timestamp.split("+", 1)[0]).setFooter(f"https://cdn.discordapp.com/avatars/{data.author.id}/{data.author.avatar}.png", f"{data.author.id}")
    try:
        embed.setImage(data.attachments[0].url)
        filename = data.attachments[0].filename
    except:
        filename = ""
    content = ''
    
    color = self.cache[gid].color
    embed.setColor(color)
    canned = self.cache[gid].canned
    if filename != "":
        embed.addField("Attachment", filename, True)  #embed.embed['description'] += f"\nAttachment: {filename}"
    if len(set(data.content.lower().split(' '))) < 2:
        await self.message(data.channel_id, f"Hey, it appears your message consist of mostly single word, therefore I'm not going to forward it. I'm forwarding your messages here automatically and <:{self.emoji['success']}> under message means it was successfully delivered to mod team. Please form a sentence and try again. Cheers mate.")
        return
    if data.channel_id in self.cache['dm']:
        s = list(self.cache['dm'][data.channel_id].messages.keys())
        if self.cache['dm'][data.channel_id].messages[s[-1]].content == data.content:
            await self.message(data.channel_id, "Please do not send same message multiple times in a row, thanks.")
            return
    reg = re.search(canned['patterns'], data.content)
    if reg and reg.lastgroup is not None:
        await self.message(data.channel_id, canned['responses'][reg.lastgroup])
        content = f"Canned response `{reg.lastgroup}` has been sent in return."
    await self.webhook(
        [embed.embed],
        content,#data.content,
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