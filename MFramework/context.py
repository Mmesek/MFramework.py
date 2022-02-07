from typing import TYPE_CHECKING, Union, List

from mdiscord import Snowflake, Guild, Channel, Message, Interaction, User, Guild_Member, Sendable, Embed, Component, Allowed_Mentions, Message_Reference, Message_Flags, Attachment

from MFramework.database.cache import Cache
from MFramework.database.database import Database
if TYPE_CHECKING:
    from MFramework.bot import Bot

class Context(Sendable):
    '''This is meant as an unified context object used for universal 
    commands that can be issued as both a message or an interaction'''
    cache: Cache = Cache
    db: Database
    bot: 'Bot'
    data: Union[Message, Interaction]
    
    guild_id: Snowflake
    guild: Guild
    channel_id: Snowflake
    channel: Channel
    message_id: Snowflake
    user_id: Snowflake
    user: User
    member: Guild_Member

    direct_message: Snowflake
    language: str

    is_message: bool
    is_interaction: bool

    def __init__(self, cache: Cache, bot: 'Bot', data: Union[Message, Interaction]):
        self.cache = cache[data.guild_id]
        self.bot = bot
        self.db = bot.db
        self.data = data
        self.guild_id = data.guild_id
        if data.guild_id:
            self.guild = self.cache.guild
            self.channel = self.cache.channels[data.channel_id]
            self.language = self.cache.language
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
            self.member = data.member or cache.members.get(data.user_id, None) or Guild_Member()
            self.member.user = data.author
            self.is_interaction = False
            self.is_message = True
        self.direct_message = cache[0].get(self.user_id, None)
        self.webhook = None
        self._deferred = False
        self._replied = False
        self._followup_id = None

    @property
    def permission_group(self):
        from MFramework.commands._utils import Groups
        if not self.is_dm:
            if self.user_id != 273499695186444289:
                if self.user_id != self.cache.guild.owner_id:
                    return self.cache.cachedRoles(self.member.roles)
                return Groups.OWNER
            return Groups.SYSTEM
        return Groups.DM

    @property
    def is_dm(self):
        return not self.guild_id
    
    async def get_dm(self, user_id: Snowflake = None):
        if not user_id or user_id == self.user_id:
            if not self.direct_message:
                dm = await self.bot.create_dm(self.user_id)
                self.direct_message = dm.id
            return self.direct_message
        dm = await self.bot.create_dm(user_id)
        return dm.id
    
    async def send_dm(self, content: str=None, embeds: List[Embed]=None, components: List[Component]=None, file: bytes=None, filename: str=None, allowed_mentions: Allowed_Mentions=None, message_reference: Message_Reference=None, reply: bool=None) -> Message:
        return await self.send(content=content, embeds=embeds, components=components, file=file, filename=filename, allowed_mentions=allowed_mentions, message_reference=message_reference, reply=reply, channel_id=await self.get_dm())

    async def reply(self, content: str=None, embeds: List[Embed]=None, components: List[Component]=None, file: bytes=None, filename: str=None, allowed_mentions: Allowed_Mentions=None, message_reference: Message_Reference=None, private: bool=None) -> Message:
        return await self.data.reply(content=content, embeds=embeds, components=components, file=file, filename=filename, allowed_mentions=allowed_mentions, message_reference=message_reference, private=private) or self.data

    async def send(self, content: str=None, embeds: List[Embed]=None, components: List[Component]=None, file: bytes=None, filename: str=None, allowed_mentions: Allowed_Mentions=None, message_reference: Message_Reference=None, reply: bool=None, private: bool=None, channel_id: Snowflake =None) -> Message:
        if private and self.is_message:
            channel_id = await self.get_dm()
        return await self.data.send(content=content, embeds=embeds, components=components, file=file, filename=filename, allowed_mentions=allowed_mentions, message_reference=message_reference, reply=reply, private=private, channel_id=channel_id) or self.data

    async def edit(self, content: str=None, embeds: List[Embed]=None, components: List[Component]=None, attachments: List[Attachment]=None, file: bytes=None, filename: str=None, allowed_mentions: Allowed_Mentions=None, flags: Message_Flags=None) -> Message:
        return await self.data.edit(content=content, embeds=embeds, components=components, attachments=attachments, file=file, filename=filename, allowed_mentions=allowed_mentions, flags=flags) or self.data

    async def delete(self, message_id: Snowflake=None, reason: str = None) -> None:
        return await self.data.delete(message_id=message_id, reason=reason)

    async def deferred(self, private: bool=False) -> None:
        '''Shows loading state when executed on Interaction or typing when executed on Message'''
        if self.is_message:
            return await self.data.typing(await self.get_dm() if private else None, private)
        return await self.data.deferred(private)
