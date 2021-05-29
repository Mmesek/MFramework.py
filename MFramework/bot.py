from mdiscord import *

from .database.database import Database
from .database.cache import Cache
from typing import Dict

class Bot(Client):
    session_id: str = None
    start_time: float = None
    application: Application = None
    registered_commands = None
    registered: bool = False

    alias: str = "?"
    emoji: dict = dict
    primary_guild: Snowflake = 463433273620824104

    db: Database
    cache: Dict[Snowflake, Cache]
    def __init__(self, name: str, cfg: dict, db: Database=None, cache: Cache=None, shard: int=0, total_shards: int=1):
        self.db = db
        self.cache = cache
        self.alias = cfg[name].get('alias', '?')
        self.emoji = cfg["Emoji"]
        self.primary_guild = cfg[name].get('primary_guild', 463433273620824104)

        super().__init__(name, cfg, shard=shard, total_shards=total_shards)
    async def dispatch(self, data: Gateway_Payload):
        await super().dispatch(data)
        if hasattr(data.d, 'guild_id') or isinstance(data.d, Guild):
            id = data.d.guild_id if hasattr(data.d, 'guild_id') else data.d.id
            if id and id in self.cache:
                await self.cache[id].logging[data.t.lower()](data.d)

from typing import Union
from MFramework.database.cache import GuildCache
class Context:
    '''This is meant as an unified context object used for universal 
    commands that can be issued as both a message or an interaction'''
    cache: GuildCache = GuildCache
    db: Database
    bot: Bot = Bot
    data: Union[Message, Interaction]
    
    guild_id: Snowflake
    guild: Guild
    channel_id: Snowflake
    channel: Channel
    message_id: Snowflake
    user_id: Snowflake
    user: User
    member: Guild_Member
    language: str

    def __init__(self, cache: Cache, bot: Bot, data: Union[Message, Interaction]):
        self.cache = cache[data.guild_id]
        self.bot = bot
        self.db = bot.db
        self.data = data
        self.guild_id = data.guild_id
        self.guild = self.cache.guild
        self.channel_id = data.channel_id
        self.channel = self.cache.channels[data.channel_id]
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
            self.member = data.member
            self.is_interaction = False
            self.is_message = True
        self.language = self.cache.language
        self.direct_message = cache[0].get(self.user_id, None)
        self.webhook = None

    @property
    def permission_group(self):
        from MFramework.commands._utils import Groups
        if not self.is_dm:
            if self.user_id != 273499695186444289:
                return self.cache.cachedRoles(self.member.roles)
            return Groups.SYSTEM
        return Groups.DM

    @property
    def is_dm(self):
        return not self.guild_id
    async def send(self, content: str=None, embeds: List[Embed]=None, *, file: bytes = None, filename: str="file.txt", allowed_mentions: Allowed_Mentions = Allowed_Mentions(parse=[]), reply=True, private=False, webhook=False, username=None, avatar_url=None) -> Union[Message, None]:
        if not private and webhook:
            return await self.bot.execute_webhook(self.webhook_id, self.webhook_token, content=content, embeds=embeds, username=username, avatar_url=avatar_url, allowed_mentions=allowed_mentions)
        if self.is_interaction:
            if not private:
                return await self.data.send(content, embeds, allowed_mentions=allowed_mentions)
            return await self.data.respond_private(content, embeds)
        if not private:
            if reply:
                return await self.data.reply(content, embeds[0], file, filename, allowed_mentions=allowed_mentions)
            return await self.data.send(content, embeds[0], file, filename, allowed_mentions)
        if not self.direct_message:
            dm = await self.bot.create_dm(self.user_id)
            self.direct_message = dm.id
        return await self.bot.create_message(channel_id=self.direct_message, content=content, embed=embeds[0], file=file, filename=filename, allowed_mentions=allowed_mentions)
    async def edit(self, content: str=None, embeds: List[Embed]=None, message_id=None, channel_id=None, allowed_mentions: Allowed_Mentions = Allowed_Mentions(parse=[])):
        if self.is_interaction:
            return await self.data.edit_response(content, embeds, allowed_mentions)
        return await self.bot.edit_message(channel_id or self.channel_id, message_id, content, embeds[0], allowed_mentions=allowed_mentions)
    