from MFramework.commands import register, subcommand, check_if_command
from MFramework.database import alchemy as db

@register(group='Global', help='Sets profile', alias='', category='')
async def profile(self, command='', *args, data, language, group, **kwargs):
    '''Extended description to use with detailed help command'''
    if command != '':
        _command = await check_if_command(self, profile, command, group, data, True)
        await _command(self, *args, data=data, language=language, group=group, **kwargs)

def query_user(session, user_id):
    user = session.query(db.Users).filter(db.Users.UserID == user_id).first()
    if user is not None:
        return user
    return db.Users(user_id)

@subcommand(profile)
async def birthday(self, date, *args, data, language, **kwargs):
    s = self.db.sql.session()
    c = query_user(s, data.author.id)
    c.Birthday = date
    s.merge(c)
    s.commit()

@subcommand(profile)
async def language(self, new_language, *args, data, language, **kwargs):
    s = self.db.sql.session()
    c = query_user(s, data.author.id)
    c.Language = new_language
    s.merge(c)
    s.commit()
    self.cache.Users[data.author.id].language = new_language