from .utils import Embed, created, tr

def MetaData(self, embed, c):
    embed.setDescription(c.content)
    embed.setTimestamp(c.timestamp)
    embed.setFooter("", f"ID: {c.author.id}")
    embed.setAuthor(f"{c.author.username}#{c.author.discriminator}", '', f"https://cdn.discordapp.com/avatars/{c.author.id}/{c.author.avatar}.png")

def Message(self, embed, message):
    #c = self.cache.get(message.guild_id).getMessage(message)
    try:
        c = self.cache[message.guild_id].getMessage(message.id, message.channel_id)
    except:
        return None
    if c != None:
        MetaData(self, embed, c)
        if c.attachments != None:
            attachments = ''
            for a in c.attachments:
                attachments += c.attachments[a]["filename"] + "\n"
            if attachments != '':
                embed.addField("Attachments:", attachments)
        return embed

async def MessageRemoved(self, message):
    webhook = getWebhook(self, message.guild_id, 'message_delete')
    if webhook is None:
        return
    embed = Embed()  #.setTitle(
    embed = Message(self, embed, message)
    if embed != None:
        await self.webhook([embed.embed], f"Message deleted in <#{message.channel_id}>", webhook, 'Message Log', None, {'parse': []})
    else:
        await self.webhook({}, f"Messaged deleted in <#{message.channel_id}>", webhook, 'Message Log', None, {'parse':[]})

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
        await self.message(data.channel_id, "Hey, it looks like no channel was specified to send a DM to therefore the whole DM forwarding is disabled")
        return
    d = s.query(db.Servers).filter(db.Servers.GuildID == gid).first()
    d.DMCount += 1



    embed = Embed()#.addField("From",f"<@{data.author.id}>", True)
    embed.setDescription(data.content)  #setDescription(f"From: <@{data.author.id}>")
    if data.author.avatar:
        avatar = f"https://cdn.discordapp.com/avatars/{data.author.id}/{data.author.avatar}.png"
    else:
        avatar = f"https://cdn.discordapp.com/avatars/embed/avatars/{int(data.author.discriminator) % 5}.png"
    embed.setTimestamp(data.timestamp.split("+", 1)[0]).setFooter(avatar, f"{data.author.id}").setAuthor(f'{data.author.username}#{data.author.discriminator}','','')
    content, filename = '', ''
    try:
        embed.setImage(data.attachments[0].url)
        if data.attachments[0].url[-3:] not in ['png', 'jpg', 'jpeg', 'webp', 'gif'] or len(data.attachments) > 1:
            for i in data.attachments:
                filename += f'[{i.filename}]({i.url})\n'
            embed.addField("Attachments", filename[:1024], True)
            filename = ''
        else:
            filename = data.attachments[0].filename
    except:
        filename = ""
    
    color = self.cache[gid].color
    embed.setColor(color)
    canned = self.cache[gid].canned
    s.commit()
    if filename != "":
        embed.addField("Image", filename, True)  #embed.embed['description'] += f"\nAttachment: {filename}"
    if (len(set(data.content.lower().split(' '))) < 2) and len(data.attachments) == 0:
        await self.message(data.channel_id, tr("commands.dm.singleWordError", self.cache[gid].language, emoji_success=self.emoji['success']))
        #await self.message(data.channel_id, f"Hey, it appears your message consist of mostly single word, therefore I'm not going to forward it. I'm forwarding your messages here automatically and <:{self.emoji['success']}> under message means it was successfully delivered to mod team. Please form a sentence and try again. Cheers mate.")
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
        content+f' <@!{data.author.id}>',#data.content,
        webhook.Webhook,
        f"{data.author.username}#{data.author.discriminator}",
        avatar, {"parse":[]}
    )
    await self.create_reaction(data.channel_id, data.id, self.emoji['success'])
    s = self.db.sql.session()
    d = s.query(db.Servers).filter(db.Servers.GuildID == gid).first()
    d.DMCountForwarded += 1
    s.commit()


def Channel(self, data, change):
    return

def Role(self, role):
    pass

def User(self, user):
    pass

def getWebhook(self, guild_id: int, logger: str):
    webhook = self.cache[guild_id].logging
    if not any(i in webhook for i in ["all", logger]):
        return None
    if logger in webhook:
        webhook = webhook[logger]
    else:
        webhook = webhook["all"]
    return webhook
from .utils import secondsToText
async def UserVoiceChannel(self, data, channel='', after=None):
    webhook = getWebhook(self, data.guild_id, 'voice_log')
    if webhook is None:
        return
    string = f'<@{data.user_id}> '
    if channel != '' and data.channel_id != channel and data.channel_id != 0:
        string += f'moved from <#{channel}> to '
        status = '|'
        channel = data.channel_id
    elif data.channel_id == 0:
        string += 'left '
        status = '-'
    else:
        string += 'joined '
        status = '+'
        channel = data.channel_id
    if channel == -1:
        channel = self.cache[data.guild_id].afk_channel
    string += f'<#{channel}>'
    if after is not None and after > 0:
        string += f" after {secondsToText(after)}"
    await self.webhook({}, string, webhook, f'Voice Log [{status}]', None, {'parse': []})


async def Infraction(self, data, user, type, reason, attachments=[]):
    webhook = getWebhook(self, data.guild_id, 'infraction_log')
    embeds = []
    if webhook is None:
        return
    string = f'[<@{data.author.id}> | {data.author.username}] {type} <@{user}>'
    for mention in data.mentions:
        if mention.id == user:
            string += f' | {mention.username}#{mention.discriminator}'
    if reason != '':
        string += f' for "{reason}"'
    if attachments != []:
        for attachment in attachments:
            if len(embeds) == 10:
                break
            embeds += [Embed().setImage(attachment.url).setTitle(attachment.filename).embed]
    await self.webhook(embeds, string, webhook, 'Infraction Log', None, {'parse': []})

