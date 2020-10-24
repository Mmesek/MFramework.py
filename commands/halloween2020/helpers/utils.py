from MFramework.database import alchemy as db
from MFramework.utils.utils import parseMention
from datetime import datetime, timedelta, timezone

#from .constants import *
from .constants import MONSTERS, _HGROUPS, _HHELP
from MFramework.commands import register

def HalloweenEvent(cmd='', help='', alias='', race='None', group='Global', _f=None, **kwargs):
    def inner(f, *arg, **kwarg):
        if race not in _HGROUPS:
            _HGROUPS[race] = []
        _HGROUPS[race].append(f.__name__)
        if alias != '':
            cmds = [a for a in alias.split(',')]
        else:
            cmds = []
        if cmd != '':
            cmds.append(cmd)
        else:
            cmds.append(f.__name__)
        for g in cmds:
            if help != '':
                if race not in _HHELP:
                    _HHELP[race] = {}
                _HHELP[race][g.strip()] = help
        if cmd != '':
            f.__name__ = cmd
        register(alias=alias, group=group, **kwargs)(f)
        return f
    if _f is not None:
        return inner(_f)
    else:
        return inner

def Monsters(cmd='', help='', alias='', *args, **kwargs):
    def inner(f, *arg, **kwarg):
        HalloweenEvent(_f=f, race='Monsters', cmd=cmd, help=help, alias=alias, *args, **kwargs)
        return f
    return inner
def Hunters(cmd='', help='', alias='', *args, **kwargs):
    def inner(f, *arg, **kwarg):
        HalloweenEvent(_f=f, race='Hunters', cmd=cmd, help=help, alias=alias, *args, **kwargs)
        return f
    return inner
def Humans(cmd='', help='', alias='', *args, **kwargs):
    def inner(f,*arg, **kwarg):
        HalloweenEvent(_f=f, race='Humans', cmd=cmd, help=help, alias=alias, *args, **kwargs)
        return f
    return inner

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
