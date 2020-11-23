import time
import MFramework.database.alchemy as db
def checkLast(self, guild, channel, user):
    j = self.cache[guild].voice[channel].pop(user)
    if j > 0:
        n = time.time()
    else:
        return 0
    return n - j
def _log(msg):
    pass
    #print(time.ctime(), msg)

def finalize(self, guild, channel, user):
    _v = 0
    v = checkLast(self, guild, channel, user)
    if v != 0:
        session = self.db.sql.session()
        l = session.query(db.UserLevels).filter(db.UserLevels.GuildID == guild).filter(db.UserLevels.UserID == user).first()
        if l == None:
            l = db.UserLevels(guild, user, 0, int(v), None)
            self.db.sql.add(l)
        else:
            l.vEXP += int(v)
        session.commit()
        if self.cache[guild].trackActivity:
            self.db.influx.commitVoiceSession(guild, channel, user, v)
    _log(f'Removed {user} from {channel} after {v}')
    in_channel = self.cache[guild].voice[channel]
    if len(in_channel) == 1:
        user = list(in_channel.keys())[0]
        _log(f'reStarting alone {user}')
        #finalize(self, guild, channel, user)
        _v = restartTimer(self, guild, channel, user)
    return v, (user, _v)

def startTimer(self, guild, channel, user):
    self.cache[guild].voice[channel][user] = time.time()
    _log(f'Starting Timer for {user} in {channel}')

def restartTimer(self, guild, channel, user, flag=0):
    c = self.cache[guild].voice[channel]
    v = (0,0)
    if user in c:
        if c[user] > 0:
            _log(f'Finalizing Previous Timer for {user} in {channel}')
            v = finalize(self, guild, channel, user)
    c[user] = flag
    _log(f'reStarting Timer for {user} in {channel} with {flag}')
    return v[0]