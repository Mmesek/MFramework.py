from MFramework.commands import register, subcommand, check_if_command
from MFramework.database import alchemy as db
from MFramework.utils.utils import Embed, get_avatar, secondsToText
@register(group='Global', help='Sets profile', alias='', category='')
async def profile(self, command='', *args, data, language, group, **kwargs):
    '''Extended description to use with detailed help command'''
    if command != '':
        _command = await check_if_command(self, profile, command, group, data, True)
        await _command(self, *args, data=data, language=language, group=group, **kwargs)
    else:
        await show_profile(self, data=data, language=language)

async def show_profile(self, *args, data, language, **kwargs):
    e = Embed().setAuthor(data.author.username, None, get_avatar(data.author))
    s = self.db.sql.session()
    u = query_user(s, data.author.id)
    if u.Language is not None:
        e.addField("Language", u.Language, True)
    if u.Birthday is not None:
        e.addField("Birthday", u.Birthday.strftime("%A, %B\n%d/%m/%Y"), True)
    if len(e.fields) == 2:
        e.addField("\u200b", "\u200b", True)
    total_exp = 0
    total_vexp = 0
    exp = s.query(db.UserLevels).filter(db.UserLevels.UserID == data.author.id).all()
    for server_exp in exp:
        total_exp += server_exp.EXP
        total_vexp += server_exp.vEXP
    if total_exp != 0:
        e.addField("Total EXP", total_exp, True)
    if total_vexp != 0:
        e.addField("Total Voice Time", secondsToText(total_vexp, language.upper()), True)
    if u.Color is not None:
        e.setColor(u.Color)
    await self.embed(data.channel_id, "", e.embed)


def query_user(session, user_id):
    user = session.query(db.Users).filter(db.Users.UserID == user_id).first()
    if user is not None:
        return user
    return db.Users(user_id)

@subcommand(profile)
async def birthday(self, year=1, month=1, day=1, *args, data, language, **kwargs):
    s = self.db.sql.session()
    c = query_user(s, data.author.id)
    from datetime import date
    c.Birthday = date(int(year), int(month), int(day))
    s.merge(c)
    s.commit()

@subcommand(profile)
async def language(self, new_language, *args, data, language, **kwargs):
    s = self.db.sql.session()
    c = query_user(s, data.author.id)
    c.Language = new_language
    s.merge(c)
    s.commit()
    #self.cache.Users[data.author.id].language = new_language

@subcommand(profile)
async def color(self, hex_color, *args, data, language, **kwargs):
    s = self.db.sql.session()
    c = query_user(s, data.author.id)
    c.Color = int(hex_color.strip('#'), 16)
    s.merge(c)
    s.commit()
    