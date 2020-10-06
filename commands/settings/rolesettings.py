from MFramework.commands import register, subcommand, check_if_command
from MFramework.database import alchemy as db


@register(group='Mod', help='Role settings', alias='', category='')
async def set_role(self, role_id, command=None, *args, data, language, group, **kwargs):
    if not role_id.isdigit():
        args = (command, *args)
        command = role_id
    _command = await check_if_command(self, set_role, command, group, data)
    await _command(self, *args, data=data, language=language, group=group, role_id=role_id, **kwargs)

@subcommand(set_role, 'Mod')
async def level(self, reqEXP=0, reqVEXP=0, type='AND', stacked=False, *args, data, language, group, role_id, **kwargs):
    s = self.db.sql.session()
    role = s.query(db.LevelRoles).filter(db.LevelRoles.GuildID == int(role_id)).first()
    if role is None:
        role = db.LevelRoles(data.guild_id, Role=int(role_id))
    role.ReqEXP = int(reqEXP)
    role.ReqVEXP = int(reqVEXP)
    role.Type = type
    s.merge(role)
    s.commit()
    self.cache[data.guild_id].levels = [i for i in self.cache[data.guild_id].levels if i.Role != role.Role]
    self.cache[data.guild_id].levels.append(role)