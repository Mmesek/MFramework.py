async def handle_roles(self, data, l, levelRole, x, user_id):
    await self.add_guild_member_role(data.guild_id, user_id, levelRole.Role, "EXP Role")
    try:
        previous_role = l[x+1]
    except:
        return
    if not previous_role.Stacked and previous_role.Role in data.member.roles:
        await self.remove_guild_member_role(data.guild_id, user_id, previous_role.Role, "EXP Role")

async def handle_exp(self, data, e=None):
    if e is None:
        user_id = data.user_id
        from ..database import alchemy as db
        session = self.db.sql.session()
        e = session.query(db.UserLevels).filter(db.UserLevels.GuildID == data.guild_id).filter(db.UserLevels.UserID == user_id).first()
    else:
        user_id = data.author.id
    l = self.cache[data.guild_id].levels
    if l == []:
        return
    for x, levelRole in enumerate(l):
        if levelRole.Role not in data.member.roles:
            if levelRole.ReqRoles is not None and not all(i in data.member.roles for i in levelRole.ReqRoles):
                continue
            if levelRole.Type == 'AND' and (e.EXP >= levelRole.ReqEXP and e.vEXP >= levelRole.ReqVEXP):
                await handle_roles(self, data, l, levelRole, x, user_id)
            elif levelRole.Type == 'OR' and (e.EXP >= levelRole.ReqEXP or e.vEXP >= levelRole.ReqVEXP):
                await handle_roles(self, data, l, levelRole, x, user_id)
            elif levelRole.Type == 'COMBINED' and ((e.EXP + e.vEXP) >= (levelRole.ReqEXP + levelRole.ReqVEXP)):
                await handle_roles(self, data, l, levelRole, x, user_id)
            else:
                continue
            break
        else:
            break