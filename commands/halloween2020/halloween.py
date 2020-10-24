from MFramework.database import alchemy as db

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
