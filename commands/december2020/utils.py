from MFramework.commands import register
from MFramework.database import alchemy as db

from MFramework.utils.utils import tr, parseMention
from datetime import datetime

_CHELP = []

def DecemberEvent(cmd='', help='', alias='', group='Global', hijak=None, **kwargs):
    def inner(f, *arg, **kwarg):
        if datetime.today().month != 12:
            return
        _CHELP.append(f.__name__)
        n = _translate('cmd_', 'en', cmd, '0')
        if n != '0':
            kwargs['cmd_trigger'] = 'events.december.cmd_' + cmd
            kwargs['localized_aliases'] = 'events.december.alias_' + cmd
        register(alias=alias, group=group, **kwargs)(f)
        return f
    return inner

def _t(key, language='en', **kwargs):
    return tr("events.december." + key, language, **kwargs)
    
def _translate(_key, _language, name, default=''):
    n = _t(_key+name, language=_language)
    if n == _language + '.events.december.' + _key + name:
        return default
    return n

def get_user_id(user) -> int:
    return int(parseMention(user[0]))

def get_inventory(s, userID):
    inventory = s.query(db.User).filter(db.User.id == userID).first()
    if inventory is None:
        inventory = db.User(userID)
        s.add(inventory)
        s.commit()
    return inventory