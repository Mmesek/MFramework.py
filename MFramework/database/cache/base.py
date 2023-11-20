import re

from MFramework import Snowflake
from MFramework.commands import Groups

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from MFramework import Bot

class Base:
    groups: dict[Groups, set[Snowflake]]

    def __init__(self, **kwargs) -> None:
        self.groups = {i: set() for i in Groups}

    def cached_roles(self, roles: list[Snowflake]) -> Groups:
        for group in self.groups:
            if any(i in roles for i in self.groups[group]):
                return group
        return Groups.GLOBAL


class Commands(Base):
    alias: re.Pattern

    _permissions_set: bool = False

    def __init__(self, *, bot: 'Bot', **kwargs) -> None:
        super().__init__(bot=bot, **kwargs)
        self.set_alias(bot)
    
    def set_alias(self, bot: 'Bot', alias: str = None):
        self.alias = re.compile(r"|".join([re.escape(alias or bot.alias), re.escape(bot.username), f"{bot.user_id}>"]))

