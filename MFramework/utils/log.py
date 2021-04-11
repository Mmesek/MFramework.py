#from MFramework import Bot, Embed, Snowflake, Allowed_Mentions, Message
import MFramework
from typing import List, Dict

class Log:
    bot: MFramework.Bot
    guild_id: MFramework.Snowflake
    webhook_id: MFramework.Snowflake
    webhook_token: str
    username: str = "Basic Logger"
    avatar: str = None
    _type: str = "all"

    def __init__(self, bot: MFramework.Bot, guild_id: MFramework.Snowflake, type:str, id: MFramework.Snowflake, token: str) -> None:
        self.bot = bot
        self._type = self.__class__.__name__.lower()
        self.guild_id = guild_id
        self.webhook_id = id
        self.webhook_token = token
    async def __call__(self, *args, **kwargs):
        return await self.log(*args, **kwargs)

    def localized(self) -> None:
        pass
    async def log(self, event) -> MFramework.Message:
        raise NotImplementedError
    async def log_dm(self, event, user_id: MFramework.Snowflake) -> MFramework.Message:
        raise NotImplementedError

    async def _log(self, content: str="", embeds: List[MFramework.Embed]=None, username=None, avatar=None) -> MFramework.Message:
        return await self.bot.execute_webhook(self.webhook_id, self.webhook_token, content=content, username=username or self.username, allowed_mentions=MFramework.Allowed_Mentions(parse=[]), avatar_url=avatar or self.avatar, embeds=embeds)
    async def _log_dm(self, user_id: MFramework.Snowflake, content: str="", embed: MFramework.Embed=None) -> MFramework.Message:
        dm_id = await self.bot.create_dm(user_id)
        return await self.bot.create_message(channel_id=dm_id, content=content, allowed_mentions=MFramework.Allowed_Mentions(parse=[]), embed=embed)

class Message(Log):
    username = "Message Log"
    def set_metadata(self, msg: MFramework.Message) -> MFramework.Embed:
        embed = MFramework.Embed()
        embed.setDescription(msg.content)
        embed.setTimestamp(msg.timestamp)
        embed.setFooter(f"ID: {msg.author.id}")
        embed.setAuthor(f"{msg.author.username}#{msg.author.discriminator}", None, msg.author.get_avatar())
        return embed

    def get_cached_message(self, channel_id, message_id) -> MFramework.Message:
        return self.bot.cache[self.guild_id].getMessage(message_id, channel_id)
    def cached_message(self, msg) -> MFramework.Embed:
        cached = self.get_cached_message(msg.channel_id, msg.id)
        if cached:
            embed = self.set_metadata(cached)
            if cached.attachments != None:
                attachments = ''
                for attachment in cached.attachments:
                    attachments += attachment.filename + "\n"
                if attachments != '':
                    embed.addField("Attachments:", attachments)
            return embed

class Message_Update(Message):
    async def log(self, msg) -> MFramework.Message:
        embed = self.cached_message(msg)
        embed.setTitle(f"Message edited in <#{msg.channel_id}>\nBefore:")
        embed.addFields("After:", msg.content)
        await self._log(embeds=embed)

class Message_Delete(Message):
    async def log(self, msg) -> MFramework.Message:
        embed = self.cached_message(msg)
        await self._log(
            content=f"Message deleted in <#{msg.channel_id}>", 
            embeds=[embed] if embed else None
        )

class User(Log):
    async def log(self, event) -> MFramework.Message:
        return super().log(event)

class Join(User):
    username = 'Joined Log'
    async def log(self, data) -> MFramework.Message:
        return await self._log(f"<@{data.user.id}> joined server. Account created at {data.user.id.as_date}")

class Left(User):
    username = "Leave Log"
    async def log(self, data) -> MFramework.Message:
        return await self._log(f"<@{data.user.id}> left server")

class Infraction(Log):
    username = "Infraction Log"
    async def log(self, guild_id, channel_id, message_id, moderator, user_id, reason, type, duration=0, attachments=None) -> MFramework.Message:
        from MFramework import Discord_Paths
        string = f'{moderator.author.username} [{type}](<{Discord_Paths.link(Discord_Paths.MessageLink).format(guild_id=guild_id, channel_id=channel_id, message_id=message_id)}>) '
        u = f'[<@{user_id}>'
        try:
            user = self.bot.cache[guild_id].members[user_id].user
            u += f' | {user.username}#{user.discriminator}'
        except:
            pass
        u += ']'
        string += u
        if reason != '':
            string += f' for "{reason}"'
        if duration:
            from mlib.localization import secondsToText
            string += f" (Duration: {secondsToText(duration)})"
        embeds = []
        if attachments is not None:
            for attachment in attachments:
                if len(embeds) == 10:
                    break
                embeds.append(MFramework.Embed().setImage(attachment.url).setTitle(attachment.filename).embed)
        await self._log(content=string, embeds=embeds)
    async def log_dm(self, type, guild_id, user_id: MFramework.Snowflake, reason="", duration=None) -> MFramework.Message:
        types = {
            "warn": "warned",
            "tempmute":"temporarily muted",
            "mute": "muted",
            "kick": "kicked",
            "tempban":"temporarily banned",
            "ban": "banned",
            "unban": "unbanned",
            "unmute": "unmuted"
        } #HACK
        s = f"You've been {types[type]} in {self.bot.cache[guild_id].name} server"
        if reason != '':
            s+=f" for {reason}"
        if duration:
            from mlib.localization import secondsToText
            s += f" ({secondsToText(duration)})"
        return await self._log_dm(user_id, s)


