from typing import TYPE_CHECKING, Any

import MFramework

if TYPE_CHECKING:
    from MFramework import Bot


class Log:
    """Base Log class. Subclass it and overwrite `.log()` and optionally `.log_dm()` to create new log.
    If it's about one of Discord Dispatch events, the name should match (For example: `Message_Delete` for logging deleted messages)

    Attributes
    ----------
    username:
        Name webhook when using this logger
    avatar:
        URL to avatar to use when using this logger"""

    bot: "Bot"
    guild_id: MFramework.Snowflake
    webhook_id: MFramework.Snowflake
    webhook_token: str
    username: str = "Basic Logger"
    avatar: str = None
    _type: str = "all"
    supported_channel_types: list[MFramework.Channel_Types] = [
        MFramework.Channel_Types.GUILD_TEXT,
        MFramework.Channel_Types.PRIVATE_THREAD,
        MFramework.Channel_Types.PUBLIC_THREAD,
    ]

    def __init__(
        self,
        bot: "Bot",
        guild_id: MFramework.Snowflake,
        type: str,
        id: MFramework.Snowflake,
        token: str,
        thread_id: MFramework.Snowflake,
    ) -> None:
        self.bot = bot
        self._type = self.__class__.__name__.lower()
        self.guild_id = guild_id
        self.webhook_id = id
        self.webhook_token = token
        self.thread_id = thread_id

    async def __call__(self, *args, **kwargs):
        return await self.log(*args, **kwargs)

    def localized(self) -> None:
        pass

    async def log(self, event: Any) -> MFramework.Message:
        raise NotImplementedError

    async def log_dm(self, event: Any, user_id: MFramework.Snowflake) -> MFramework.Message:
        raise NotImplementedError

    async def _log(
        self,
        content: str = None,
        embeds: list[MFramework.Embed] = None,
        components: list[MFramework.Component] = None,
        *,
        username: str = None,
        avatar: str = None,
        thread_id: MFramework.Snowflake = None,
        wait: bool = None,
    ) -> MFramework.Message:
        return await self.bot.execute_webhook(
            self.webhook_id,
            self.webhook_token,
            content=content,
            username=username or self.username,
            allowed_mentions=MFramework.Allowed_Mentions(parse=[]),
            avatar_url=avatar or self.avatar,
            embeds=embeds,
            components=components,
            thread_id=thread_id or self.thread_id,
            wait=wait,
        )

    async def _log_dm(
        self,
        user_id: MFramework.Snowflake,
        content: str = None,
        embeds: list[MFramework.Embed] = None,
        components: list[MFramework.Component] = None,
    ) -> MFramework.Message:
        _dm = await self.bot.create_dm(user_id)
        return await self.bot.create_message(
            channel_id=_dm.id,
            content=content,
            allowed_mentions=MFramework.Allowed_Mentions(parse=[]),
            embeds=embeds,
            components=components,
        )


class Message(Log):
    username = "Message Log"

    def set_metadata(self, msg: MFramework.Message) -> MFramework.Embed:
        embed = MFramework.Embed()
        embed.setDescription(msg.content)
        embed.setTimestamp(msg.timestamp)
        embed.setFooter(f"ID: {msg.author.id}")
        embed.setAuthor(
            f"{msg.author.username}#{msg.author.discriminator}",
            icon_url=msg.author.get_avatar(),
        )
        return embed

    def user_in_footer(self, embed: MFramework.Embed, msg: MFramework.Message) -> MFramework.Embed:
        return embed.setFooter(text=msg.author.username, icon_url=msg.author.get_avatar())

    async def get_cached_message(self, key: MFramework.Snowflake) -> MFramework.Message:
        return await self.bot.cache[self.guild_id].messages[key]

    async def cached_message(self, msg: MFramework.Message) -> MFramework.Embed:
        cached = await self.get_cached_message(f"{msg.guild_id}.{msg.channel_id}.{msg.id}")
        if cached:
            embed = self.set_metadata(cached)
            if cached.attachments:
                attachments = ""
                for attachment in cached.attachments:
                    attachments += attachment.filename + "\n"
                if attachments != "":
                    embed.addField("Attachments:", attachments)
            return embed


class Message_Update(Message):
    async def log(self, msg: MFramework.Message) -> MFramework.Message:
        embed = await self.cached_message(msg)
        embed.setTitle(f"Message edited in <#{msg.channel_id}>\nBefore:")
        embed.addFields("After:", msg.content)
        await self._log(embeds=embed)


