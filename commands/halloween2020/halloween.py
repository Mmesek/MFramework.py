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
    