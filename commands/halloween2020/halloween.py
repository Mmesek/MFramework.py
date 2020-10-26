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
        race = 'Monsters'
    elif user.CurrentClass in HUNTERS:
        race = 'Hunters'
    else:
        race = "Humans"
    e = Embed().setTitle("Rules").setDescription("- Monsters can bite any non monster that is not hunting them.\nVampire can bite Human, Huntsman and Zombie Slayer but not Vampire Hunter.\n\n- Hunters can only cure what they hunt.\nVampire Hunter can only cure Vampires")
    e.addField("Drinking or Enlisting", "- You can choose your `drink` only if you weren't bitten/enlisted before. Otherwise you can only drink random drink.\n\n- You can `enlist` only while being Human unless there is no hunter in profession you want to enlist to.")
    e.addField("Last of the Kind", "You can't bite/cure someone if turning them means the group will have 0 members")
    e.addField("Joining game", "To begin, if you weren't bitten by someone already, either `drink` to become a Monster or `enlist` to join Hunters")
    e.addField("Command Arguments", "[Optional argument]")
    s = {}
    def iterate(race):
        s = ''
        for h in _HHELP[race]:
            if _HHELP[race][h]['msg'] == '':
                continue
            s += '\n`'+h+'` ' + _HHELP[race][h]['sig'] + ' - ' + _HHELP[race][h]['msg']
            if _HHELP[race][h]['alias'] != '':
                s+=' - Aliases: `'+ _HHELP[race][h]['alias'] + '`'
        return s
    s[race] = iterate(race)
    s['Global'] = iterate('None')
    for race in s:
        e.addField(race if race != 'None' else 'Global', s[race])
    await self.embed(data.channel_id, '', e.embed)
    