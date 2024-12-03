from typing import TYPE_CHECKING

from mdiscord import (
    Allowed_Mentions,
    Attachment,
    Channel,
    Component,
    Embed,
    Guild,
    Guild_Member,
    Interaction,
    Message,
    Message_Flags,
    Message_Reference,
    Sendable,
    Snowflake,
    User,
)

from MFramework.commands.command import Command
from MFramework.cache import Cache
from MFramework.database.database import Database

if TYPE_CHECKING:
    from MFramework.bot import Bot

from .localized import Localizable


class Context(Sendable, Localizable):
    """This is meant as an unified context object used for universal
    commands that can be issued as both a message or an interaction"""

    cache: Cache = Cache
    db: Database
    bot: "Bot"
    data: Message | Interaction

    guild_id: Snowflake
    guild: Guild
    channel_id: Snowflake
    channel: Channel
    message_id: Snowflake
    user_id: Snowflake
    user: User
    member: Guild_Member

    direct_message: Snowflake
    language: str = "en"

    is_message: bool
    is_interaction: bool

    def __init__(self, cache: Cache, bot: "Bot", data: Message | Interaction, cmd: Command = None):
        self.cache = cache[data.guild_id]
        self.bot = bot
        self.db = bot.db
        self.data = data
        self.guild_id = data.guild_id
        if data.guild_id:
            self.guild = self.cache.guild
            self.language = self.cache.language  # FIXME?
        self.channel_id = data.channel_id
        self.message_id = data.id
        if type(data) is Interaction:
            if data.user:
                self.user_id = data.user.id
                self.user = data.user
                self.member = None
            else:
                self.user_id = data.member.user.id
                self.user = data.member.user
                self.member = data.member
            self.is_message = False
            self.is_interaction = True
        else:
            self.user_id = data.author.id
            self.user = data.author
            try:
                self.member = data.member or cache.members.get(data.user_id, None) or Guild_Member()
            except:
                self.member = Guild_Member()
            self.member.user = data.author
            self.is_interaction = False
            self.is_message = True
        self.direct_message = cache[0].get(self.user_id, None)
        self.webhook = None
        self._deferred = False
        self._replied = False
        self._followup_id = None
        super().__init__(data, cmd)

    @property
    def permission_group(self):
        from MFramework.commands._utils import detect_group
        from MFramework import Groups

        if not self.is_dm:
            return detect_group(self.bot, self.user_id, self.guild_id, self.member.roles)
        return Groups.DM

    @property
    def is_dm(self):
        return not self.guild_id

    async def init(self):
        if self.data.guild_id:
            self.channel = await self.cache.channels[self.data.channel_id]

    async def get_dm(self, user_id: Snowflake = None):
        if not user_id or user_id == self.user_id:
            if not self.direct_message:
                dm = await self.bot.create_dm(self.user_id)
                self.direct_message = dm.id
            return self.direct_message
        dm = await self.bot.create_dm(user_id)
        return dm.id

    async def send_dm(
        self,
        content: str = None,
        embeds: list[Embed] = None,
        components: list[Component] = None,
        attachments: list[Attachment] = None,
        allowed_mentions: Allowed_Mentions = None,
        message_reference: Message_Reference = None,
        reply: bool = None,
    ) -> Message:
        return await self.send(
            content=content,
            embeds=embeds,
            components=components,
            attachments=attachments,
            allowed_mentions=allowed_mentions,
            message_reference=message_reference,
            reply=reply,
            channel_id=await self.get_dm(),
        )

    async def reply(
        self,
        content: str = None,
        embeds: list[Embed] = None,
        components: list[Component] = None,
        attachments: list[Attachment] = None,
        allowed_mentions: Allowed_Mentions = None,
        message_reference: Message_Reference = None,
        private: bool = None,
    ) -> Message:
        return (
            await self.data.reply(
                content=content,
                embeds=embeds,
                components=components,
                attachments=attachments,
                allowed_mentions=allowed_mentions,
                message_reference=message_reference,
                private=private,
            )
            or self.data
        )

    async def send(
        self,
        content: str = None,
        embeds: list[Embed] = None,
        components: list[Component] = None,
        attachments: list[Attachment] = None,
        allowed_mentions: Allowed_Mentions = None,
        message_reference: Message_Reference = None,
        reply: bool = None,
        private: bool = None,
        channel_id: Snowflake = None,
    ) -> Message:
        if private and self.is_message:
            channel_id = await self.get_dm()
        return (
            await self.data.send(
                content=content,
                embeds=embeds,
                components=components,
                attachments=attachments,
                allowed_mentions=allowed_mentions,
                message_reference=message_reference,
                reply=reply,
                private=private,
                channel_id=channel_id,
            )
            or self.data
        )

    async def edit(
        self,
        content: str = None,
        embeds: list[Embed] = None,
        components: list[Component] = None,
        attachments: list[Attachment] = None,
        allowed_mentions: Allowed_Mentions = None,
        flags: Message_Flags = None,
    ) -> Message:
        return (
            await self.data.edit(
                content=content,
                embeds=embeds,
                components=components,
                attachments=attachments,
                allowed_mentions=allowed_mentions,
                flags=flags,
            )
            or self.data
        )

    async def delete(self, message_id: Snowflake = None, reason: str = None) -> None:
        return await self.data.delete(message_id=message_id, reason=reason)

    async def deferred(self, private: bool = False) -> None:
        """Shows loading state when executed on Interaction or typing when executed on Message"""
        if self.is_message:
            return await self.data.typing(await self.get_dm() if private else None, private)
        return await self.data.deferred(private)

    async def get_messages(
        self,
        before_id: Snowflake = None,
        messages: list[Message] = [],
        limit: int = 100,
    ) -> list[Message]:
        """Eagerly retrieves messages from channel. Ordered by newest first"""
        r = await self.bot.get_channel_messages(self.channel_id, before=before_id, limit=min(limit, 100))
        if limit - len(r) < 1 or len(r) < min(limit, 100):
            return messages + r
        return await self.get_messages(r[-1].id, messages=messages + r, limit=limit - len(r))
