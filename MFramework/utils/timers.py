import time
from MFramework.database.alchemy import log, models, types
from MFramework import log as _log
def checkLast(self, guild, channel, user):
    j = self.cache[guild].voice[channel].pop(user)
    if j > 0:
        n = time.time()
    else:
        return 0
    return n - j

def finalize(self, guild, channel, user):
    _v = 0
    v = checkLast(self, guild, channel, user)
    if v != 0:
        session = self.db.sql.session()
        _user = models.User.fetch_or_add(session, id=user)
        stat = log.Statistic.get(session, guild, user, types.Statistic.Voice)
        stat.value += int(v)
        session.commit()
        if self.cache[guild].is_tracking(types.Flags.Activity):
            self.db.influx.commitVoiceSession(guild, channel, user, v)
    _log.debug(f'Removed {user} from {channel} after {v}')
    in_channel = self.cache[guild].voice[channel]
    if len(in_channel) == 1:
        user = list(in_channel.keys())[0]
        _log.debug(f'reStarting alone {user}')
        #finalize(self, guild, channel, user)
        _v = restartTimer(self, guild, channel, user)
    return v, (user, _v)

def startTimer(self, guild, channel, user):
    self.cache[guild].voice[channel][user] = time.time()
    _log.debug(f'Starting Timer for {user} in {channel}')

def restartTimer(self, guild, channel, user, flag=0):
    c = self.cache[guild].voice[channel]
    v = (0,0)
    if user in c:
        if c[user] > 0:
            _log.debug(f'Finalizing Previous Timer for {user} in {channel}')
            v = finalize(self, guild, channel, user)
    c[user] = flag
    _log.debug(f'reStarting Timer for {user} in {channel} with {flag}')
    return v[0]