from typing import Dict, Any
from functools import wraps
from datetime import datetime, timedelta, timezone

from mdiscord import Snowflake

from MFramework import Context

cooldowns: Dict[str, Dict[Snowflake, datetime]] = {}

# Scope: Global | Group | Function - What's on cooldown
# Bucket: User | Guild | Channel | Role | Group - Who's on cooldown

class Cooldown:
    ctx: Context
    '''Command Context for cooldown calculation'''
    _type: str
    '''Type of this cooldown'''
    cooldown: timedelta
    '''Cooldown value'''

    def __init__(self, ctx: Context, _cooldown: timedelta, _cooldown_type: str, **kwargs) -> None:
        self.ctx: Context = ctx
        self._type = _cooldown_type
        self.cooldown = _cooldown
    
    @property
    def last_action(self) -> datetime:
        '''Returns time of last execution'''
        return cooldowns.get(self._type, {}).get(self.ctx.user.id, None)
    
    def add_cooldown(self) -> None:
        '''Saves last execution'''
        if not cooldowns.get(self._type):
            cooldowns[self._type] = {}
        cooldowns[self._type][self.ctx.user_id] = datetime.now(tz=timezone.utc)

    @property
    def elapsed(self) -> timedelta:
        '''Elapsed since last action'''
        return datetime.now(tz=timezone.utc) - self.last_action
        
    @property
    def remaining(self) -> timedelta:
        '''Remaining cooldown'''
        return self.cooldown - self.elapsed if self.last_action else timedelta()

    @property
    def on_cooldown(self) -> bool:
        '''Whether the cooldown is still active'''
        return self.remaining.total_seconds() > 0

class CacheCooldown(Cooldown):
    @property
    def last_action(self) -> datetime:
        return self.ctx.cache.cooldowns.get(self.ctx.user_id, None)
    
    def add_cooldown(self) -> None:
        return self.ctx.cache.cooldowns.store(self.ctx.guild_id, self.ctx.user_id, self._type, expire=self.cooldown)

class DatabaseCooldown(Cooldown):
    def __init__(self, ctx: Context, _cooldown: timedelta, _cooldown_type: str, table: Any, **kwargs) -> None:
        self.table = table
        super().__init__(ctx=ctx, _cooldown=_cooldown, _cooldown_type=_cooldown_type, **kwargs)
    @property
    def last_action(self) -> datetime:
        session = self.ctx.db.sql.session()
        r = session.query(self.table).filter(self.table.user_id == self.ctx.user_id, self.table.server_id == self.ctx.guild_id).first()
        return r.timestamp if r else None
    
    def add_cooldown(self) -> None:
        session = self.ctx.db.sql.session()
        r = session.query(self.table).filter(self.table.user_id == self.ctx.user_id, self.table.server_id == self.ctx.guild_id).first()
        if r:
            r.timestamp = datetime.now(tz=timezone.utc)
        else:
            session.add(self.table(user_id=self.ctx.user_id, server_id=self.ctx.guild_id))
        session.commit()

def cooldown(*, seconds: int=0, minutes: int=0, hours: int=0, days: int=0, weeks: int=0, logic: Cooldown=Cooldown, **cooldown_kwargs):
    '''Applies a cooldown on command.
    Use it with callable function accepting interaction returning boolean for conditional execution and datetime object with last execution timestamp for cooldown calculation'''
    def inner(f):
        @wraps(f)
        def wrapped(ctx: 'Context'= None, **kwargs):
            _cooldown = timedelta(days=days, seconds=seconds, minutes=minutes, hours=hours, weeks=weeks)
            c = logic(ctx=ctx, _cooldown=_cooldown, _cooldown_type=f.__name__, **cooldown_kwargs)
            if not c.on_cooldown:
                c.add_cooldown()
                return f(ctx=ctx, **kwargs)
            return c.remaining
        return wrapped
    return inner