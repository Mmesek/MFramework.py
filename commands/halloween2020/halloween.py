from MFramework.commands import register
from MFramework.database import alchemy as db
from datetime import datetime, timedelta, timezone
from MFramework.utils.utils import parseMention, tr
from random import SystemRandom
immune_table = {
    "Vampire": "Vampire Hunter",
    "Werewolf": "Huntsman",
    "Zombie": "Zombie Slayer",
    "Zombie Slayer": "Zombie",
    "Huntsman": "Werewolf",
    "Vampire Hunter": "Vampire"
}
monsters = ['Vampire', "Werewolf", "Zombie"]
hunters = ["Vampire Hunter", "Huntsman", "Zombie Slayer"]
drinks = {
    "wine": "Vampire",
    "bloody red wine": "Vampire",
    "moonshine": "Werewolf",
    "vodka": "Zombie",
    'vodka braaaainzz?':"Zombie"    
}
@register(group='Global', help='HALLOWEEN COMMAND', alias='', category='', notImpl=True)
async def _halloween(self, *class_or_user, data, language, cmd, **kwargs):
    '''Extended description to use with detailed help command'''
    if ' '.join(class_or_user) == 'help':
        await self.message(data.channel_id, 'Available commands are:\nenlist [class] - Join Hunters\ndrink [drink] - Drink an elixir to join the Dark Side™\nbite [user] - Bite someone!\ncure [user] - Bring them back to The Light!')
    s = self.db.sql.session()
    self_user = s.query(db.HalloweenClasses).filter(db.HalloweenClasses.GuildID == data.guild_id, db.HalloweenClasses.UserID == data.author.id).first()
    if self_user is not None and self_user.LastAction is not None and ' '.join(class_or_user) == 'cooldown':
        cooldown = datetime.now(tz=timezone.utc) - self_user.LastAction
        return await self.message(data.channel_id, f"Remaining Cooldown: {timedelta(hours=4) - cooldown}")
    roles = s.query(db.HalloweenRoles).filter(db.HalloweenRoles.GuildID == data.guild_id).all()
    roles = {i.RoleName: i.RoleID for i in roles}
    if self_user is None or self_user.CurrentClass == 'Human':
        if cmd in ['bite', 'cure']:
            await self.message(data.channel_id, "This action is outside your expertise")
        _class = ' '.join(class_or_user)
        if cmd in ['drink'] and self_user is None and (_class.lower() in ['vampire', 'werewolf', 'zombie'] or _class.lower() in drinks):
            if _class.lower() in drinks:
                _class = drinks.get(_class.lower())
            self_user = db.HalloweenClasses(data.guild_id, data.author.id)
            self_user.CurrentClass = _class.capitalize()
            self.db.sql.add(self_user)
            s.add(db.HalloweenLog(data.guild_id, self_user.UserID, "Human", self_user.CurrentClass, self_user.UserID, datetime.now(tz=timezone.utc)))
            if roles != {}:
                role_id = roles.get(self_user.CurrentClass, "")
                await self.add_guild_member_role(data.guild_id, data.author.id, role_id, "Halloween Minigame")
            await self.message(data.channel_id, "Welcome to the Dark Side™. You can now use `bite` command.")
        elif _class.lower() in ['vampire hunter', 'huntsman', 'zombie slayer']:
            _new = False
            if self_user is None:
                _new = True
                self_user = db.HalloweenClasses(data.guild_id, data.author.id)
            self_user.CurrentClass = _class.title()
            if not _new:
                s.merge(self_user)
            else:
                self.db.sql.add(self_user)
            s.add(db.HalloweenLog(data.guild_id, self_user.UserID, "Human", self_user.CurrentClass, self_user.UserID, datetime.now(tz=timezone.utc)))
            if roles != {}:
                role_id = roles.get(self_user.CurrentClass, "")
                await self.add_guild_member_role(data.guild_id, data.author.id, role_id, "Halloween Minigame")
            await self.message(data.channel_id, "You have successfully joined ranks of hunters. You can now use `cure` command.")
        else:
            if cmd in ['drink'] and self_user is None:
                await self.message(data.channel_id, 'Available drinks:\n- Bloody Red Wine (Become Vampire)\n- Moonshine (Become Werewolf)\n- Vodka "Braaaainzz?" (Become Zombie)')
            elif cmd in ['drink']:
                await self.message(data.channel_id, "Sorry. Drinks are only available to freshbloods")
            elif cmd in ['enlist']:
                await self.message(data.channel_id, 'Available classes:\n- Vampire Hunter\n- Huntsman\n- Zombie Slayer')
    elif cmd in ['drink']:
        await self.message(data.channel_id, "Sorry. Drinks are only available to freshbloods")
    elif cmd in ['enlist']:
        await self.message(data.channel_id, "You have to be human to use that!")
    else:
        if self_user.LastAction == None or (datetime.now(tz=timezone.utc) - self_user.LastAction > timedelta(hours=4)):
            if class_or_user != ():
                target = parseMention(class_or_user[0])
                if target.isdigit():
                    target = int(target)
            else:
                target = None
            target_user = s.query(db.HalloweenClasses).filter(db.HalloweenClasses.GuildID == data.guild_id, db.HalloweenClasses.UserID == target).first()
            if cmd in ['bite'] and self_user.CurrentClass in monsters:
                if (target_user is not None and target_user.CurrentClass not in monsters) or target_user is None:
                    _target_user = False
                    if target_user is None:
                        target_user = db.HalloweenClasses(data.guild_id, target, 'Human')
                        _target_user = None
                    if immune_table.get(target_user.CurrentClass, '') != self_user.CurrentClass:
                        previousClass = target_user.CurrentClass
                        target_user.CurrentClass = self_user.CurrentClass
                        target_user.LastUser = self_user.UserID
                        self_user.LastVictim = target_user.UserID
                        self_user.LastAction = datetime.now(tz=timezone.utc)
                        if self_user.CurrentClass == 'Vampire':
                            self_user.VampireStats += 1
                        elif self_user.CurrentClass == 'Werewolf':
                            self_user.WerewolfStats += 1
                        elif self_user.CurrentClass == 'Zombie':
                            self_user.ZombieStats += 1
                        target_user.TurnCount += 1
                        if _target_user is None:
                            self.db.sql.add(target_user)
                        else:
                            s.merge(target_user)
                        s.add(db.HalloweenLog(data.guild_id, target_user.UserID, previousClass, target_user.CurrentClass, self_user.UserID, self_user.LastAction))
                        if roles != {}:
                            role_id = roles.get(previousClass, "")
                            await self.remove_guild_member_role(data.guild_id, target, role_id, "Halloween Minigame")
                            role_id = roles.get(self_user.CurrentClass, "")
                            await self.add_guild_member_role(data.guild_id, target, role_id, "Halloween Minigame")
                        await self.message(data.channel_id, f'Successfully turned <@{target}> into {self_user.CurrentClass}', allowed_mentions={"parse":[]})
                    else:
                        await self.message(data.channel_id, "Your target is immune to that")
                else:
                    await self.message(data.channel_id, "Your target is immune to that")
            elif cmd in ['bite'] and self_user.CurrentClass in hunters:
                await self.message(data.channel_id, "You are not doing such savage actions! You cure others from that!")
            elif cmd in ['cure'] and self_user.CurrentClass in monsters:
                await self.message(data.channel_id, "Cure? Cure from what? You bite others!")
            elif cmd in ['cure'] and self_user.CurrentClass in hunters:
                if target_user is not None and target_user.CurrentClass not in hunters:
                    if immune_table.get(target_user.CurrentClass) == self_user.CurrentClass:
                        previousClass = target_user.CurrentClass
                        target_user.CurrentClass = 'Human'
                        target_user.LastUser = self_user.UserID
                        self_user.LastVictim = target_user.UserID
                        self_user.LastAction = datetime.now(tz=timezone.utc)
                        if self_user.CurrentClass == 'Vampire Hunter':
                            self_user.VampireHunterStats += 1
                        elif self_user.CurrentClass == 'Huntsman':
                            self_user.HuntsmanStats += 1
                        elif self_user.CurrentClass == 'Zombie Slayer':
                            self_user.ZombieSlayerStats += 1
                        target_user.TurnCount += 1
                        s.merge(target_user)
                        s.add(db.HalloweenLog(data.guild_id, target_user.UserID, previousClass, target_user.CurrentClass, self_user.UserID, self_user.LastAction))
                        if roles != {}:
                            role_id = roles.get(previousClass, "")
                            await self.remove_guild_member_role(data.guild_id, target, role_id, "Halloween Minigame")
                            role_id = roles.get(target_user.CurrentClass, "")
                            await self.add_guild_member_role(data.guild_id, target, role_id, "Halloween Minigame")
                        await self.message(data.channel_id, f'Successfully cured <@{target}> from {previousClass}', allowed_mentions={"parse":[]})
                    else:
                        await self.message(data.channel_id, f"Provided user is not {immune_table.get(self_user.CurrentClass)}")
                else:
                    await self.message(data.channel_id, f"Provided user is not {immune_table.get(self_user.CurrentClass)}")
            elif cmd in ['bite'] and self_user.CurrentClass not in monsters:
                await self.message(data.channel_id, f"You can't do that!")
            elif cmd in ['cure'] and self_user.CurrentClass not in hunters:
                await self.message(data.channel_id, f"You can't do that!")
        else:
            cooldown = datetime.now(tz=timezone.utc) - self_user.LastAction
            await self.message(data.channel_id, f"Last action was done less than 4h ago! Remaining Cooldown: {timedelta(hours=4) - cooldown}")
    s.commit()

