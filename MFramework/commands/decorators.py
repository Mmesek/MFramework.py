from mlib.types import aInvalid
from MFramework import Interaction, Message, Snowflake

__all__ = ["Event", "EventBetween", "Cooldown", "Chance", "regex", "register"]

def Event(*, month=None, day=None, hour=None, minute=None, year=None):
    '''Executes command only if it's during provided timeframe'''
    def inner(f):
        def wrapped(*args, **kwargs):
            from datetime import datetime
            t = datetime.today()
            d = datetime(year or t.year, month or t.month, day or t.day, hour if hour is not None else t.hour, minute if minute is not None else t.minute)
            t = t.replace(second=0, microsecond=0)
            if t == d:
                return f(*args, **kwargs)
            return aInvalid()
        return wrapped
    return inner

def EventBetween(*, \
                after_month=None, after_day=None, after_hour=None, after_minute=None, after_year=None,\
                before_month=None, before_day=None, before_hour=None, before_minute=None, before_year=None):
    '''Executes only if it's between provided timeframes
    \nFor year parameters, specify how many years should be added/deduced'''
    def inner(f):
        def wrapped(*args, **kwargs):
            from datetime import datetime
            t = datetime.today()
            t = t.replace(second=0, microsecond=0)
            nonlocal after_year, before_year
            if after_year < 0:
                after_year = t.year + after_year
            if before_year:
                before_year = t.year + before_year
            after = datetime(after_year or t.year, after_month or t.month, after_day or t.day, after_hour if after_hour is not None else t.hour, after_minute if after_minute is not None else t.minute)
            before = datetime(before_year or t.year, before_month or t.month, before_day or t.day, before_hour if before_hour is not None else t.hour, before_minute if before_minute is not None else t.minute)
            if t >= after and t <= before:
                return f(*args, **kwargs)
            return aInvalid()
        return wrapped
    return inner

def Cooldown(*, seconds=None, minutes=None, hours=None, days=None, weeks=None, logic=lambda x: x):
    '''Applies a cooldown on command.
    Use it with callable function accepting interaction returning boolean for conditional execution and datetime object with last execution timestamp for cooldown calculation'''
    def inner(f):
        def wrapped(interaction: Interaction= None, *args, **kwargs):
            should_execute, last_execution = logic(interaction)
            if should_execute:
                from datetime import datetime, timedelta
                cooldown = timedelta(days=days, seconds=seconds, minutes=minutes, hours=hours, weeks=weeks)
                if (datetime.now() - last_execution) > cooldown:
                    return f(interaction=interaction, *args, **kwargs)
            return aInvalid()
        return wrapped
    return inner

def Chance(chance: float=0):
    '''Randomizes execution
    \nChance can be between 0 and 100'''
    def inner(f):
        def wrapped(*args, **kwargs):
            from random import SystemRandom
            if SystemRandom().random() < (chance / 100):
                return f(*args, **kwargs)
            return aInvalid()
        return wrapped
    return inner

COMPILED_REGEX = {}
def regex(expression: str):
    '''Checks for Regular Expression in Message's content'''
    def inner(f):
        import re
        COMPILED_REGEX[expression] = re.compile(expression)
        def wrapped(data: Message, *args, **kwargs):
            if COMPILED_REGEX[expression].search(data.content):
                return f(data=data, *args, **kwargs)
            return aInvalid()
        return wrapped
    return inner

from ._utils import Groups, commands, Command
def register(group: Groups = Groups.GLOBAL, interaction: bool = True, main=False, guild: Snowflake = None, choice: bool=None, **kwargs):
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
        whether this should be triggered depending on choice on main function'''
    def inner(f):
        _name = f.__name__.lower()
        _main  = main.__name__.lower() if main else None
        cmd = Command(f, interaction, main, group, guild)
        if main: #TODO: It doesn't support nesting!
            if not choice:
                commands[_main].add_subcommand(cmd)
            else:
                commands[_main].add_choice(_name, cmd)
        else:
            commands[_name] = cmd
        return f
    return inner
