from MFramework.database import alchemy as db
from MFramework.utils.utils import Embed

from .helpers import *
from .helpers.utils import _t

@Humans(cmd='enlist', help='Join a hunters side')
@Humans(cmd='drink', help="Drink an unknown beverage to become a monster")
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
        await self.message(data.channel_id, _t("success_"+cmd, language))
    elif r is Responses.AVAILABLE or r is Responses.ERROR:
        await self.message(data.channel_id, _t("available_"+cmd, language))
    else:
        await self.message(data.channel_id, _t("cant_"+cmd, language))

@Monsters(cmd='bite', help="Turns your target")
@Hunters(cmd='cure', help="Cures a monster")
async def turn(self, *target, data, language, cmd, **kwargs):
    '''Extended description to use with detailed help command'''
    if cmd == 'cure':
        OPCODE = await turning_logic(self, data, target, HUNTERS, True, COOLDOWNS[cmd], to_same_class=False)
    else:
        OPCODE = await turning_logic(self, data, target, MONSTERS, False, COOLDOWNS[cmd])
    if type(OPCODE) is tuple:
        OPCODE, r = OPCODE
    if OPCODE is Responses.SUCCESS:
        target, oldClass, currentClass = r
        await self.message(data.channel_id, _t("success_"+cmd, language, author=data.author.id, target=target, previousClass=oldClass, currentClass=currentClass), allowed_mentions={"parse": []})
    elif OPCODE is Responses.COOLDOWN:
        cooldown = COOLDOWNS[cmd] - r
        if cooldown.total_seconds() <= 0:
            return await self.message(data.channel_id, _t("cooldown_finished", language))
        await self.message(data.channel_id, _t("cooldown", language, elapsed=COOLDOWNS[cmd], cooldown=cooldown))
    elif OPCODE is Responses.IMMUNE or OPCODE is Responses.PROTECTED:
        await self.message(data.channel_id, _t("target_immune", language))
    elif OPCODE is Responses.CANT:
        await self.message(data.channel_id, _t("cant_"+cmd, language))
    elif OPCODE is Responses.FAILED:
        await self.message(data.channel_id, _t("failed_"+cmd, language))
    elif OPCODE is Responses.ERROR:
        await self.message(data.channel_id, _t("error_"+cmd, language, currentClass=immune_table.get(r)))
    else:
        await self.message(data.channel_id, _t("error_generic", language))