def get_user_and_roles(data, s):
    self_user = s.query(db.HalloweenClasses).filter(db.HalloweenClasses.GuildID == data.guild_id, db.HalloweenClasses.UserID == data.author.id).first()
    roles = s.query(db.HalloweenRoles).filter(db.HalloweenRoles.GuildID == data.guild_id).all()
    roles = {i.RoleName: i.RoleID for i in roles}
    return self_user, roles

def get_cooldown(user):
    if user is not None and user.LastAction is not None:
        return datetime.now(tz=timezone.utc) - user.LastAction
    return 0

async def _join_logic(self, data, _class, classes, first_only=False):
    s = self.db.sql.session()
    self_user, roles = get_user_and_roles(data, s)
    if first_only and self_user is not None:
        return None
    if self_user is None or self_user.CurrentClass == 'Human':
        _class = ' '.join(_class) if type(_class) is tuple else _class
        if _class.lower() in classes:
            _new = False
            if self_user is None:
                _new = True
                self_user = db.HalloweenClasses(data.guild_id, data.author.id)
            self_user.CurrentClass = _class.title()
            if not _new:
                s.merge(self_user)
            else:
                self.db.sql.add(self_user)
            s.add(db.HalloweenLog(data.guild_id, self_user.UserID, "Human", self_user.CurrentClass, self_user.UserID, datetime.now(tz=timezone.utc)))
            if roles != {}:
                role_id = roles.get(self_user.CurrentClass, "")
                await self.add_guild_member_role(data.guild_id, data.author.id, role_id, "Halloween Minigame")
            s.commit()
            return True
        return None
    return False