class Infraction_Event(Infraction):
    username = "Infraction Event Log"
    async def log(self, data, type, reason="", by_user="") -> MFramework.Message:
        if by_user != '':
            try:
                by_user = self.bot.cache[data.guild_id].members[int(by_user)].user.username
            except:
                pass
            string = f'{by_user} {type} [<@{data.user.id}> | {data.user.username}#{data.user.discriminator}]'
        else:
            string = f'[<@{data.user.id}> | {data.user.username}#{data.user.discriminator}] has been {type}'
        if reason != '' and reason != 'Unspecified':
            string += f' for "{reason}"'
        await self._log(string)

class Voice(Log):
    username = "Voice Log"
    async def log(self, data, channel='', after=None) -> MFramework.Message:
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
            channel = self.bot.cache[data.guild_id].afk_channel
        string += f'<#{channel}>'
        if after is not None and after > 0:
            from mlib.localization import secondsToText
            string += f" after {secondsToText(after)}"
        await self._log(string, username=self.username+ f' [{status}]')

class Member_Update(Log):
    username = "Member Update Log"
    async def log(self, data) -> MFramework.Message:
        ctx = self.bot
        if data.user.id not in ctx.cache[data.guild_id].members:
            return
        c = ctx.cache[data.guild_id].members[data.user.id]
        diff = set(c.roles) ^ set(data.roles)
        
        if len(diff) == 0:
            return # Something else
        elif any(i in data.roles for i in diff):
            case = 'added'
        else:
            case = 'removed'
        roles = ""
        for i in diff:
            if i == ctx.cache[data.guild_id].VoiceLink:
                if len(diff) == 1:
                    return
                continue
            roles += f"<@&{i}> "
        s =''
        if len(diff) > 1:
            s = 's'
        string = f"<@{data.user.id}> role{s} {case}: {roles}"
        await self._log(string)
        ctx.cache[data.guild_id].members[data.user.id] = data

class Nitro_Change(Member_Update):
    username = "Nitro Log"
    async def log(self, data) -> MFramework.Message:
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
                await self._log(f"<@{data.user.id}> {case}")
                self.cache[data.guild_id].members[data.user.id] = data
                return s

class Muted_Change(Member_Update):
    username = "Muted Log"
    async def log(self, data) -> MFramework.Message:
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
                await self._log(f"<@{data.user.id}> {case}")
                self.cache[data.guild_id].members[data.user.id] = data

class Direct_Message(Message):
    def __init__(self, bot: MFramework.Bot, guild_id: MFramework.Snowflake, type: str, id: MFramework.Snowflake, token: str) -> None:
        super().__init__(bot, guild_id, type, id, token)
    async def log(self, msg) -> MFramework.Message:
        embed = self.set_metadata(msg)
        avatar = msg.author.get_avatar()
        embed.author.icon_url = None
        embed.footer.icon_url = avatar
        embed.footer.text = msg.author.id
        from .utils import check_attachments
        embed = check_attachments(msg, embed)

        embed.setColor(self.bot.cache[self.guild_id].color)
        canned = self.bot.cache[self.guild_id].canned

        from mlib.localization import tr
        if (len(set(msg.content.lower().split(' '))) < 2) and len(msg.attachments) == 0:
            return await msg.reply(tr("commands.dm.singleWordError", self.bot.cache[self.guild_id].language, emoji_success=self.bot.emoji['success']))

        if msg.channel_id in self.bot.cache['dm']:
            s = list(self.bot.cache['dm'][msg.channel_id].messages.keys())
            if self.bot.cache['dm'][msg.channel_id].messages[s[-1]].content == msg.content:
                return await msg.reply(tr("commands.dm.sameMessageError", self.bot.cache[self.guild_id].language))
                #"Please do not send same message multiple times in a row, thanks."

        import re
        reg = re.search(canned['patterns'], msg.content)
        content = ''
        if reg and reg.lastgroup is not None:
            await msg.reply(canned['responses'][reg.lastgroup])
            content = tr("commands.dm.cannedResponseError", self.bot.cache[self.guild_id].language, canned_response=reg.lastgroup)
            #f"Canned response `{reg.lastgroup}` has been sent in return."
        await self._log(content+f' <@!{msg.author.id}>', [embed], f"{msg.author.username}#{msg.author.discriminator}", avatar)
        await msg.react(self.bot.emoji['success'])


from mlib.utils import all_subclasses
def create_loggers(ctx: MFramework.Bot, guild_id: MFramework.Snowflake) -> Dict[str, Log]:
    loggers = {}
    webhooks = ctx.cache[guild_id].logging
    _classes = {i.__name__.lower():i for i in all_subclasses(Log)}
    for webhook in webhooks:
        if webhook in _classes:
            loggers[webhook] = _classes[webhook](ctx, guild_id, webhook, *webhooks[webhook])
    return loggers