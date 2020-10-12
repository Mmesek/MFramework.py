from MFramework.commands import register, subcommand, check_if_command
from MFramework.database import alchemy as db


@register(group='Mod', help='Role settings', alias='', category='')
async def set_role(self, role_id, command=None, *args, data, language, group, role_mentions, **kwargs):
    if not role_id.isdigit():
        if '<@' not in role_id:
            args = (command, *args)
            command = role_id
        if role_mentions != []:
            role_id = role_mentions[0]
            role_mentions = role_mentions[1:]
    else:
        role_mentions = [i for i in role_mentions if i != role_id]
    from MFramework.utils.utils import parseMention
    args = [i for i in args if parseMention(i) not in role_mentions]
    _command = await check_if_command(self, set_role, command, group, data)
    await _command(self, *args, data=data, language=language, group=group, role_id=role_id, role_mentions=role_mentions, **kwargs)

@subcommand(set_role, 'Mod')
async def level(self, reqEXP=0, reqVEXP=0, type='AND', stacked=False, *args, data, language, group, role_id, role_mentions, **kwargs):
    if type not in ['AND', 'OR', 'COMBINED']:
        type='AND'
    s = self.db.sql.session()
    role = s.query(db.LevelRoles).filter(db.LevelRoles.GuildID == int(role_id)).first()
    if role is None:
        role = db.LevelRoles(data.guild_id, Role=int(role_id))
    role.ReqEXP = int(reqEXP)
    role.ReqVEXP = int(reqVEXP)
    role.Type = type
    if role_mentions != []:
        role.ReqRoles = [int(i) for i in role_mentions]
    s.merge(role)
    s.commit()
    levels = [i for i in self.cache[data.guild_id].levels if i.Role != role.Role]
    levels.append(role)
    self.cache[data.guild_id].levels = sorted(levels, key=lambda i: i.ReqEXP+i.ReqVEXP, reverse=True)