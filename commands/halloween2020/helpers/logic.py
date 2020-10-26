from MFramework.database import alchemy as db

from datetime import datetime, timedelta, timezone
from random import SystemRandom

from .utils import *
from .constants import *
from .logic import *

async def turning_logic(self, data, target, side, _hunters=False, action_cooldown=timedelta(hours=3), skip_cooldown=False, to_same_class=True):
    s = self.db.sql.session()
    self_user = get_user(data.guild_id, data.author.id, s)
    if self_user is None:
        return None #"User doesn't have a class"
    if self_user.CurrentClass not in side:
        return Responses.CANT #"User is not a monster or a hunter"

    try:
        target = get_user_id(target)
    except:
        return Responses.OTHER #"Target is either not specified or wrongly specified"

    target_user = s.query(db.HalloweenClasses).filter(db.HalloweenClasses.GuildID == data.guild_id, db.HalloweenClasses.UserID == target).first()
    if target_user is None:
        target_user = db.HalloweenClasses(data.guild_id, target, "Human")
    elif target_user.CurrentClass in side:
        return Responses.IMMUNE #"Target is on the same side"

    failed = False
    cooldown = get_elapsed(self_user)
    if not _hunters:
        others, _current_race, _current_target = get_race_counts(s, data, self_user, target_user)
        if _current_target == 1:
            return Responses.FAILED #"Failed to bite"
        elif is_top_faction(others, _current_race):
            roll = SystemRandom().randint(0, 75)
            if roll < get_difference(_current_race, others):
                failed = True
        cooldown += cooldown_var(others, _current_race)

    if self_user.LastAction != None:
        if not skip_cooldown and cooldown < action_cooldown:
            return Responses.COOLDOWN, cooldown #"Cooldown not ready"

    if _hunters and IMMUNE_TABLE.get(target_user.CurrentClass) != self_user.CurrentClass:
        return Responses.IMMUNE  #"Target is immune"
    elif _hunters is False and IMMUNE_TABLE.get(target_user.CurrentClass, '') == self_user.CurrentClass:
        return Responses.ERROR, self_user.CurrentClass

    timestamp = datetime.now(tz=timezone.utc)
    if not skip_cooldown:
        self_user.LastAction = timestamp
        s.commit()
    if target_user.ProtectionEnds is not None and target_user.ProtectionEnds > timestamp:
        return Responses.PROTECTED #"Target is protected"

    if failed:
        return Responses.FAILED #"Failed to bite"

    previousClass = target_user.CurrentClass
    target_user.CurrentClass = self_user.CurrentClass if to_same_class else "Human"
    target_user.LastUser = self_user.UserID
    target_user.TurnCount += 1

    self_user.LastVictim = target_user.UserID
    if self_user.CurrentClass == 'Vampire':
        self_user.VampireStats += 1
    elif self_user.CurrentClass == 'Werewolf':
        self_user.WerewolfStats += 1
    elif self_user.CurrentClass == 'Zombie':
        self_user.ZombieStats += 1
    elif self_user.CurrentClass == 'Vampire Hunter':
        self_user.VampireHunterStats += 1
    elif self_user.CurrentClass == 'Huntsman':
        self_user.HuntsmanStats += 1
    elif self_user.CurrentClass == 'Zombie Slayer':
        self_user.ZombieSlayerStats += 1
    s.commit()

    await add_and_log(self, data, target_user, s, previousClass, self_user, timestamp)
    return Responses.SUCCESS, (target, previousClass, target_user.CurrentClass) #"Target Bitten successfuly"

async def join_logic(self, data, _class, classes, first_only=False):
    s = self.db.sql.session()
    self_user = get_user(data.guild_id, data.author.id, s)
    if first_only and self_user is not None and _class != 'random':
        return Responses.FAILED #"This action is only for first timers"
    elif _class == ():
        return Responses.AVAILABLE
    _class = ' '.join(_class).title() if type(_class) is tuple else _class.title()

    if self_user is None:
        self_user = db.HalloweenClasses(data.guild_id, data.author.id)
    elif self_user.CurrentClass != "Human":
        users = s.query(db.HalloweenClasses.CurrentClass).filter(db.HalloweenClasses.GuildID == data.guild_id, db.HalloweenClasses.CurrentClass == _class).all()
        if users != []:
            return Responses.CANT #"Not a human"

    previousClass = self_user.CurrentClass
    if _class == 'Random':
        races = s.query(db.HalloweenClasses.CurrentClass).filter(db.HalloweenClasses.GuildID == data.guild_id).all()
        c = {}
        for i in races:
            if i.CurrentClass not in classes:
                continue
            if i.CurrentClass not in c:
                c[i.CurrentClass] = 0
            c[i.CurrentClass] += 1
        for i in classes:
            if i not in c:
                c[i] = 0
        if all(c[i] != 0 for i in c) and self_user.CurrentClass != "Human":
            return Responses.CANT
        if c != []:
            _class = sorted(c.items(), key=lambda i: i[1])[0][0]
        else:
            _class = SystemRandom().choice(c)
    elif _class not in classes:
        return Responses.ERROR #"Invalid class"

    self_user.CurrentClass = _class.title()
    s.commit()

    await add_and_log(self, data, self_user, s, previousClass, self_user, datetime.now(tz=timezone.utc))
    return Responses.SUCCESS #"Successfully joined"
