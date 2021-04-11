import time
import inspect

def log(msg=""):
    try:
        func = inspect.stack()[1].function
        with open('data/log.log', 'a') as logf:
            logf.write(
                str(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())) + f': [Ex@{func}] {msg}\n')
        return
    except IOError:
        with open('data/log.log', 'a+') as logf:
            logf.write(str(time.strftime("%Y-%m-%d %H:%M:%S",
                                         time.gmtime())) + f': Created log file.\n')
    except Exception as ex:
        with open('data/log.log', 'a') as logf:
            logf.write(str(time.strftime("%Y-%m-%d %H:%M:%S",
                                         time.gmtime())) + f': Exception with log: {ex}\n')
        return
    return

from mlib.utils import replaceMultiple
def parseMention(message: str) -> str:
    return replaceMultiple(message, ['<:', '@!', '#', '&', '<', ':>', '>', '@'], '')

def param(message: str) -> list:
    return replaceMultiple(message, ['<:', '@!', '#', '&', '<', ':>', '>', '@'], '').split(' ')[1:]

async def get_usernames(self, guild_id: int, user_id: int) -> str:
    try:
        u = self.cache[guild_id].members[user_id].user.username
    except:
        try:
            u = await self.get_guild_member(guild_id, user_id)
        except:
            return None
        self.cache[guild_id].members[user_id] = u
        u = u.user.username
    return u

from datetime import timedelta
def total_seconds(duration: str) -> timedelta:
    total = timedelta()
    for d in duration.split(' '):
        if 's' in d:
            total += timedelta(seconds=int(d.split('s')[0]))
        elif 'm' in d:
            total += timedelta(minutes=int(d.split('m')[0]))
        elif 'h' in d:
            total += timedelta(hours=int(d.split('h')[0]))
        elif 'd' in d:
            total += timedelta(days=int(d.split('d')[0]))
        elif 'w' in d:
            total += timedelta(weeks=int(d.split('w')[0]))
    return total

def check_attachments(self, msg, embed=None):
    if len(msg.attachments) == 0:
        return embed
    from mlib.localization import tr
    if embed is None:
        from MFramework import Embed
        embed = Embed()
    embed.setImage(msg.attachments[0].url)
    if msg.attachments[0].url[-3:] not in ['png', 'jpg', 'jpeg', 'webp', 'gif'] or len(msg.attachments) > 1:
        filename = '\n'.join([f"[{i.filename}]({i.url})" for i in msg.attachments])
        embed.addFields(tr("commands.dm.attachments", self.bot.cache[self.guild_id].language), filename, True)
        #"Attachments"filename = ''
    else:
        embed.addField("Image", msg.attachments[0].filename, True)
    return embed
