import re
from dataclasses import dataclass
from datetime import timedelta
from typing import TYPE_CHECKING

from MFramework import Snowflake
from MFramework.commands import Groups

if TYPE_CHECKING:
    from MFramework import Bot


class BasicCache:
    _client: "Bot"

    def __init__(self, bot: "Bot", **kwargs) -> None:
        """Regular cache initialization"""
        self._client = bot

    async def initialize(self, **kwargs) -> None:
        """Async cache initialization (External cache, database, loading resources etc)"""
        pass


class Base(BasicCache):
    groups: dict[Groups, set[Snowflake]]
    """Mapping of Groups to set of role IDs"""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.groups = {i: set() for i in Groups}

    async def initialize(self, **kwargs) -> None:
        return

    def cached_roles(self, roles: list[Snowflake]) -> Groups:
        """
        Parameters
        ----------
        roles:
            List of role IDs

        Returns
        -------
        Highest group based on roles
        """
        for group in self.groups:
            if any(i in roles for i in self.groups[group]):
                return group
        return Groups.GLOBAL


class Commands(Base):
    alias: re.Pattern
    """Guild custom alias to use bot commands"""

    _permissions_set: bool = False
    """Determines whether interaction commands permissions were already set"""

    def __init__(self, *, bot: "Bot", **kwargs) -> None:
        super().__init__(bot=bot, **kwargs)
        self.set_alias(bot)

    def set_alias(self, bot: "Bot", alias: str = None) -> None:
        """Compiles regex for command alias based on string, name or mention

        Parameters
        ----------
        bot:
            Related bot's instance
        alias:
            New default guild alias
        """
        self.alias = re.compile(r"|".join([re.escape(alias or bot.alias), re.escape(bot.username), f"{bot.user_id}>"]))


@dataclass
class Trigger:
    """Datastructure to store trigger metadata"""

    group: Groups
    """Required group that can use this trigger"""
    name: str
    """(Unique) Name of this trigger"""
    trigger: str
    """Regular expression to be used to trigger this response"""
    content: str
    """Response code"""
    cooldown: timedelta
    """Determines how often can this trigger be used by user"""


class RuntimeCommands(BasicCache):
    triggers: dict[str, Trigger]
    """`Trigger`s objects look-up table"""
    responses: dict[Groups, re.Pattern]
    """Regular expression with compiled triggers"""

    def __init__(self, **kwargs):
        self.responses = {}
        super().__init__(**kwargs)

    def recompile_triggers(self, triggers: list[Trigger]) -> None:
        """Compiles list of known triggers for `commands.parser` commands

        Parameters
        ----------
        triggers:
            List of trigger objects to compile regex from
        """
        self.triggers = {t.name: t for t in triggers}
        self.responses = {}

        for group in [t.group for t in triggers]:
            self.responses[group] = re.compile(
                r"(?:{})".format(
                    "|".join(
                        "(?P<{}>{})".format(k, f)
                        for k, f in {t.name: t.trigger for t in triggers if t.group == group}.items()
                    )
                ),
                re.IGNORECASE,
            )
