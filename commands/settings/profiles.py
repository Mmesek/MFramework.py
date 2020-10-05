from MFramework.commands import register, subcommand, check_if_command
from MFramework.database import alchemy as db
from MFramework.utils.utils import Embed, get_avatar, secondsToText, created, tr
@register(group='Global', help='Sets profile', alias='', category='')
async def profile(self, command='', *args, data, language, group, **kwargs):
    '''Extended description to use with detailed help command'''
    if command != '':
        _command = await check_if_command(self, profile, command, group, data, True)
        await _command(self, *args, data=data, language=language, group=group, **kwargs)
    else:
        await show_profile(self, data=data, language=language)

from datetime import datetime
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
    dates = "Discord: {discord}\nServer: {server}".format(discord=created(data.author.id).strftime('%Y-%m-%d %H:%M:%S'), server=datetime.fromisoformat(data.member.joined_at).strftime('%Y-%m-%d %H:%M:%S'))
    if data.member.premium_since:
        dates += '\nBooster: {boost}'.format(boost=datetime.fromisoformat(data.member.premium_since).strftime('%Y-%m-%d %H:%M:%S'))
    e.addField("Joined", dates, True)
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
    import pycountry
    try:
        new_language = pycountry.languages.lookup(new_language).alpha_2
    except LookupError:
        return await self.message(data.channel, f"Couldn't find language {new_language}")
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
    
@subcommand(profile)
async def timezone(self, timezone, *args, data, language, **kwargs):
    s = self.db.sql.session()
    c = query_user(s, data.author.id)
    import pytz
    timezone = timezone.lower().replace('utc', 'Etc/GMT').replace('gmt', 'Etc/GMT')
    if any(timezone.lower() == i.lower() for i in pytz.all_timezones):
        c.Timezone = timezone.replace('+','MINUS').replace('-','PLUS').replace('MINUS','-').replace('PLUS','+')
    else:
        return await self.message(data.channel_id, tr('commands.timezone.timezoneNotFound', language, from_timezone=timezone))#f"Couldn't find Timezone {timezone}.")
    s.merge(c)
    s.commit()

@subcommand(profile)
async def region(self, region, *args, data, language, **kwargs):
    s = self.db.sql.session()
    c = query_user(s, data.author.id)
    import pycountry
    try:
        region = pycountry.countries.search_fuzzy(region)[0].alpha_2
    except LookupError:
        return await self.message(data.channel, f"Couldn't find region {region}")
    c.Region = region
    s.merge(c)
    s.commit()