async def _turning_logic(self, data, target, side, hunters=False, action_cooldown=timedelta(hours=3), skip_cooldown=False):
    s = self.db.sql.session()
    self_user, roles = get_user_and_roles(data, s)
    if self_user is None:
        return None
    if self_user.CurrentClass not in side:
        return -1
    if self_user.LastAction != None:
        cooldown = get_cooldown(self_user)
    else:
        cooldown = 0
    if self_user.LastAction == None or (cooldown > action_cooldown) or skip_cooldown:
        try:
            target = parseMention(target[0])
            target = int(target)
        except:
            return (1, None, None, None, cooldown)
        target_user = s.query(db.HalloweenClasses).filter(db.HalloweenClasses.GuildID == data.guild_id, db.HalloweenClasses.UserID == target).first()
        if self_user.CurrentClass in side:
            if (target_user is not None and target_user.CurrentClass not in side) or target_user is None:
                _target_user = False
                if target_user is None:
                    target_user = db.HalloweenClasses(data.guild_id, target, 'Human')
                    _target_user = None
                
                if (
                    (hunters and immune_table.get(target_user.CurrentClass) == self_user.CurrentClass) or
                    (hunters is False and immune_table.get(target_user.CurrentClass, '') != self_user.CurrentClass)
                ):
                    timestamp = datetime.now(tz=timezone.utc)
                    if not skip_cooldown:
                        self_user.LastAction = timestamp
                    if hunters is False or (hunters is False and target_user.CurrentClass != 'Human'):
                        users = s.query(db.HalloweenClasses.CurrentClass).filter(db.HalloweenClasses.GuildID == data.guild_id).all()
                        others = 0
                        _current_race = 0
                        _hunters = {}
                        for i in users:
                            if i.CurrentClass == self_user.CurrentClass:
                                _current_race += 1
                            elif i.CurrentClass in monsters:
                                others += 1
                            elif i.CurrentClass != "Human":
                                if i.CurrentClass not in _hunters:
                                    _hunters[i.CurrentClass] = 0
                                _hunters[i.CurrentClass] += 1
                        if others // 2 < _current_race:
                            difference = _current_race - others // 2
                            roll = SystemRandom().randint(0, 25)
                            if roll < difference:
                                return -2
                    previousClass = target_user.CurrentClass
                    target_user.CurrentClass = self_user.CurrentClass if not hunters else 'Human'
                    target_user.LastUser = self_user.UserID
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
                    target_user.TurnCount += 1
                    if _target_user is None:
                        self.db.sql.add(target_user)
                    else:
                        s.merge(target_user)
                    s.add(db.HalloweenLog(data.guild_id, target_user.UserID, previousClass, target_user.CurrentClass, self_user.UserID, timestamp))
                    s.commit()
                    if roles != {}:
                        role_id = roles.get(previousClass, "")
                        await self.remove_guild_member_role(data.guild_id, target, role_id, "Halloween Minigame")
                        role_id = roles.get(self_user.CurrentClass, "")
                        await self.add_guild_member_role(data.guild_id, target, role_id, "Halloween Minigame")
                    return (True, target, previousClass, target_user.CurrentClass, cooldown)
                return None
        return (-1, None, None, self_user.CurrentClass, cooldown)
    return (1, None, None, None, cooldown)

