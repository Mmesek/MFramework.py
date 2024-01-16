from typing import Callable, List

from MFramework import Context, Embed, Guild_Member, Snowflake, User


class Leaderboard_Entry:
    """Helper class representing user and a corresponding value"""

    user_id: Snowflake
    _value: int

    def __init__(
        self,
        ctx: Context,
        user_id: Snowflake,
        value: int,
        value_processing: Callable = lambda x: x,
    ) -> None:
        self.ctx = ctx
        self.user_id = user_id
        self._value = value
        self._value_processing = value_processing

    def __str__(self) -> str:
        return f"`{self.name}` - {self.value}"

    @property
    def value(self) -> int:
        """Processed value of entry"""
        if self._value:
            return self._value_processing(self._value)
        value = None
        # TODO: attempt fetching from db here?
        return self._value_processing(value)

    @property
    def name(self) -> str:
        """Username corresponding to this user ID"""
        return self.ctx.cache.members.get(
            int(self.user_id), Guild_Member(user=User(username=self.user_id))
        ).user.username  # FIXME: .members is async

    @property
    def in_guild(self) -> bool:
        """Checks if user is still in guild's cache"""
        return self.user_id in self.ctx.cache.members  # FIXME: .members is async


class Leaderboard:
    """Builder sorting and formatting leaderboard"""

    user_id: Snowflake

    postion_str: str = "{position}. {value}"
    marked_str: str = "__{}__"
    _leaderboard: List[str] = []
    _iterable: List[Leaderboard_Entry] = []
    _user_stats: Leaderboard_Entry = None

    def __init__(
        self,
        ctx: Context,
        user_id: Snowflake,
        iterable: List[Leaderboard_Entry],
        limit: int = 10,
        error: str = "No results",
        skip_invalid: bool = False,
        reverse: bool = False,
    ) -> None:
        self.ctx = ctx
        self.user_id = user_id
        self._iterable = list(i for i in iterable if not skip_invalid or i.in_guild)
        self._user_stats = next(filter(lambda x: x.user_id == user_id, iterable), None)
        self._iterable.sort(key=lambda x: (x._value, x.name), reverse=not reverse)
        if self._user_stats:
            self._user_position = self._iterable.index(self._user_stats) + 1
        self._iterable = self._iterable[:limit]
        self.error_no_results = error
        self._user_found = False

    def __str__(self) -> str:
        return "\n".join(self.leaderboard)

    @property
    def leaderboard(self) -> List:
        """Sorted List of strings"""
        self._leaderboard = []
        for x, rank in enumerate(self._iterable, 1):
            r = self.postion_str.format(position=x, value=rank)
            if self.user_id == rank.user_id:
                self._user_found = True
                r = self.marked_str.format(r)
            self._leaderboard.append(r)
        if not self._leaderboard:
            self._leaderboard.append(self.error_no_results)
        return self._leaderboard

    @property
    def user_stats(self) -> int:
        """User leaderboard statistic"""
        return self._user_stats.value if self._user_stats else None

    def as_embed(
        self,
        title: str = "Leaderboard",
        add_user: bool = True,
        user_title: str = None,
        user_inline: bool = False,
    ) -> Embed:
        """Returns embed with leaderboard & optionally user stats"""
        e = Embed().setTitle(title).setDescription(self).setColor(self.ctx.cache.color)
        if add_user and self.user_stats and not self._user_found:
            if not user_title:
                user_title = (
                    "Your Stats"
                    if not self.user_id or self.ctx.user.id == self.user_id
                    else f"{self._user_stats.name}'s Stats"
                )
            e.addField(user_title, str(self.user_stats), user_inline)
        return e
