from datetime import datetime, timedelta, timezone
from functools import wraps
from typing import Any, Dict

from mdiscord import Snowflake

from MFramework import Context

cooldowns: Dict[str, Dict[Snowflake, datetime]] = {}

from enum import Enum

from MFramework import Groups


class Bucket(Enum):
    USER: Snowflake = "user_id"
    GUILD: Snowflake = "guild_id"
    CHANNEL: Snowflake = "channel_id"
    ROLE: Snowflake = "roles"
    GROUP: Groups = "permission_group"


# Scope: Global | Group | [Function] - What's on cooldown
# Bucket: [User] | Guild | Channel | Role | Group - Who's on cooldown


class Cooldown:
    """Base cooldown calculation class"""

    ctx: Context
    """Command Context for cooldown calculation"""
    _type: str
    """Type of this cooldown"""
    _bucket: Bucket = Bucket.USER
    """Bucket for this cooldown"""

    def __init__(self, ctx: Context, cooldown: timedelta, cooldown_type: str, bucket: Bucket = None, **kwargs) -> None:
        """
        _cooldown:
            Delta of a cooldown
        _cooldown_type:
            Name of this cooldown"""
        self.ctx: Context = ctx
        self._type = cooldown_type
        self._cooldown = cooldown
        self._bucket = bucket

    @property
    def cooldown(self) -> timedelta:
        """Cooldown value"""
        return self._cooldown

    @property
    def now(self):
        return datetime.now(tz=timezone.utc)

    def _get_cooldown(self) -> Any:
        return cooldowns.get(self._type, {}).get(self.bucket, None)

    @property
    def last_action(self) -> datetime:
        """Returns time of last execution"""
        return self._get_cooldown()

    @property
    def bucket(self) -> Snowflake:
        """Returns ID of bucket cooldown should be applied to"""
        return getattr(self.ctx, self._bucket.value)

    def add_cooldown(self, value=None) -> None:
        """Saves last execution"""
        if not cooldowns.get(self._type):
            cooldowns[self._type] = {}
        cooldowns[self._type][self.bucket] = value or self.now

    @property
    def elapsed(self) -> timedelta:
        """Elapsed since last action"""
        return datetime.now(tz=timezone.utc) - self.last_action

    @property
    def remaining(self) -> timedelta:
        """Remaining cooldown"""
        return self.cooldown - self.elapsed if self.last_action else timedelta()

    @property
    def on_cooldown(self) -> bool:
        """Whether the cooldown is still active"""
        return self.remaining.total_seconds() > 0


class CacheCooldown(Cooldown):
    """Cooldown stored (and manages) in remote cache like Redis"""

    @property
    def last_action(self) -> datetime:
        return self.ctx.cache.cooldowns.get(self.ctx.guild_id, self.ctx.user_id, self._type)

    def add_cooldown(self) -> None:
        return self.ctx.cache.cooldowns.store(self.ctx.guild_id, self.ctx.user_id, self._type, expire=self.cooldown)


class DatabaseCooldown(Cooldown):
    """Cooldown timestamp stored in a database table"""

    def __init__(self, ctx: Context, cooldown: timedelta, cooldown_type: str, table: Any, **kwargs) -> None:
        self.table = table
        super().__init__(ctx=ctx, cooldown=cooldown, cooldown_type=cooldown_type, **kwargs)

    @property
    def last_action(self) -> datetime:
        session = self.ctx.db.sql.session()
        r = (
            session.query(self.table)
            .filter(
                self.table.user_id == self.ctx.user_id,
                self.table.server_id == self.ctx.guild_id,
            )
            .first()
        )
        return r.timestamp if r else None

    def add_cooldown(self) -> None:
        session = self.ctx.db.sql.session()
        r = (
            session.query(self.table)
            .filter(
                self.table.user_id == self.ctx.user_id,
                self.table.server_id == self.ctx.guild_id,
            )
            .first()
        )
        if r:
            r.timestamp = datetime.now(tz=timezone.utc)
        else:
            session.add(self.table(user_id=self.ctx.user_id, server_id=self.ctx.guild_id))
        session.commit()


class Tokens(Cooldown):
    """Simple Tokens counter before applying cooldown"""

    def __init__(self, ctx: Context, capacity: int, cooldown: timedelta, cooldown_type: str, **kwargs) -> None:
        self.capacity: int = capacity
        self._count = 0
        super().__init__(ctx, cooldown, cooldown_type, **kwargs)
        v = self._get_cooldown()
        self._last_action = v[0]
        self._count = v[1]

    def _get_cooldown(self) -> Any:
        return super()._get_cooldown() or (None, 0)

    @property
    def last_action(self) -> datetime:
        return self._last_action

    def add_cooldown(self, value=None) -> None:
        return super().add_cooldown(value=(self._count, self.now()))

    @property
    def on_cooldown(self) -> bool:
        if not super().on_cooldown:
            # Restart window
            self._count = self.capacity

        if not self._count:
            # No more free tokens, cooldown
            return True

        # No cooldown, decrease remaining tokens
        self._count -= 1
        return False


class SlidingWindow(Tokens):
    """Remaining Tokens affected by usage during cooldown's previous window"""

    @property
    def on_cooldown(self) -> bool:
        if not super(Tokens).on_cooldown:
            # Restart window
            self._previous = self._count
            self._count = 0

        t = self.remaining / self.cooldown
        est = self._previous * t + self._count

        if est > self.capacity:
            # Usage within this and previous window suggest *probably* depleted tokens and therefore Cooldown
            return True

        # No cooldown, usage counter increased
        self._count += 1
        return False


def cooldown(
    rate: int = 1,
    bucket: Bucket = Bucket.USER,
    scope: str = None,
    *,
    seconds: int = 0,
    minutes: int = 0,
    hours: int = 0,
    days: int = 0,
    weeks: int = 0,
    logic: Cooldown = Cooldown,
    delta: timedelta = None,
    **cooldown_kwargs,
):
    """Applies a cooldown on command.

    Parameters
    ----------
    rate:
        After how many uses cooldown should be applied
    bucket:
        Group which cooldown is applied to (User, Guild, Channel, Role, Group). Default: User
    scope:
        Group of cooldowns (Global, Functions, Function). Default: Function
    logic:
        Backend class which handles Cooldown calculation on command invocation
    delta:
        Delta to be used as a cooldown value
    cooldown_kwargs:
        Keyword arguments that should be passed to Cooldown (logic) class
    Use it with callable function accepting interaction returning boolean for conditional execution and datetime object with last execution timestamp for cooldown calculation"""

    def inner(f):
        @wraps(f)
        def wrapped(ctx: "Context" = None, **kwargs):
            _cooldown = delta or timedelta(days=days, seconds=seconds, minutes=minutes, hours=hours, weeks=weeks)
            c = logic(
                ctx=ctx,
                cooldown=_cooldown,
                cooldown_type=scope or f.__name__,
                func_args=kwargs,
                bucket=bucket,
                capacity=rate,
                **cooldown_kwargs,
            )
            if not c.on_cooldown:
                c.add_cooldown()
                return f(ctx=ctx, **kwargs)
            from .exceptions import CooldownError

            raise CooldownError(int((c.now + c.remaining).timestamp()))

        return wrapped

    return inner
