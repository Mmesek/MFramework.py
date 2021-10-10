from typing import TYPE_CHECKING, Callable, List, Union
from functools import wraps

from mlib.types import aInvalid

from MFramework.commands._utils import Groups, commands, Command, aliasList, commands_regex, COMPILED_REGEX, command_shortcuts, reactions, ChanceError, EventInactive
from MFramework import Message, Snowflake

if TYPE_CHECKING:
    from MFramework.bot import Context

__all__ = ["Event", "EventBetween", "Cooldown", "Chance", "req_regex", "regex", "register", "shortcut", "any_role", "reaction"]

def Event(*, month: int=None, day: int=None, hour: int=None, minute: int=None, year: int=None):
    '''Executes command only if it's during provided timeframe'''
    def inner(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            from datetime import datetime
            t = datetime.today()
            try:
                d = datetime(year or t.year, month or t.month, day or t.day, hour if hour is not None else t.hour, minute if minute is not None else t.minute)
            except ValueError:
                return aInvalid()
            t = t.replace(second=0, microsecond=0)
            if t == d:
                return f(*args, **kwargs)
            return aInvalid()
        return wrapped
    return inner

def EventBetween(*, \
                after_month: int=None, after_day: int=None, after_hour: int=None, after_minute: int=None, after_year: int=None,\
                before_month: int=None, before_day: int=None, before_hour: int=None, before_minute: int=None, before_year: int=None):
    '''Executes only if it's between provided timeframes
    \nFor year parameters, specify how many years should be added/deduced'''
    def inner(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            from datetime import datetime
            t = datetime.today()
            t = t.replace(second=0, microsecond=0)
            nonlocal after_year, before_year
            if after_year and after_year < 0:
                after_year = t.year + after_year
            if before_year:
                before_year = t.year + before_year
            after = datetime(after_year or t.year, after_month or t.month, after_day or t.day, after_hour if after_hour is not None else t.hour, after_minute if after_minute is not None else t.minute)
            before = datetime(before_year or t.year, before_month or t.month, before_day or t.day, before_hour if before_hour is not None else t.hour, before_minute if before_minute is not None else t.minute)
            if t >= after and t <= before:
                return f(*args, **kwargs)
            raise EventInactive(f"This event is currently inactive! Check back between <t:{int(after.timestamp())}:D> and <t:{int(before.timestamp())}:D>!")
        return wrapped
    return inner

def Cooldown(*, seconds: int=None, minutes: int=None, hours: int=None, days: int=None, weeks: int=None, logic: Callable=lambda x: x):
    '''Applies a cooldown on command.
    Use it with callable function accepting interaction returning boolean for conditional execution and datetime object with last execution timestamp for cooldown calculation'''
    def inner(f):
        @wraps(f)
        def wrapped(ctx: 'Context'= None, *args, **kwargs):
            should_execute, last_execution = logic(ctx)
            if should_execute:
                from datetime import datetime, timedelta
                cooldown = timedelta(days=days, seconds=seconds, minutes=minutes, hours=hours, weeks=weeks)
                if (datetime.now() - last_execution) > cooldown:
                    return f(ctx=ctx, *args, **kwargs)
            return aInvalid()
        return wrapped
    return inner

def Chance(chance: float=0, fail_message: str=None):
    '''Randomizes execution
    \nChance can be between 0 and 100'''
    def inner(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            from random import SystemRandom
            if SystemRandom().random() < (chance / 100):
                return f(*args, **kwargs)
            if fail_message:
                raise ChanceError(fail_message)
            return aInvalid()
        return wrapped
    return inner

def req_regex(expression: str):
    '''Checks for Regular Expression in Message's content'''
    def inner(f):
        import re
        COMPILED_REGEX[expression] = re.compile(expression)
        @wraps(f)
        def wrapped(data: Message, *args, **kwargs):
            if COMPILED_REGEX[expression].search(data.content):
                return f(data=data, *args, **kwargs)
            return aInvalid()
        return wrapped
    return inner

def regex(expression: str, group: Groups = Groups.GLOBAL):
    '''Checks for Regular Expression in Message's content'''
    def inner(f):
        import re
        cmd = Command(f, False, None, group, None)
        commands_regex[re.compile(expression)] = cmd
        return f
    return inner

def shortcut(name:str, group: Groups = Groups.GLOBAL, **kwargs):
    '''Creates shortcut that prefils specified keywords with provided values'''
    def inner(f):
        cmd = Command(f, False, None, group, None)
        command_shortcuts[name] = (cmd, kwargs)
        return f
    return inner

def register(group: Groups = Groups.GLOBAL, interaction: bool = True, main=False, guild: Snowflake = None, choice: bool=None, aliases: List[str] = [], name: str = None, help: str = None, **kwargs):
    '''Decorator for creating commands.
    
    Params
    ------
    group:
        is a lowest group that can access this command (Highest digit). DM and Muted are special groups
    interaction:
        whether this function should be an interaction or not
    main:
        is a function pointer. 
    guild: 
        is used when command is exclusive to a specific guild
    choice:
        whether this should be triggered depending on choice on main function
    aliases:
        List of possible alias names
    name:
        Overwrites default name inferred from function name
    help:
        Overwrites default help string inferred from function's docstring'''
    def inner(f):
        if name:
            f.__name__ = name
        _name = f.__name__.strip('_')
        cmd = Command(f, interaction, main, group, guild, help=help)
        f._cmd = cmd
        for alias in aliases:
            aliasList[alias] = f"{main.__name__}.{_name}" if main else _name
        if main:
            if not hasattr(main, '_cmd'):
                return
            if not choice:
                main._cmd.add_subcommand(cmd)
            else:
                main._cmd.add_choice(_name, cmd)
        else:
            commands[_name] = cmd
        return f
    return inner


def any_role(*required: Union[Snowflake, str]):
    '''Checks if user has any provided role.

    Params
    ------
    required:
        Checks if provided role IDs or role names are present on calling user
    '''
    def inner(f):
        @wraps(f)
        def wrapped(ctx, *args, **kwargs):
            if ctx.member:
                nonlocal required
                if not all(issubclass(type(i), int) for i in required):
                    required = [i.id for i in ctx.cache.roles.values() if i.name in required or i.id in required]
                if len(set(required) & set(ctx.member.roles)):
                    return f(ctx, *args, **kwargs)
            return aInvalid()
        return wrapped
    return inner

def reaction(reaction: str, group: Groups = Groups.GLOBAL, guild: Snowflake = None):
    '''Makes command respond to reaction as a trigger

    Params
    ------
    reaction:
        Reaction which should trigger this function
    group:
        is a lowest group that can access this command (Highest digit). DM and Muted are special groups
    guild: 
        is used when command is exclusive to a specific guild
    '''
    def inner(f):
        cmd = Command(f, False, None, group, guild)
        reactions[reaction] = cmd
        return f
    return inner