async def InfractionEvent(self, data, type, reason='', by_user=''):
    webhook = getWebhook(self, data.guild_id, 'infraction_event_log')
    if webhook is None:
        return
    if by_user != '':
        string = f'<@{by_user}> {type} <@{data.user.id}>'
    else:
        string = f'<@{data.user.id}> has been {type}'
    string += f' | {data.user.username}#{data.user.discriminator}'
    if reason != '' and reason != 'Unspecified':
        string += f' for "{reason}"'
    await self.webhook({}, string, webhook, 'Infraction Event Log', None, {'parse': []})

async def UserJoinedGuild(self, data):
    webhook = getWebhook(self, data.guild_id, 'join_log')
    if webhook is None:
        return
    string = f"<@{data.user.id}> joined server. Account created at {created(data.user.id)}"
    await self.webhook({}, string, webhook, 'Joined Log', None, {'parse': []})
    
async def UserLeftGuild(self, data):
    webhook = getWebhook(self, data.guild_id, 'join_log')
    if webhook is None:
        return
    string = f"<@{data.user.id}> left server"
    await self.webhook({}, string, webhook, 'Leave Log', None, {'parse': []})
    
async def MemberUpdate(self, data):
    webhook = getWebhook(self, data.guild_id, 'member_update_log')
    if webhook is None:
        return
    if data.user.id in self.cache[data.guild_id].members:
        c = self.cache[data.guild_id].members[data.user.id]
        diff = set(c.roles) ^ set(data.roles)
        
        if len(diff) == 0:
            return
            case = "Something else"
        elif any(i in data.roles for i in diff):
            case = 'added'
        else:
            case = 'removed'
        roles = ""
        for i in diff:
            if i == self.cache[data.guild_id].VoiceLink:
                if len(diff) == 1:
                    return
                continue
            roles += f"<@&{i}> "
        s =''
        if len(diff) > 1:
            s = 's'
        string = f"<@{data.user.id}> role{s} {case}: {roles}"
        await self.webhook({}, string, webhook, 'Member Update Log', None, {'parse': []})
        self.cache[data.guild_id].members[data.user.id] = data

async def NitroChange(self, data):
    webhook = getWebhook(self, data.guild_id, 'nitro_log')
    if webhook is None:
        return
    if data.user.id in self.cache[data.guild_id].members:
        c = self.cache[data.guild_id].members[data.user.id]
        diff = set(c.roles) ^ set(data.roles)
        if len(diff) == 0:
            return

        elif any(i in data.roles for i in diff) and data.premium_since is not None:
            case = 'started boosting'
            s = True
        else:
            s = False
            case = 'stopped boosting'
        booster = False
        for i in diff:
            if i in self.cache[data.guild_id].groups['Nitro']:
                booster = True
                break
        if booster:
            string = f"<@{data.user.id}> {case}"
            await self.webhook({}, string, webhook, 'Nitro Log', None, {'parse': []})
            self.cache[data.guild_id].members[data.user.id] = data
            return s

async def MutedChange(self, data):
    webhook = getWebhook(self, data.guild_id, 'muted_log')
    if webhook is None:
        return
    if data.user.id in self.cache[data.guild_id].members:
        c = self.cache[data.guild_id].members[data.user.id]
        diff = set(c.roles) ^ set(data.roles)
        if len(diff) == 0:
            return

        elif any(i in data.roles for i in diff):
            case = f'has been muted'
        else:
            case = 'has been unmuted'
        muted = False
        for i in diff:
            if i in self.cache[data.guild_id].groups['Muted']:
                muted = True
                break
        if muted:
            string = f"<@{data.user.id}> {case}"
            await self.webhook({}, string, webhook, 'Mute Log', None, {'parse': []})
            self.cache[data.guild_id].members[data.user.id] = data

async def _MemberUpdate(self, data):
    webhooks = ['member_update_log', 'nitro_log', 'muted_log']
    for x, webhook in enumerate(webhooks):
        webhook = getWebhook(self, data.guild_id, 'nitro_log')
        if webhook is None:
            return
        if data.user.id in self.cache[data.guild_id].members:
            c = self.cache[data.guild_id].members[data.user.id]
            diff = set(c.roles) ^ set(data.roles)
            if len(diff) == 0:
                return
            elif any(i in data.roles for i in diff):
                case = 'added'
            else:
                case = 'removed'
            roles = ""
            booster = False
            muted = False
            for i in diff:
                if i == self.cache[data.guild_id].VoiceLink:
                    if len(diff) == 1:
                        return
                    continue
                elif i in self.cache[data.guild_id].groups['Nitro']:
                    booster = True
                    if i in data.roles and data.premium_since is not None:
                        case = 'started boosting'
                    else:
                        case = 'stopped boosting'
                elif i in self.cache[data.guild_id].groups['Muted']:
                    muted = True
                    if i in data.roles:
                        case = f'has been <@{i}>'
                    else:
                        case = f'has been unmuted'
                roles += f"<@&{i}> "
            s =''
            if len(diff) > 1:
                s = 's'
            string = f"<@{data.user.id}> role{s} {case}: {roles}"
            if booster or muted:
                string = f"<@{data.user.id}> {case}"

            logs = ['Member Update Log', 'Nitro Log', 'Muted Log']
            await self.webhook({}, string, webhook, logs[x], None, {'parse': []})
            self.cache[data.guild_id].members[data.user.id] = data