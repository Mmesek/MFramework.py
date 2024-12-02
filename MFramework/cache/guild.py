from typing import Optional, TYPE_CHECKING, DefaultDict
from collections import defaultdict

from mlib.types import aInvalid
from mlib.utils import all_subclasses

from MFramework import Guild, Guild_Member, Snowflake, Role
from MFramework.commands import Groups
from MFramework.utils.log import Log

from ._internal import models as collections
from .base import BasicCache, Base

if TYPE_CHECKING:
    from MFramework import Bot

default_roles = {
    "admin": Groups.ADMIN,
    "administrator": Groups.ADMIN,
    "mod": Groups.MODERATOR,
    "moderator": Groups.MODERATOR,
    "nitro booster": Groups.NITRO,
    "muted": Groups.MUTED,
    "vip": Groups.VIP,
    "contributor": Groups.VIP,
    "limbo": Groups.LIMBO,
}


class GuildCache(BasicCache):
    guild_id: Snowflake
    """Guild ID this cache is related to"""
    guild: Guild
    """Guild object"""

    def __init__(self, *, guild: Guild, **kwargs) -> None:
        self.guild_id = guild.id
        self.guild = guild
        super().__init__(guild=guild, **kwargs)


class ObjectCollections(Base):
    messages: collections.Messages = collections.Messages()
    """Mapping of IDs to Message objects"""
    channels: collections.Channels = collections.Channels()
    """Mapping of IDs to Channel objects"""
    roles: collections.Roles = collections.Roles()
    """Mapping of IDs to Role objects"""
    members: collections.Members = collections.Members()
    """Mapping of User IDs to Guild Member objects"""
    presence: collections.Presences = collections.Presences()
    """Mapping of User IDs to last presence's updates"""
    kv: collections.KeyValue = collections.KeyValue()
    """Custom Key-Value store"""

    def __init__(self, *, bot: "Bot", guild: Guild, rds: Optional[collections.Redis] = None, **kwargs) -> None:
        if not rds:
            _redis = bot.cfg.get("redis", {})
            if host := _redis.get("host", None):
                rds = collections.Redis(
                    host=host,
                    password=_redis.get("password", None),
                    port=_redis.get("port", 6379),
                    db=_redis.get("_db", 0),
                )
            else:
                rds = collections.Dictionary()
        self.members = collections.Members()
        self.presence = collections.Presences()
        self.roles = collections.Roles()
        self.channels = collections.Channels()

        self.messages = collections.Messages(rds)
        self.cooldowns = collections.Cooldowns(rds)
        self.kv = collections.KeyValue(rds, guild.id)
        super().__init__(guild=guild, bot=bot, rds=rds, **kwargs)

    async def initialize(self, *, guild: Guild, **kwargs) -> None:
        await self.members.from_list(guild.members)
        await self.roles.from_list(guild.roles)
        await self.channels.from_list(guild.channels, guild_id=guild.id)
        self.set_role_groups(self.roles)
        await super().initialize(guild=guild, **kwargs)

    def set_role_groups(self, roles: dict[Snowflake, Role]) -> None:
        """Associates default `Groups` roles based on `default_roles` mapping

        Parameters
        ----------
        roles:
            Mapping of ID to roles to check"""
        for id, role in roles.items():
            if _group := default_roles.get(role.name.lower(), None):
                self.groups[_group].add(id)


class BotMeta(ObjectCollections):
    bot: Guild_Member
    """Bot's Guild Member object"""
    name: str = "Uninitialized"
    """Bot's name in guild"""
    color: int = None
    """Bot's top color in guild"""
    permissions: int = 0
    """Current bot permissions within guild"""

    async def initialize(self, *, bot: "Bot", guild: Guild, **kwargs) -> None:
        await super().initialize(bot=bot, guild=guild, **kwargs)

        self.bot: Guild_Member = await self.members[bot.user_id]
        if self.bot:
            self.name = self.bot.nick or self.bot.user.username
            self.color = await self.get_top_color(self.bot.roles)
            self.permissions = await self.calculate_permissions(self.bot.roles)

    async def get_top_color(self, roles: list[Snowflake]) -> int:
        """Calculates top color based on provided roles

        Parameters
        ----------
        roles:
            List of role IDs
        """
        color: tuple[int, int, bool] = [0, 0, False]
        for role_id in roles:
            role = await self.roles[role_id]
            if role.managed and role.color:
                color = (role.position, role.color, True)
                break
            elif color is None:
                color = (role.position, role.color, False)
            elif role.position > color[0]:
                color = (role.position, role.color, False)
        return color[1] if color else None

    async def calculate_permissions(self, roles: list[Snowflake]) -> int:
        """Calculates permissions based on provided roles

        Parameters
        ----------
        roles:
            List of role IDs
        """
        permissions = 0
        for role in roles:
            permissions |= int((await self.roles[role]).permissions)
        return permissions


class Permissions(BotMeta):
    async def user_roles(self, user_id: Snowflake) -> list[int]:
        member = await self.members.get(user_id)
        return member.roles

    async def user_permissions(self, user_id: Snowflake):
        raise NotImplementedError


class Logging(GuildCache, BotMeta):
    logging: DefaultDict[str, Log]
    """Mapping of logger name to Log objects"""
    webhooks: dict[str, tuple[Snowflake, str]] = {}
    """Mapping of webhook name to Webhook ID & Token"""

    async def initialize(self, bot: "Bot", guild: Guild, **kwargs) -> None:
        self.webhooks = {}  # TODO
        self.logging = defaultdict(lambda: aInvalid)
        await super().initialize(bot=bot, guild=guild, **kwargs)
        await self.set_loggers()

    async def set_loggers(self) -> None:
        """Maps loggers inheriting from `Log` to Webhooks that shares name & instantiates each"""
        self.logging = defaultdict(lambda: aInvalid)
        _classes = {i.__name__.lower(): i for i in all_subclasses(Log)}
        for webhook in filter(lambda x: x in _classes, self.webhooks):
            self.logging[webhook] = _classes[webhook](self.bot, self.guild_id, webhook, *self.webhooks[webhook])
