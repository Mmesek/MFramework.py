from MFramework.commands import register
from MFramework.database import alchemy as db
from datetime import datetime, timedelta, timezone
from MFramework.utils.utils import parseMention
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
@register(group='Global', help='HALLOWEEN COMMAND', alias='bite, drink, cure, enlist', category='')
async def halloween(self, *class_or_user, data, language, cmd, **kwargs):
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

@register(group='Global', help='Shows bites/cures history', alias='bitehistory, curehistory', category='')
async def hhistory(self, *args, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    session = self.db.sql.session()
    history = session.query(db.HalloweenLog).filter(db.HalloweenLog.GuildID == data.guild_id, db.HalloweenLog.UserID == data.author.id).all()
    s = ""
    for x, entry in enumerate(history):
        try:
            u = self.cache[data.guild_id].members[entry.ByUser].user.username
        except:
            try:
                u = await self.get_guild_member(data.guild_id, entry.ByUser)
            except:
                continue
            self.cache[data.guild_id].members[entry.ByUser] = u
            u = u.user.username
        i = f'\n`[{entry.Timestamp.strftime("%Y/%m/%d %H:%M")}]` Turned from `{entry.FromClass}` into `{entry.ToClass}` by `{u}`'
        if len(i) + len(s) > 2048:
            break
        else:
            s += i
    e = Embed()
    if s != '':
        e.setDescription(s)
    my_bites = session.query(db.HalloweenLog).filter(db.HalloweenLog.GuildID == data.guild_id, db.HalloweenLog.ByUser == data.author.id).all()
    s = ""
    for x, entry in enumerate(my_bites):
        try:
            u = self.cache[data.guild_id].members[entry.UserID].user.username
        except:
            try:
                u = await self.get_guild_member(data.guild_id, entry.UserID)
            except:
                continue
            self.cache[data.guild_id].members[entry.UserID] = u
            u = u.user.username
        i = f'\n`[{entry.Timestamp.strftime("%Y/%m/%d %H:%M")}]` Turned `{u}` from `{entry.FromClass}` into `{entry.ToClass}`'
        if len(i) + len(s) > 1024:
            break
        else:
            s += i
    if s != '':
        e.addField("Your actions", s)
    await self.embed(data.channel_id, "", e.embed)
