import MFramework
from MFramework.database.alchemy import types
from typing import List, TYPE_CHECKING, Any, Tuple
if TYPE_CHECKING:
    from MFramework import Bot

class Log:
    '''Base Log class. Subclass it and overwrite `.log()` and optionally `.log_dm()` to create new log. 
    If it's about one of Discord Dispatch events, the name should match (For example: `Message_Delete` for logging deleted messages)

    Atributtes
    ----------
    username:
        Name webhook when using this logger
    avatar:
        URL to avatar to use when using this logger'''
    bot: 'Bot'
    guild_id: MFramework.Snowflake
    webhook_id: MFramework.Snowflake
    webhook_token: str
    username: str = "Basic Logger"
    avatar: str = None
    _type: str = "all"

    def __init__(self, bot: 'Bot', guild_id: MFramework.Snowflake, type:str, id: MFramework.Snowflake, token: str) -> None:
        self.bot = bot
        self._type = self.__class__.__name__.lower()
        self.guild_id = guild_id
        self.webhook_id = id
        self.webhook_token = token
    async def __call__(self, *args, **kwargs):
        return await self.log(*args, **kwargs)

    def localized(self) -> None:
        pass
    async def log(self, event: Any) -> MFramework.Message:
        raise NotImplementedError
    async def log_dm(self, event: Any, user_id: MFramework.Snowflake) -> MFramework.Message:
        raise NotImplementedError

    async def _log(self, content: str="", embeds: List[MFramework.Embed]=None, components: List[MFramework.Component]=None, *, username: str=None, avatar: str=None, thread_id: MFramework.Snowflake=None, wait:bool=None) -> MFramework.Message:
        return await self.bot.execute_webhook(self.webhook_id, self.webhook_token, content=content, username=username or self.username, allowed_mentions=MFramework.Allowed_Mentions(parse=[]), avatar_url=avatar or self.avatar, embeds=embeds, components=components, thread_id=thread_id, wait=wait)
    async def _log_dm(self, user_id: MFramework.Snowflake, content: str="", embeds: List[MFramework.Embed]=None, components: List[MFramework.Component]=None) -> MFramework.Message:
        dm_id = await self.bot.create_dm(user_id)
        return await self.bot.create_message(channel_id=dm_id, content=content, allowed_mentions=MFramework.Allowed_Mentions(parse=[]), embeds=embeds, components=components)

class Message(Log):
    username = "Message Log"
    def set_metadata(self, msg: MFramework.Message) -> MFramework.Embed:
        embed = MFramework.Embed()
        embed.setDescription(msg.content)
        embed.setTimestamp(msg.timestamp)
        embed.setFooter(f"ID: {msg.author.id}")
        embed.setAuthor(f"{msg.author.username}#{msg.author.discriminator}", None, msg.author.get_avatar())
        return embed
    def user_in_footer(self, embed: MFramework.Embed, msg: MFramework.Message) -> MFramework.Embed:
        return embed.setFooter(text=msg.author.username, icon_url=msg.author.get_avatar())

    def get_cached_message(self, key: MFramework.Snowflake) -> MFramework.Message:
        return self.bot.cache[self.guild_id].messages[key]
        #return self.bot.cache[self.guild_id].messages.get(key, None) #getMessage(message_id, channel_id)
    def cached_message(self, msg: MFramework.Message) -> MFramework.Embed:
        cached = self.get_cached_message(f"{msg.guild_id}.{msg.channel_id}.{msg.id}")
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
    async def log(self, msg: MFramework.Message) -> MFramework.Message:
        embed = self.cached_message(msg)
        embed.setTitle(f"Message edited in <#{msg.channel_id}>\nBefore:")
        embed.addFields("After:", msg.content)
        await self._log(embeds=embed)

class Message_Delete(Message):
    async def log(self, msg: MFramework.Message) -> MFramework.Message:
        embed = self.cached_message(msg)
        await self._log(
            content=f"Message deleted in <#{msg.channel_id}>", 
            embeds=[embed] if embed else None
        )

class User(Log):
    async def log(self, event: MFramework.Guild_Member) -> MFramework.Message:
        return super().log(event)

class Join(User):
    username = 'Joined Log'
    async def log(self, data: MFramework.Guild_Member_Add) -> MFramework.Message:
        return await self._log(f"<@{data.user.id}> joined server. Account created at {data.user.id.as_date}")

class Left(User):
    username = "Leave Log"
    async def log(self, data: MFramework.Guild_Member_Remove) -> MFramework.Message:
        return await self._log(f"<@{data.user.id}> left server")

class Infraction(Log):
    username = "Infraction Log"
    async def log(self, guild_id: MFramework.Snowflake, channel_id: MFramework.Snowflake, message_id: MFramework.Snowflake, moderator: MFramework.User, user_id: MFramework.Snowflake, reason: str, type: types.Infraction, duration: int=0, attachments: List[MFramework.Attachment]=None) -> MFramework.Message:
        from MFramework import Discord_Paths
        string = f'{moderator.username} [{type.name.lower()}](<{Discord_Paths.MessageLink.link.format(guild_id=guild_id, channel_id=channel_id, message_id=message_id)}>) '
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
    async def log_dm(self, type: types.Infraction, guild_id: MFramework.Snowflake, user_id: MFramework.Snowflake, reason: str="", duration: int=None) -> MFramework.Message:
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
        s = f"You've been {types[type.name.lower()]} in {self.bot.cache[guild_id].guild.name} server"
        if reason != '':
            s+=f" for {reason}"
        if duration:
            from mlib.localization import secondsToText
            s += f" ({secondsToText(duration)})"
        return await self._log_dm(user_id, s)


