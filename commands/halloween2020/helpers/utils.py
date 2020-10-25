from MFramework.database import alchemy as db
from MFramework.utils.utils import parseMention, tr
from datetime import datetime, timedelta, timezone

#from .constants import *
from .constants import MONSTERS, HUNTERS, _HHELP
from MFramework.commands import register
from inspect import signature
def HalloweenEvent(cmd='', help='', alias='', race='None', group='Global', hijak=None, **kwargs):
    def inner(f, *arg, **kwarg):
        nonlocal cmd, help, alias, race, group
        if race not in _HHELP:
            _HHELP[race] = {}
        if cmd == '':
            cmd = f.__name__
        else:
            f.__name__ = cmd
        _HHELP[race][cmd] = {}

        sig = signature(f)
        s = str(sig).replace('(', '').replace('self, ', '').replace('*args', '').replace(')', '').replace('**kwargs', '').replace('*','\*').replace('group','').replace('_','\_').replace('language','').replace('cmd','')
        si = s.split('data, ')
        sig = si[0].split(', ')
        sig = [f'[{a}]' if '=' not in a else f"({a})" if a.split('=', 1)[1] not in ['0', "''", 'None', 'False'] else f"({a.split('=',1)[0]})" for a in sig if a != '']
        s = si[1].split(', ')
        sig += [f"(-{i.split('=')[0]})" if '=False' in i else f"(--{i.split('=')[0]})" if '=' in i else f'[@{i}]' for i in s if i != '']
        _HHELP[race][cmd]['sig'] = ' '.join(sig)
        _HHELP[race][cmd]['alias'] = alias
        _HHELP[race][cmd]['msg'] = help

        register(alias=alias, group=group, hijak=hijak, hijak_coroutine=True, **kwargs)(f)
        return f
    return inner

def Monsters(cmd='', help='', alias='', *args, **kwargs):
    def inner(f, *arg, **kwarg):
        HalloweenEvent(race='Monsters', cmd=cmd, help=help, alias=alias, *args, hijak=check_monster, **kwargs)(f)
        return f
    return inner
def Hunters(cmd='', help='', alias='', *args, **kwargs):
    def inner(f, *arg, **kwarg):
        HalloweenEvent(race='Hunters', cmd=cmd, help=help, alias=alias, *args, hijak=check_hunter, **kwargs)(f)
        return f
    return inner
def Humans(cmd='', help='', alias='', *args, **kwargs):
    def inner(f,*arg, **kwarg):
        HalloweenEvent(race='Humans', cmd=cmd, help=help, alias=alias, *args, hijak=check_human, **kwargs)(f)
        return f
    return inner

def check_hunter(self, f, *args, data, **kwargs):
    if generic_check(self, data, HUNTERS):
        return f(self, *args, data=data, **kwargs)

def check_monster(self, f, *args, data, **kwargs):
    if generic_check(self, data, MONSTERS):
        return f(self, *args, data=data, **kwargs)

def check_human(self, f, *args, data, **kwargs):
    if generic_check(self, data, ["Human"]):
        return f(self, *args, data=data, **kwargs)

def generic_check(self, data, classes):
    s = self.db.sql.session()
    self_user = get_user(data.guild_id, data.author.id, s)
    if self_user is None or self_user.CurrentClass not in classes:
        return False
    return True

def get_user(guild_id: int, user_id: int, s) -> db.HalloweenClasses:
    return s.query(db.HalloweenClasses).filter(db.HalloweenClasses.GuildID == guild_id, db.HalloweenClasses.UserID == user_id).first()

def get_roles(guild_id: int, s) -> dict:
    roles = s.query(db.HalloweenRoles).filter(db.HalloweenRoles.GuildID == guild_id).all()
    return {i.RoleName: i.RoleID for i in roles}

def get_user_and_roles(guild_id, user_id, s) -> tuple:
    user = get_user(guild_id, user_id, s)
    roles = get_roles(guild_id, s)
    return user, roles

def get_elapsed(user: db.HalloweenClasses) -> timedelta:
    try:
        return datetime.now(tz=timezone.utc) - user.LastAction
    except:
        return timedelta(seconds=0)

def get_action_cooldown_left(user: db.HalloweenClasses) -> timedelta:
    try:
        return user.ActionCooldownEnd - datetime.now(tz=timezone.utc)
    except:
        return timedelta(seconds=0)

def is_top_faction(others, _current_race):
    if others // 2 < _current_race:
        return True
    return False

def get_difference(_current_race, others):
    return _current_race - others // 2

def cooldown_var(others, _current_race):
    difference = get_difference(_current_race, others)
    if not is_top_faction(others, _current_race):
        difference = difference * 2
    return timedelta(minutes=difference * 3)

def calc_cooldown_var(s, data, self_user):
    others, _current_race, _current_target = get_race_counts(s, data, self_user, self_user)
    return cooldown_var(others, _current_race)


def get_user_id(user) -> int:
    return int(parseMention(user[0]))

def get_current_time() -> datetime.now:
    return datetime.now(tz=timezone.utc)

def get_total(self, data, total):
    totalPopulation = {}
    totalBites = 0
    for v in total:
        if v.CurrentClass not in totalPopulation:
            totalPopulation[v.CurrentClass] = 0
        totalPopulation[v.CurrentClass] += 1
        if v.TurnCount > 0:
            totalBites += v.TurnCount
    return totalBites, totalPopulation

def get_race_counts(s, data, self_user, target_user):
    users = s.query(db.HalloweenClasses.CurrentClass).filter(db.HalloweenClasses.GuildID == data.guild_id).all()
    others = 0
    _current_race = 0
    _current_target = 0
    for i in users:
        if i.CurrentClass == self_user.CurrentClass:
            _current_race += 1
        elif i.CurrentClass in MONSTERS:
            others += 1
        elif i.CurrentClass != "Human" and i.CurrentClass == target_user.CurrentClass:
            _current_target += 1
    return others, _current_race, _current_target

async def get_usernames(self, guild_id: int, user_id: int) -> str:
    try:
        u = self.cache[guild_id].members[user_id].user.username
    except:
        try:
            u = await self.get_guild_member(guild_id, user_id)
        except:
            return None
        self.cache[guild_id].members[user_id] = u
        u = u.user.username
    return u

async def add_and_log(self, data, target, s, previousClass, self_user, timestamp):
    s.merge(target)
    s.add(db.HalloweenLog(data.guild_id, target.UserID, previousClass, target.CurrentClass, self_user.UserID, timestamp))
    s.commit()
    roles = get_roles(data.guild_id, s)
    if roles != {}:
        role_id = roles.get(previousClass, "")
        await self.remove_guild_member_role(data.guild_id, target.UserID, role_id, "Halloween Minigame")
        role_id = roles.get(target.CurrentClass, "")
        await self.add_guild_member_role(data.guild_id, target.UserID, role_id, "Halloween Minigame")

def _t(key, language='en', **kwargs):
    return tr("events.halloween."+key, language, **kwargs)