@Monsters(help='Shows bitesboard', cmd='bitesboard', alias='biteboard')
@Hunters(help='Shows curesboard', cmd='cureboard', alias='curesboard')
@HalloweenEvent(help='Shows leaderboards')
async def hleaderboard(self, *args, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    session = self.db.sql.session()
    total = session.query(db.HalloweenClasses).filter(db.HalloweenClasses.GuildID == data.guild_id).order_by(db.HalloweenClasses.TurnCount.desc()).all()
    e = Embed().setTitle(_t("Bitesboard", language))
    vampireStats = []
    werewolfStats = []
    zombieStats = []
    vampireHunterStats = []
    huntsmanStats = []
    zombieSlayerStats = []
    totalPopulation = {}
    totalBites = 0
    for v in total:
        u = await get_usernames(self, data.guild_id, v.UserID)
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
    _bites = _t("bite", language, count=2).title()
    _cures = _t("cure", language, count=2).title()
    _user = _t("user", language).title()
    biteboard = "```md\n"+_bites+" | "+_user+"\n============================\n{}```"
    cureboard = "```md\n"+_cures+" | "+_user+"\n============================\n{}```"
    if vampireStats != []:
        vampireStats.sort(key=lambda i: i[1], reverse=True)
        e.addField(_t("bites_vampire", language), biteboard.format('\n'.join(('{0:'+str(len(_bites)-1)+'}. | {1:}').format(i[1], i[0]) for i in vampireStats[:10])))
    if werewolfStats != []:
        werewolfStats.sort(key=lambda i: i[1], reverse=True)
        e.addField(_t("bites_werewolf", language), biteboard.format('\n'.join(('{0:'+str(len(_bites)-1)+'}. | {1:}').format(i[1], i[0]) for i in werewolfStats[:10])))
    if zombieStats != []:
        zombieStats.sort(key=lambda i: i[1], reverse=True)
        e.addField(_t("bites_zombie", language), biteboard.format('\n'.join(('{0:'+str(len(_bites)-1)+'}. | {1:}').format(i[1], i[0]) for i in zombieStats[:10])))
    if vampireHunterStats != []:
        vampireHunterStats.sort(key=lambda i: i[1], reverse=True)
        e.addField(_t("cures_vampire_hunter", language), cureboard.format('\n'.join(('{0:'+str(len(_cures)-1)+'}. | {1:}').format(i[1], i[0]) for i in vampireHunterStats[:10])))
    if huntsmanStats != []:
        huntsmanStats.sort(key=lambda i: i[1], reverse=True)
        e.addField(_t("cures_huntsman", language), cureboard.format('\n'.join(('{0:'+str(len(_cures)-1)+'}. | {1:}').format(i[1], i[0]) for i in huntsmanStats[:10])))
    if zombieSlayerStats != []:
        zombieSlayerStats.sort(key=lambda i: i[1], reverse=True)
        e.addField(_t("cures_zombie_slayer", language), cureboard.format('\n'.join(('{0:'+str(len(_cures)-1)+'}. | {1:}').format(i[1], i[0]) for i in zombieSlayerStats[:10])))

    e.setDescription(_t("total_bites", language)+'/'+_t("total_cures", language)+f": {totalBites}\n"+'\n'.join('{}: {}'.format(_t(i.lower().replace(' ','_'), language, count=totalPopulation[i]).title(), totalPopulation[i]) for i in totalPopulation))

    await self.embed(data.channel_id, "", e.embed)

@Monsters(help="Shows bites history", cmd='bitehistory')
@Hunters(help="Shows cures history", cmd='curehistory')
@HalloweenEvent(help='Shows bites/cures history')
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
        i = _t("turned_history", language, timestamp=entry.Timestamp.strftime("%Y/%m/%d %H:%M"), fromClass=entry.FromClass, toClass=entry.ToClass, u=u)
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
        i = _t("turned_victims", language, timestamp=entry.Timestamp.strftime("%Y/%m/%d %H:%M"), fromClass=entry.FromClass, toClass=entry.ToClass, u=u)
        if len(i) + len(s) > 1024:
            break
        else:
            s += i
    if s != '':
        if not_self:
            e.addField(_t("their_actions", language), s)
        else:
            e.addField(_t("your_actions", language), s)
    await self.embed(data.channel_id, "", e.embed)

@HalloweenEvent(help='Shows faction statistics')
async def hstats(self, *args, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    session = self.db.sql.session()
    total = session.query(db.HalloweenClasses).filter(db.HalloweenClasses.GuildID == data.guild_id).order_by(db.HalloweenClasses.TurnCount.desc()).all()
    e = Embed()
    totalBites, totalPopulation = get_total(self, data, total)
    e.setDescription(_t("total_bites", language)+'/'+_t("total_cures", language)+f": {totalBites}\n"+'\n'.join('{}: {}'.format(_t(i.lower().replace(' ','_'), language, count=totalPopulation[i]).title(), totalPopulation[i]) for i in totalPopulation))
    await self.embed(data.channel_id, "", e.embed)

@HalloweenEvent(help='Shows current cooldowns')
async def cooldown(self, *args, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    s = self.db.sql.session()
    self_user = get_user(data.guild_id, data.author.id, s)
    elapsed = get_elapsed(self_user)
    if self_user.CurrentClass in HUNTERS:
        cooldown = COOLDOWNS['cure'] - elapsed
        action_cooldown = get_action_cooldown_left(self_user)
        if cooldown.total_seconds() <= 0:
            cooldown = _t("ready", language)
        if action_cooldown.total_seconds() <= 0:
            action_cooldown = _t("ready", language)
        return await self.message(data.channel_id, _t("remaining_cooldowns", language, cooldown=cooldown, action=action_cooldown))
    elif self_user.CurrentClass in MONSTERS:
        cooldown = COOLDOWNS["bite"] + calc_cooldown_var(s, data, self_user)
        cooldown = cooldown - elapsed
        if cooldown.total_seconds() <= 0:
            return await self.message(data.channel_id, _t("cooldown_finished", language))
        await self.message(data.channel_id, _t("remaining_cooldown", language, cooldown=cooldown))
    
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
            t = _t("Profession", language)
        else:
            t = _t("Race", language)
        r = self_user.CurrentClass.lower().replace(' ', '_')
        e.addField(t, _t(r, language, count=1).title(), True)
        bites = 0
        cures = 0
        for i in [self_user.VampireHunterStats, self_user.HuntsmanStats, self_user.ZombieSlayerStats]:
            cures += i
        for i in [self_user.WerewolfStats, self_user.VampireStats, self_user.ZombieStats]:
            bites += i
        e.addField(_t("total_bites", language), str(bites), True)
        e.addField(_t("total_cures", language), str(cures), True)
        e.addField(_t("total_turns", language), str(self_user.TurnCount), True)
        if self_user.LastAction is not None:
            e.setFooter("", _t("last_action", language)).setTimestamp(self_user.LastAction.isoformat())
        effects = ""
        if self_user.ProtectionEnds is not None and get_current_time() < self_user.ProtectionEnds:
            u = await get_usernames(self, data, self_user.ProtectedBy)
            effects += _t("effect_bite_protection", language, user=u)
        if effects != "":
            e.addField(_t("active_effects", language), effects, True)
        await self.embed(data.channel_id, "", e.embed)
