from MFramework.database import alchemy as db
from MFramework.utils.utils import tr, Embed

from datetime import datetime, timedelta, timezone

from .helpers import *

@Humans(cmd='drink', alias='enlist')
async def drink(self, *class_drink, data, language, cmd, **kwargs):
    '''Extended description to use with detailed help command'''
    _class = ' '.join(class_drink)    
    if cmd == 'enlist':
        r = await join_logic(self, data, _class, HUNTERS)
    else:
        if _class.lower() in DRINKS:
            _class = DRINKS.get(_class.lower())
        r = await join_logic(self, data, _class, MONSTERS, True)

    if r is Responses.SUCCESS:
        await self.message(data.channel_id, tr("events.halloween.success_"+cmd, language))
    elif r is Responses.AVAILABLE:
        await self.message(data.channel_id, tr("events.halloween.available_"+cmd, language))
    else:
        await self.message(data.channel_id, tr("events.halloween.cant_"+cmd, language))

@Monsters(cmd='bite')
@Hunters(cmd='cure')
async def turn(self, *target, data, language, cmd, **kwargs):
    '''Extended description to use with detailed help command'''
    if cmd == 'cure':
        OPCODE = await turning_logic(self, data, target, HUNTERS, True, timedelta(hours=2), to_same_class=False)
    else:
        OPCODE = await turning_logic(self, data, target, MONSTERS)
    if type(OPCODE) is tuple:
        OPCODE, r = OPCODE
    if OPCODE is Responses.SUCCESS:
        target, oldClass, currentClass = r
        await self.message(data.channel_id, tr("events.halloween.success_"+cmd, language, author=data.author.id, target=target, previousClass=oldClass, currentClass=currentClass), allowed_mentions={"parse": []})
    elif OPCODE is Responses.COOLDOWN:
        cooldown = COOLDOWNS[cmd] - r
        if cooldown.total_seconds() <= 0:
            return await self.message(data.channel_id, tr("events.halloween.cooldownFinished", language))
        await self.message(data.channel_id, tr("events.halloween.cooldown", language, elapsed=COOLDOWNS[cmd], cooldown=cooldown))
    elif OPCODE is Responses.IMMUNE or OPCODE is Responses.PROTECTED:
        await self.message(data.channel_id, tr("events.halloween.targetImmune", language))
    elif OPCODE is Responses.CANT:
        await self.message(data.channel_id, tr("events.halloween.cant_"+cmd, language))
    elif OPCODE is Responses.FAILED:
        await self.message(data.channel_id, tr("events.halloween.failed_"+cmd, language))
    elif OPCODE is Responses.ERROR:
        await self.message(data.channel_id, tr("events.halloween.error_"+cmd, language, currentClass=immune_table.get(r)))
    else:
        await self.message(data.channel_id, tr("events.halloween.error_generic", language))

@Monsters(help='Shows bitesboard', cmd='bitesboard', alias='biteboard')
@Hunters(help='Shows curesboard', cmd='cureboard', alias='curesboard')
@HalloweenEvent(help='Shows leaderboards')
async def hleaderboard(self, *args, data, language, **kwargs):
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

@HalloweenEvent(help='Shows bites/cures history', alias='bitehistory, curehistory')
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
        u = await get_usernames(self, data.guild_id, entry.ByUser)
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
        u = await get_usernames(self, data.guild_id, entry.UserID)
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

@HalloweenEvent(help='Shows faction statistics')
async def hstats(self, *args, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    session = self.db.sql.session()
    total = session.query(db.HalloweenClasses).filter(db.HalloweenClasses.GuildID == data.guild_id).order_by(db.HalloweenClasses.TurnCount.desc()).all()
    e = Embed()
    totalBites, totalPopulation = get_total(self, data, total)
    e.setDescription(tr("events.halloween.totalBites", language)+'/'+tr("events.halloween.totalCures", language)+f": {totalBites}\n"+'\n'.join('{}: {}'.format(tr("events.halloween."+i.lower().replace(' ','_'), language, count=totalPopulation[i]).title(), totalPopulation[i]) for i in totalPopulation))
    await self.embed(data.channel_id, "", e.embed)

@HalloweenEvent(help='Shows current cooldowns')
async def cooldown(self, *args, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    s = self.db.sql.session()
    self_user = get_user(data.guild_id, data.author.id, s)
    cooldown = datetime.now(tz=timezone.utc) - self_user.LastAction
    if self_user.CurrentClass in HUNTERS:
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
    elif self_user.CurrentClass in MONSTERS:
        others, _current_race, _current_target = get_race_counts(s, data, self_user, self_user)
        if others // 2 < _current_race:
            difference = _current_race - others // 2
        else:
            difference = (_current_race - others // 2) * 2
        _cooldown = timedelta(minutes=difference*3)
    cooldown = timedelta(hours=3)+_cooldown - cooldown
    if cooldown.total_seconds() < 0:
        return await self.message(data.channel_id, tr("events.halloween.cooldownFinished", language))
    await self.message(data.channel_id, tr("events.halloween.remainingCooldown", language, cooldown=cooldown))
    
@HalloweenEvent(help="Shows user's profile")
async def hprofile(self, *user, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    if user != ():
        data.author.id = get_user_id(user)
    s = self.db.sql.session()
    self_user = get_user(data.guild_id, data.author.id, s)
    if self_user is not None:
        e = Embed()
        if self_user.CurrentClass in HUNTERS:
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
            u = await get_usernames(self, data, self_user.ProtectedBy)
            effects += tr("events.halloween.effect_biteProtection", language, user=u)
        if effects != "":
            e.addField(tr("events.halloween.activeEffects", language), effects, True)
        await self.embed(data.channel_id, "", e.embed)
