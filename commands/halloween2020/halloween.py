from MFramework.database import alchemy as db
from MFramework.utils.utils import Embed
from .helpers import *
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
        _race = 'Monsters'
    elif user.CurrentClass in HUNTERS:
        _race = 'Hunters'
    else:
        _race = "Humans"
    e = Embed()
    s = {}
    for race in _HHELP:
        for h in _HHELP[race]:
            if race not in s:
                s[race] = ''
            s[race] += f'\n`{h}` - ' + _HHELP[race][h]
    for race in s:
        e.addField(race if race != 'None' else 'Global', s[race])
    await self.embed(data.channel_id, '', e.embed)
    