class Message_Delete(Message):
    async def log(self, msg: MFramework.Message) -> MFramework.Message:
        embed = await self.cached_message(msg)
        await self._log(
            content=f"Message deleted in <#{msg.channel_id}>",
            embeds=[embed] if embed else None,
        )


class User(Log):
    async def log(self, event: MFramework.Guild_Member) -> MFramework.Message:
        return super().log(event)


class Guild_Member_Add(User):
    username = "Joined Log"

    async def log(self, data: MFramework.Guild_Member_Add) -> MFramework.Message:
        return await self._log(f"<@{data.user.id}> joined server. Account created at {data.user.id.as_date}")


class Guild_Member_Remove(User):
    username = "Leave Log"

    async def log(self, data: MFramework.Guild_Member_Remove) -> MFramework.Message:
        return await self._log(f"<@{data.user.id}> left server")


class Voice(Log):
    username = "Voice Log"

    async def log(
        self,
        data: MFramework.Voice_State,
        channel: MFramework.Snowflake = "",
        after: int = None,
    ) -> MFramework.Message:
        string = f"<@{data.user_id}> "
        if channel != "" and data.channel_id != channel and data.channel_id != 0:
            string += f"moved from <#{channel}> to "
            status = "|"
            channel = data.channel_id
        elif data.channel_id == 0:
            string += "left "
            status = "-"
        else:
            string += "joined "
            status = "+"
            channel = data.channel_id
        if channel == -1:
            channel = self.bot.cache[data.guild_id].afk_channel  # FIXME?
        string += f"<#{channel}>"
        if after is not None and after > 0:
            from mlib.localization import secondsToText

            string += f" after {secondsToText(after)}"
        await self._log(string, username=self.username + f" [{status}]")


class Guild_Member_Update(Log):
    username = "Member Update Log"

    async def log(self, data: MFramework.Guild_Member_Update) -> MFramework.Message:
        ctx = self.bot
        if not await ctx.cache[data.guild_id].members.has(data.user.id):
            return
        c = await ctx.cache[data.guild_id].members[data.user.id]
        diff = set(c.roles) ^ set(data.roles)

        if len(diff) == 0:
            return  # Something else
        elif any(i in data.roles for i in diff):
            case = "added"
        else:
            case = "removed"
        roles = ""
        for i in diff:
            if i == ctx.cache[data.guild_id].voice_link:  # FIXME?
                if len(diff) == 1:
                    return
                continue
            roles += f"<@&{i}> "
        s = ""
        if len(diff) > 1:
            s = "s"
        string = f"<@{data.user.id}> role{s} {case}: {roles}"
        await self._log(string)
        await ctx.cache[data.guild_id].members.update(data)


class Nitro_Change(Guild_Member_Update):
    username = "Nitro Log"

    async def log(self, data: MFramework.Guild_Member_Update) -> MFramework.Message:
        ctx = self.bot
        if await ctx.cache[data.guild_id].members.has(data.user.id):
            c = await ctx.cache[data.guild_id].members[data.user.id]
            diff = set(c.roles) ^ set(data.roles)
            if len(diff) == 0:
                return
            elif any(i in data.roles for i in diff) and data.premium_since is not None:
                case = "started boosting"
                s = True
            else:
                s = False
                case = "stopped boosting"
            booster = False
            for i in diff:
                if i in ctx.cache[data.guild_id].groups[MFramework.Groups.NITRO]:
                    booster = True
                    break
            if booster:
                await self._log(f"<@{data.user.id}> {case}")
                await ctx.cache[data.guild_id].members.update(data)
                return s


class Muted_Change(Guild_Member_Update):
    username = "Muted Log"

    async def log(self, data: MFramework.Guild_Member_Update) -> MFramework.Message:
        ctx = self.bot
        if await ctx.cache[data.guild_id].members.has(data.user.id):
            c = await ctx.cache[data.guild_id].members[data.user.id]
            diff = set(c.roles) ^ set(data.roles)
            if len(diff) == 0:
                return
            elif any(i in data.roles for i in diff):
                case = "has been muted"
            else:
                case = "has been unmuted"
            muted = False
            for i in diff:
                if i in ctx.cache[data.guild_id].groups[MFramework.Groups.MUTED]:
                    muted = True
                    break
            if muted:
                await self._log(f"<@{data.user.id}> {case}")
                await ctx.cache[data.guild_id].members.update(data)