def get_race_counts(s, data, self_user, target_user):
    users = s.query(db.HalloweenClasses.CurrentClass).filter(db.HalloweenClasses.GuildID == data.guild_id).all()
    others = 0
    _current_race = 0
    _current_target = 0
    for i in users:
        if i.CurrentClass == self_user.CurrentClass:
            _current_race += 1
        elif i.CurrentClass in monsters:
            others += 1
        elif i.CurrentClass != "Human" and i.CurrentClass == target_user.CurrentClass:
            _current_target += 1
    return others, _current_race, _current_target

async def turning_logic(self, data, target, side, _hunters=False, action_cooldown=timedelta(hours=3), skip_cooldown=False, to_same_class=True):
    s = self.db.sql.session()
    self_user, roles = get_user_and_roles(data, s)
    if self_user is None:
        return None #"User doesn't have a class"
    if self_user.CurrentClass not in side:
        return -1 #"User is not a monster or a hunter"
    try:
        target = get_user_id(target)
    except:
        cooldown = get_cooldown(self_user)
        return (1, None, None, None, cooldown) #"Target is either not specified or wrongly specified"
    target_user = s.query(db.HalloweenClasses).filter(db.HalloweenClasses.GuildID == data.guild_id, db.HalloweenClasses.UserID == target).first()
    if target_user is None:
        target_user = db.HalloweenClasses(data.guild_id, target, "Human")
    elif target_user.CurrentClass in side:
        return (None, None, None, self_user.CurrentClass, None) #"Target is on the same side"
    others, _current_race, _current_target = get_race_counts(s, data, self_user, target_user)
    if not _hunters:
        if others // 2 < _current_race:
            difference = _current_race - others // 2
            roll = SystemRandom().randint(0, 75)
            if roll < difference:
                return -2 #"Failed to bite"
        elif _current_target == 1:
            return -2 #"Failed to bite"
        else:
            difference = (_current_race - others // 2) * 2
        action_cooldown += timedelta(minutes=difference*3)
    if self_user.LastAction != None:
        cooldown = get_cooldown(self_user)
        if not skip_cooldown and cooldown < action_cooldown:
            return (1, None, None, None, cooldown) #"Cooldown not ready"
    if ((_hunters and immune_table.get(target_user.CurrentClass) != self_user.CurrentClass) or
        (_hunters is False and immune_table.get(target_user.CurrentClass, '') == self_user.CurrentClass)):
        return None #"Target is immune"
    timestamp = datetime.now(tz=timezone.utc)
    if not skip_cooldown:
        self_user.LastAction = timestamp
        s.commit()
    if target_user.ProtectionEnds is not None and target_user.ProtectionEnds > timestamp:
        return -2 #"Target is protected"
    previousClass = target_user.CurrentClass
    target_user.CurrentClass = self_user.CurrentClass if to_same_class else "Human"
    target_user.LastUser = self_user.UserID
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
    target_user.TurnCount += 1
    await add_and_log(self, data, target_user, roles, s, previousClass, self_user, timestamp)
    s.commit()
    return (True, target, previousClass, target_user.CurrentClass, timestamp) #"Target Bitten successfuly"

async def join_logic(self, data, _class, classes, first_only=False):
    s = self.db.sql.session()
    self_user, roles = get_user_and_roles(data, s)
    if first_only and self_user is not None and _class != 'random':
        return None #"This action is only for first timers"
    _class = ' '.join(_class) if type(_class) is tuple else _class
    if self_user is None:
        self_user = db.HalloweenClasses(data.guild_id, data.author.id)
    elif self_user.CurrentClass != "Human":
        users = s.query(db.HalloweenClasses.CurrentClass).filter(db.HalloweenClasses.GuildID == data.guild_id, db.HalloweenClasses.CurrentClass == _class).all()
        if not (users is None or users == []):
            return False #"Not a human"
    previousClass = self_user.CurrentClass
    if _class == 'random':
        races = s.query(db.HalloweenClasses.CurrentClass).filter(db.HalloweenClasses.GuildID == data.guild_id).all()
        c = {}
        for i in races:
            if i not in classes:
                continue
            if i not in c:
                c[i] = 0
            c[i] += 1
        _class = sorted(c.items(), key=lambda i: i[1])[0][0]
    elif _class.lower() not in classes:
        return None #"Invalid class"
    self_user.CurrentClass = _class.title()
    await add_and_log(self, data, self_user, roles, s, previousClass, self_user, datetime.now(tz=timezone.utc))
    s.commit()
    return True #"Successfully joined"

async def add_and_log(self, data, target, roles, s, previousClass, self_user, timestamp):
    s.merge(target)
    s.add(db.HalloweenLog(data.guild_id, target.UserID, previousClass, target.CurrentClass, self_user.UserID, timestamp))
    s.commit()
    if roles != {}:
        role_id = roles.get(previousClass, "")
        await self.remove_guild_member_role(data.guild_id, target.UserID, role_id, "Halloween Minigame")
        role_id = roles.get(target.CurrentClass, "")
        await self.add_guild_member_role(data.guild_id, target.UserID, role_id, "Halloween Minigame")

@register(group='Global', help='Short description to use with help command', alias='', category='')
async def enlist(self, *_class, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    r = await join_logic(self, data, _class, ['vampire hunter', 'huntsman', 'zombie slayer'])
    if r:
        await self.message(data.channel_id, tr("events.halloween.success_enlist", language))
    elif r is None:
        await self.message(data.channel_id, tr("events.halloween.availableClasses", language))#'Available classes:\n- Vampire Hunter\n- Huntsman\n- Zombie Slayer')
    else:
        await self.message(data.channel_id, tr("events.halloween.cant_enlist", language))

@register(group='Global', help='Short description to use with help command', alias='', category='')
async def drink(self, *drink, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    _class = ' '.join(drink)
    if _class.lower() in drinks:
        _class = drinks.get(_class.lower())
    r = await join_logic(self, data, _class, ['vampire', 'werewolf', 'zombie'], True)
    if r:
        await self.message(data.channel_id, tr("events.halloween.success_drink", language))
    elif r is False:
        await self.message(data.channel_id, tr("events.halloween.availableDrinks", language))#'Available drinks:\n- Bloody Red Wine (Become Vampire)\n- Moonshine (Become Werewolf)\n- Vodka "Braaaainzz?" (Become Zombie)')
    else:
        await self.message(data.channel_id, tr("events.halloween.cant_drink", language))

@register(group='Global', help='Short description to use with help command', alias='', category='')
async def bite(self, *target, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    r = await turning_logic(self, data, target, monsters)
    if type(r) is tuple:
        target = r[1]
        newClass = r[3]
        cooldown = r[4]
        r = r[0]
    if r is True:
        await self.message(data.channel_id, tr("events.halloween.success_bite", language, target=target, currentClass=newClass), allowed_mentions={"parse": []})
    elif r == 1:
        cooldown = timedelta(hours=3) - cooldown
        if cooldown.total_seconds() < 0:
            return await self.message(data.channel_id, tr("events.halloween.cooldownFinished", language))
        await self.message(data.channel_id, tr("events.halloween.cooldown", language, elapsed="3h", cooldown=cooldown))
    elif r is None:
        await self.message(data.channel_id, tr("events.halloween.targetImmune", language))
    elif r == -1:
        await self.message(data.channel_id, tr("events.halloween.cant_bite", language))
    elif r == -2:
        await self.message(data.channel_id, tr("events.halloween.failed_bite", language))
    else:
        await self.message(data.channel_id, tr("events.halloween.error_generic", language))

@register(group='Global', help='Short description to use with help command', alias='', category='')
async def cure(self, *target, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    r = await turning_logic(self, data, target, hunters, True, timedelta(hours=2), to_same_class=False)
    if type(r) is tuple:
        target = r[1]
        oldClass = r[2]
        currentClass = r[3]
        cooldown = r[4]
        r = r[0]
    if r is True:
        await self.message(data.channel_id, tr("events.halloween.success_cure", language, target=target, previousClass=oldClass), allowed_mentions={"parse": []})
    elif r == 1:
        cooldown = timedelta(hours=2) - cooldown
        if cooldown.total_seconds() < 0:
            return await self.message(data.channel_id, tr("events.halloween.cooldownFinished", language))
        await self.message(data.channel_id, tr("events.halloween.cooldown", language, elapsed="2h", cooldown=cooldown))
    elif r is None:
        await self.message(data.channel_id, tr("events.halloween.error_cure", language, currentClass=immune_table.get(currentClass)))
    elif r == -1:
        await self.message(data.channel_id, tr("events.halloween.cant_cure", language))
    else:
        await self.message(data.channel_id, tr("events.halloween.error_generic", language))#, currentClass=immune_table.get(currentClass)))

def get_user_id(user):
    return int(parseMention(user[0]))

@register(group='Global', help='Short description to use with help command', alias='', category='')
async def defend(self, *user, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    s = self.db.sql.session()
    self_user, roles = get_user_and_roles(data, s)
    if self_user is None or self_user.CurrentClass not in hunters:
        return
    if self_user.ActionCooldownEnd is not None:
        if datetime.now(tz=timezone.utc) < self_user.ActionCooldownEnd:
            cooldown = self_user.ActionCooldownEnd - datetime.now(tz=timezone.utc)
            return await self.message(data.channel_id, tr("events.halloween.remainingCooldown", language, cooldown=cooldown))
    target = get_user_id(user)
    target_user = s.query(db.HalloweenClasses).filter(db.HalloweenClasses.GuildID == data.guild_id, db.HalloweenClasses.UserID == target).first()
    if target_user.CurrentClass in hunters:
        if target_user.ProtectionEnds is None or target_user.ProtectionEnds < datetime.now(tz=timezone.utc):
            duration = SystemRandom().randint(5, 40)
            delta = datetime.now(tz=timezone.utc) + timedelta(minutes=duration)
            target_user.ProtectedBy = data.author.id
            target_user.ProtectionEnds = delta
            self_user.ActionCooldownEnd = datetime.now(tz=timezone.utc) + timedelta(hours=1)
            s.add(db.HalloweenLog(data.guild_id, target_user.UserID, target_user.CurrentClass, target_user.CurrentClass, self_user.UserID, datetime.now(tz=timezone.utc)))
            s.commit()
            return await self.message(data.channel_id, tr("events.halloween.success_defend", language, duration=duration))
        return await self.message(data.channel_id, tr("events.halloween.error_defend", language))
    return await self.message(data.channel_id, tr("events.halloween.cant_defend", language))
    
        

@register(group='Global', help='Short description to use with help command', alias='', category='')
async def betray(self, *user, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    s = self.db.sql.session()
    self_user, roles = get_user_and_roles(data, s)
    if self_user is None or self_user.CurrentClass not in hunters:
        return
    if self_user.ActionCooldownEnd is not None:
        if datetime.now(tz=timezone.utc) < self_user.ActionCooldownEnd:
            cooldown = self_user.ActionCooldownEnd - datetime.now(tz=timezone.utc)
            return await self.message(data.channel_id, tr("events.halloween.remainingCooldown", language, cooldown=cooldown))
    roll = SystemRandom().randint(0, 100)
    self_user.ActionCooldownEnd = datetime.now(tz=timezone.utc) + timedelta(hours=4)
    s.commit()
    if roll > 97:
        await turning_logic(self, data, user, hunters, True, skip_cooldown=True)
        return await self.message(data.channel_id, tr("events.halloween.success_betray", language))
    return await self.message(data.channel_id, tr("events.halloween.error_betray", language))
    

@register(group='Global', help='Short description to use with help command', alias='', category='')
async def cooldown(self, *args, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    s = self.db.sql.session()
    self_user, roles = get_user_and_roles(data, s)
    cooldown = get_cooldown(self_user)
    cooldown = datetime.now(tz=timezone.utc) - self_user.LastAction
    if self_user.CurrentClass in hunters:
        cooldown = timedelta(hours=2) - cooldown
        if self_user.ActionCooldownEnd is not None:
            action_cooldown = self_user.ActionCooldownEnd - datetime.now(tz=timezone.utc)
        else:
            action_cooldown = timedelta(seconds=-1)
        if cooldown.total_seconds() < 0:
            cooldown = tr("events.halloween.ready", language)
        if action_cooldown.total_seconds() < 0:
            action_cooldown = tr("events.halloween.ready", language)
        return await self.message(data.channel_id, tr("events.halloween.remainingCooldowns", language, cooldown=cooldown, action=action_cooldown))
    cooldown = timedelta(hours=3) - cooldown
    if cooldown.total_seconds() < 0:
        return await self.message(data.channel_id, tr("events.halloween.cooldownFinished", language))
    await self.message(data.channel_id, tr("events.halloween.remainingCooldown", language, cooldown=cooldown))
    

@register(group='Global', help='Short description to use with help command', alias='', category='')
async def hprofile(self, *user, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    if user != ():
        data.author.id = get_user_id(user)
    s = self.db.sql.session()
    self_user, roles = get_user_and_roles(data, s)
    if self_user is not None:
        e = Embed()
        if self_user.CurrentClass in hunters:
            t = tr("events.halloween.Profession", language)
        else:
            t = tr("events.halloween.Race", language)
        r = self_user.CurrentClass.lower().replace(' ', '_')
        e.addField(t, tr("events.halloween."+r, language, count=1).title(), True)
        bites = 0
        cures = 0
        for i in [self_user.VampireHunterStats, self_user.HuntsmanStats, self_user.ZombieSlayerStats]:
            cures += i
        for i in [self_user.WerewolfStats, self_user.VampireStats, self_user.ZombieStats]:
            bites += i
        e.addField(tr("events.halloween.totalBites", language), str(bites), True)
        e.addField(tr("events.halloween.totalCures", language), str(cures), True)
        e.addField(tr("events.halloween.totalTurns", language), str(self_user.TurnCount), True)
        if self_user.LastAction is not None:
            e.setFooter("", tr("events.halloween.lastAction", language)).setTimestamp(self_user.LastAction.isoformat())
        effects = ""
        if self_user.ProtectionEnds is not None and datetime.now(timezone.utc) < self_user.ProtectionEnds:
            u = get_usernames(self, data, self_user.ProtectedBy)
            effects += tr("events.halloween.effect_biteProtection", language, user=u)
        if effects != "":
            e.addField(tr("events.halloween.activeEffects", language), effects, True)
        await self.embed(data.channel_id, "", e.embed)

@register(group='System', help='Creates roles', alias='', category='')
async def createHalloweenRoles(self, *args, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    roles = ["Human",
    "Vampire", "Werewolf",
    "Zombie", "Vampire Hunter",
    "Huntsman", "Zombie Slayer"]
    s = self.db.sql.session()
    for name in roles:
        role = await self.create_guild_role(data.guild_id, name, 0, None, False, False, "Created Role for Halloween Minigame")
        s.merge(db.HalloweenRoles(data.guild_id, role.name, role.id))
    s.commit()

@register(group='System', help='Adds roles', alias='', category='')
async def addRoles(self, *args, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    s = self.db.sql.session()
    roles = s.query(db.HalloweenRoles).filter(db.HalloweenRoles.GuildID == data.guild_id).all()
    roles = {i.RoleName: i.RoleID for i in roles}
    users = s.query(db.HalloweenClasses).filter(db.HalloweenClasses.GuildID == data.guild_id).all()
    for user in users:
        await self.add_guild_member_role(data.guild_id, user.UserID, roles.get(user.CurrentClass, ""), "Halloween Minigame")

from MFramework.utils.utils import Embed
@register(group='Global', help='Shows leaderboards', alias='bitesboard, biteboard, cureboard, curesboard', category='')
async def leaderboard(self, *args, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    session = self.db.sql.session()
    total = session.query(db.HalloweenClasses).filter(db.HalloweenClasses.GuildID == data.guild_id).order_by(db.HalloweenClasses.TurnCount.desc()).all()
    e = Embed().setTitle("Bitesboard")
    vampireStats = []
    werewolfStats = []
    zombieStats = []
    vampireHunterStats = []
    huntsmanStats = []
    zombieSlayerStats = []
    totalPopulation = {}
    totalBites = 0
    for v in total:
        try:
            u = self.cache[data.guild_id].members[v.UserID].user.username
        except:
            try:
                u = await self.get_guild_member(data.guild_id, v.UserID)
            except:
                continue
            self.cache[data.guild_id].members[v.UserID] = u
            u = u.user.username
        if v.VampireStats > 0:
            vampireStats.append((u, v.VampireStats))
        if v.WerewolfStats > 0:
            werewolfStats.append((u, v.WerewolfStats))
        if v.ZombieStats > 0:
            zombieStats.append((u, v.ZombieStats))
        if v.VampireHunterStats > 0:
            vampireHunterStats.append((u, v.VampireHunterStats))
        if v.HuntsmanStats > 0:
            huntsmanStats.append((u, v.HuntsmanStats))
        if v.ZombieSlayerStats > 0:
            zombieSlayerStats.append((u, v.ZombieSlayerStats))
        if v.CurrentClass not in totalPopulation:
            totalPopulation[v.CurrentClass] = 0
        totalPopulation[v.CurrentClass] += 1
        if v.TurnCount > 0:
            totalBites += v.TurnCount
    biteboard = "```md\nBites | User\n============================\n{}```"
    cureboard = "```md\nCures | User\n============================\n{}```"
    if vampireStats != []:
        vampireStats.sort(key=lambda i: i[1], reverse=True)
        e.addField("Vampire Bites", biteboard.format('\n'.join('{0:4}. | {1:}'.format(i[1], i[0]) for i in vampireStats[:10])))
    if werewolfStats != []:
        werewolfStats.sort(key=lambda i: i[1], reverse=True)
        e.addField("Werewolf Bites", biteboard.format('\n'.join('{0:4}. | {1:}'.format(i[1], i[0]) for i in werewolfStats[:10])))
    if zombieStats != []:
        zombieStats.sort(key=lambda i: i[1], reverse=True)
        e.addField("Zombie Bites", biteboard.format('\n'.join('{0:4}. | {1:}'.format(i[1], i[0]) for i in zombieStats[:10])))
    if vampireHunterStats != []:
        vampireHunterStats.sort(key=lambda i: i[1], reverse=True)
        e.addField("Vampire Hunter Cures", cureboard.format('\n'.join('{0:4}. | {1:}'.format(i[1], i[0]) for i in vampireHunterStats[:10])))
    if huntsmanStats != []:
        huntsmanStats.sort(key=lambda i: i[1], reverse=True)
        e.addField("Huntsman Cures", cureboard.format('\n'.join('{0:4}. | {1:}'.format(i[1], i[0]) for i in huntsmanStats[:10])))
    if zombieSlayerStats != []:
        zombieSlayerStats.sort(key=lambda i: i[1], reverse=True)
        e.addField("Zombie Slayer Cures", cureboard.format('\n'.join('{0:4}. | {1:}'.format(i[1], i[0]) for i in zombieSlayerStats[:10])))

    e.setDescription(f"Total Bites/Cures: {totalBites}\n"+'\n'.join('{}s: {}'.format(i if i != 'Werewolf' else 'Werewolve', totalPopulation[i]) for i in totalPopulation))
    await self.embed(data.channel_id, "", e.embed)

async def get_usernames(self, data, user_id):
    try:
        u = self.cache[data.guild_id].members[user_id].user.username
    except:
        try:
            u = await self.get_guild_member(data.guild_id, user_id)
        except:
            return None
        self.cache[data.guild_id].members[user_id] = u
        u = u.user.username
    return u


@register(group='Global', help='Shows bites/cures history', alias='bitehistory, curehistory', category='')
async def hhistory(self, *user, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    not_self=False
    if user != ():
        not_self = True
        data.author.id = get_user_id(user)
    session = self.db.sql.session()
    history = session.query(db.HalloweenLog).filter(db.HalloweenLog.GuildID == data.guild_id, db.HalloweenLog.UserID == data.author.id).order_by(db.HalloweenLog.Timestamp.desc()).all()
    s = ""
    for x, entry in enumerate(history):
        u = await get_usernames(self, data, entry.ByUser)
        if u is None:
            continue
        i = f'\n`[{entry.Timestamp.strftime("%Y/%m/%d %H:%M")}]` Turned from `{entry.FromClass}` into `{entry.ToClass}` by `{u}`'
        if len(i) + len(s) > 2048:
            break
        else:
            s += i
    e = Embed()
    if s != '':
        e.setDescription(s)
    my_bites = session.query(db.HalloweenLog).filter(db.HalloweenLog.GuildID == data.guild_id, db.HalloweenLog.ByUser == data.author.id).order_by(db.HalloweenLog.Timestamp.desc()).all()
    s = ""
    for x, entry in enumerate(my_bites):
        u = await get_usernames(self, data, entry.UserID)
        if u is None:
            continue
        i = f'\n`[{entry.Timestamp.strftime("%Y/%m/%d %H:%M")}]` Turned `{u}` from `{entry.FromClass}` into `{entry.ToClass}`'
        if len(i) + len(s) > 1024:
            break
        else:
            s += i
    if s != '':
        if not_self:
            e.addField("Their actions", s)
        else:
            e.addField("Your actions", s)
    await self.embed(data.channel_id, "", e.embed)

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


@register(group='Global', help='Shows faction statistics', alias='', category='')
async def hstats(self, *args, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    session = self.db.sql.session()
    total = session.query(db.HalloweenClasses).filter(db.HalloweenClasses.GuildID == data.guild_id).order_by(db.HalloweenClasses.TurnCount.desc()).all()
    e = Embed()
    totalBites, totalPopulation = get_total(self, data, total)
    e.setDescription(f"Total Bites/Cures: {totalBites}\n"+'\n'.join('{}: {}'.format(tr("events.halloween."+i.lower().replace(' ','_'), language, count=totalPopulation[i]).title(), totalPopulation[i]) for i in totalPopulation))
    await self.embed(data.channel_id, "", e.embed)