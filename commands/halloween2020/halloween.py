from MFramework.database import alchemy as db
from MFramework.utils.utils import Embed
from .helpers import *
from .helpers.utils import _translate, _t
@HalloweenEvent(group="System")
async def halloween_createRoles(self, *args, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    s = self.db.sql.session()
    for name in ROLES:
        role = await self.create_guild_role(data.guild_id, _t(name.lower().replace(' ','_'), language, count=1).title(), 0, None, False, False, "Created Role for Halloween Minigame")
        s.merge(db.HalloweenRoles(data.guild_id, role.name, role.id))
    s.commit()

@HalloweenEvent(group="System")
async def halloween_addRoles(self, *args, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    s = self.db.sql.session()
    roles = get_roles(data.guild_id, s)
    users = s.query(db.HalloweenClasses).filter(db.HalloweenClasses.GuildID == data.guild_id).all()
    for user in users:
        await self.add_guild_member_role(data.guild_id, user.UserID, roles.get(user.CurrentClass, ""), "Halloween Minigame")

@HalloweenEvent(help="Shows Halloween commands help")
async def hhelp(self, *args, data, language, **kwargs):
    from .helpers.constants import _HHELP
    s = self.db.sql.session()
    user = get_user(data.guild_id, data.author.id, s)
    if user.CurrentClass in MONSTERS:
        race = 'Monsters'
    elif user.CurrentClass in HUNTERS:
        race = 'Hunters'
    else:
        race = "Humans"
    rules_main = [_t('rules_main_monsters', language), _t('rules_main_hunters', language)]
    e = Embed().setTitle(_t('rules_title', language)).setDescription('\n\n'.join(rules_main))
    rules_drinking = [_t('rules_drinking', language, drink_cmd=_t('cmd_drink', language), enlist_cmd=_t('cmd_enlist', language), drink_nightmare=_t('drink_nightmare', language)), _t('rules_enlisting', language, drink_cmd=_t('cmd_drink', language), enlist_cmd=_t('cmd_enlist', language))]
    e.addField(_t('rules_drinking_title', language), '\n\n'.join(rules_drinking))
    e.addField(_t('rules_last_protection_title', language), _t('rules_last_protection', language))
    e.addField(_t('rules_joining_title', language), _t('rules_joining', language, drink_cmd=_t('cmd_drink', language), enlist_cmd=_t('cmd_enlist', language)))
    e.addField(_t('rules_command_args_title', language), _t('rules_command_args', language))
    s = {}
    def iterate(race):
        s = ''
        for h in _HHELP[race]:
            _m = _translate('help_', language, h, _HHELP[race][h]['msg'])
            if _m == '':
                continue
            _h = _translate('cmd_', language, h, h)
            s += '\n`' + _h + '` ' + _HHELP[race][h]['sig'] + ' - ' + _m
            _a = _translate('alias_', language, h, _HHELP[race][h]['alias'])
            if _a != '':
                s+=' - Aliases: `'+ _a + '`'
        return s
    s[race] = iterate(race)
    s['Global'] = iterate('None')
    for race in s:
        r = _t('race_'+race.lower(), language)
        e.addField(r, s[race])
    await self.embed(data.channel_id, '', e.embed)

@register(group='System', help='Shows Halloween 2020 statistics graph', alias='', category='')
async def hsummary(self, *args, data, resample='D', locator='Day', interval=1, growth=False, language, **kwargs):
    '''Extended description to use with detailed help command'''
    from datetime import date, datetime, timezone
    import MFramework.utils.graphing as graph
    await self.trigger_typing_indicator(data.channel_id)

    _s = self.db.sql.session()
    history = _s.query(db.HalloweenLog).filter(db.HalloweenLog.GuildID == data.guild_id).order_by(db.HalloweenLog.Timestamp.asc()).all()
    _total = _s.query(db.HalloweenClasses).filter(db.HalloweenClasses.GuildID == data.guild_id).order_by(db.HalloweenClasses.TurnCount.desc()).all()
    e = Embed().setTitle("Thanks for participating!")
    totalBites, totalPopulation = get_total(self, data, _total)
    totalPopulation = sorted(totalPopulation.items(), key=lambda i: i[1], reverse=True)
    totalPopulation = {i[0]: i[1] for i in totalPopulation}
    e.setDescription(_t("total_bites", language) + '/' + _t("total_cures", language) + f": {totalBites}\n" + '\n'.join('{}: {}'.format(_t(i.lower().replace(' ', '_'), language, count=totalPopulation[i]).title(), totalPopulation[i]) for i in totalPopulation))
    total = {}
    _counts = {}
    _first = {}
    y = []
    x = []
    for entry in history:
        if entry.ToClass not in total:
            total[entry.ToClass] = {'x': [], 'y': []}
        if entry.FromClass not in total:
            total[entry.FromClass] = {'x':[],'y':[]}
        if entry.ToClass not in _counts:
            _counts[entry.ToClass] = 0
        if entry.FromClass not in _counts:
            _counts[entry.FromClass] = 0

        _counts[entry.FromClass] -= 1
        if entry.FromClass not in _first:
            _first[entry.FromClass] = False
        _counts[entry.ToClass] += 1
        if entry.ToClass not in _first:
            _first[entry.ToClass] = True
        
        total[entry.FromClass]['x'].append(entry.Timestamp)
        total[entry.FromClass]['y'].append(_counts[entry.FromClass])
        total[entry.ToClass]['x'].append(entry.Timestamp)
        total[entry.ToClass]['y'].append(_counts[entry.ToClass])

    for i in total:
        if total[i] == {}:
            continue
        m = min(total[i]['y'])
        if m < 0:
            n_list = []
            for j in total[i]['y']:
                n_list.append(j + abs(m))
            total[i]['y'] = n_list
        d = totalPopulation[i] - total[i]['y'][-1]
        if total[i]['y'][-1] < totalPopulation[i]:
            n_list = []
            for j in total[i]['y']:
                n_list.append(j + d)
            total[i]['y'] = [d] + n_list
            total[i]['x'] = [datetime(2020, 10, 17, tzinfo=timezone.utc)] + total[i]['x']
    for i in total:
        if total[i] != {}:
            total[i]['y'] = [0] + total[i]['y']
            total[i]['x'] = [datetime(2020, 10, 16, tzinfo=timezone.utc)] + total[i]['x']
    total['Human'] = {}

    img_str = graph.plot(total, resample, growth, locator, interval)
    file_name = f"growth-{date.today()}.png"
    e.setImage("attachment://"+file_name).setColor(16744206)
    await self.withFile(data.channel_id, img_str, file_name, "", e.embed)