class Infraction_Event(Infraction):
    username = "Infraction Event Log"
    async def log(self, data: MFramework.Message, type: str, reason: str="", by_user: str="") -> MFramework.Message:
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

    async def get_ban_data(self, data: MFramework.Message, type: str, audit_type: str) -> Tuple[bool, bool]:
        import asyncio
        await asyncio.sleep(3)
        audit = await self.bot.get_guild_audit_log(data.guild_id, action_type=audit_type)
        reason = None
        for obj in audit.audit_log_entries:
            #Try to find ban in Audit Log
            if int(obj.target_id) == data.user.id:
                moderator = obj.user_id
                reason = obj.reason
                break
        if reason is None and type == 'ban':
            #Fall back to fetching ban manually
            reason = await self.bot.get_guild_ban(data.guild_id, data.user.id)
            reason = reason.reason
        r = None #TODO: Get from database
        if r is None:
            #TODO: Add to Databse
            return reason, moderator
        return False, False

class Guild_Ban_Add(Infraction_Event):
    async def log(self, data: MFramework.Message):
        reason, moderator = await self.get_ban_data(data, "ban", 22) #TODO: Move it to log, actually turn it all into a logger instead of dispatch thing
        # TODO: Hey! Idea, maybe make decorator like @onDispatch, but like @log or something to make it a logger and register etc?
        if reason is not False:
            await super().log(data, type="banned", reason=reason, by_user=moderator)

class Guild_Ban_Remove(Infraction_Event):
    async def log(self, data: MFramework.Message):
        reason, moderator = await self.get_ban_data(data, "unban", 23)
        if reason is not False:
            await super().log(data, type="unbanned", reason=reason, by_user=moderator)

class Voice(Log):
    username = "Voice Log"
    async def log(self, data: MFramework.Voice_State, channel: MFramework.Snowflake='', after: int=None) -> MFramework.Message:
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
    async def log(self, data: MFramework.Guild_Member_Update) -> MFramework.Message:
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
            if i == ctx.cache[data.guild_id].voice_link:
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
    async def log(self, data: MFramework.Guild_Member_Update) -> MFramework.Message:
        ctx = self.bot
        if data.user.id in ctx.cache[data.guild_id].members:
            c = ctx.cache[data.guild_id].members[data.user.id]
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
                if i in ctx.cache[data.guild_id].groups[MFramework.Groups.NITRO]:
                    booster = True
                    break
            if booster:
                await self._log(f"<@{data.user.id}> {case}")
                ctx.cache[data.guild_id].members[data.user.id] = data
                return s

class Muted_Change(Member_Update):
    username = "Muted Log"
    async def log(self, data: MFramework.Guild_Member_Update) -> MFramework.Message:
        ctx = self.bot
        if data.user.id in ctx.cache[data.guild_id].members:
            c = ctx.cache[data.guild_id].members[data.user.id]
            diff = set(c.roles) ^ set(data.roles)
            if len(diff) == 0:
                return
            elif any(i in data.roles for i in diff):
                case = f'has been muted'
            else:
                case = 'has been unmuted'
            muted = False
            for i in diff:
                if i in ctx.cache[data.guild_id].groups[MFramework.Groups.MUTED]:
                    muted = True
                    break
            if muted:
                await self._log(f"<@{data.user.id}> {case}")
                ctx.cache[data.guild_id].members[data.user.id] = data

class Message_Replay_QnA(Message):
    username = None
    async def log(self, msg: MFramework.types.Message) -> MFramework.Message:
        rmsg = msg.referenced_message
        question = self.set_metadata(rmsg).setTitle("Question")
        question.author = None
        question.setColor("#45f913")
        question.setUrl(MFramework.Discord_Paths.MessageLink.link.format(
            guild_id=rmsg.guild_id, channel_id=rmsg.channel_id, message_id=rmsg.id))
        self.user_in_footer(question, rmsg)
        if rmsg.attachments != []:
            question.setImage(url=rmsg.attachments[0].url)

        answer = self.set_metadata(msg).setTitle("Answer")
        answer.author = None
        answer.setColor("#ec2025")
        answer.setUrl(MFramework.Discord_Paths.MessageLink.link.format(
            guild_id=msg.guild_id, channel_id=msg.channel_id, message_id=msg.id))
        self.user_in_footer(answer, msg)
        if msg.attachments != []:
            answer.setImage(url=msg.attachments[0].url)

        await self._log(None, embeds=[question, answer])

class Stream(Log):
    username = "Stream Log"
    async def log(self, data: MFramework.types.Presence_Update, stream: MFramework.types.Activity):
        if not hasattr(self, 'logged_streams'):
            self.logged_streams = {}
        if self.logged_streams.get(data.user.id) == stream.created_at:
            return
        self.logged_streams[data.user.id] = stream.created_at
        await self._log(f"<@{data.user.id}> właśnie transmituje {stream.state} na [{stream.name}]({stream.url})!")

class Report(Log):
    username = "User Report Log"
    async def log(self, data: MFramework.types.Message) -> MFramework.Message:
        await self._log()
    async def log_dm(self, data: MFramework.types.Message, user_id: MFramework.Snowflake) -> MFramework.Message:
        await self._log_dm()
