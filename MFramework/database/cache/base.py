import re
from datetime import timedelta

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

class Trigger:
    group: Groups
    name: str
    trigger: str
    content: str
    cooldown: timedelta

class RuntimeCommands(Commands):
    triggers: dict[str, Trigger]
    responses: dict[Groups, re.Pattern]

    async def initialize(self, **kwargs) -> None:
        await self.recompile_triggers()

    async def recompile_triggers(self, triggers: list[Trigger]):
        self.triggers = {t.name: t for t in triggers}
        self.responses = {}

        for group in [t.group for t in triggers]:
            self.responses[group] = re.compile(
                r"(?:{})".format(
                    "|".join(
                        "(?P<{}>{})".format(k, f) 
                        for k, f in 
                        {t.name: t.trigger for t in triggers}.items()
                    )
                ), re.IGNORECASE
            )
