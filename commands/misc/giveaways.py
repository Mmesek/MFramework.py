from MFramework.utils.scheduler import scheduledTask, add_task, wait_for_scheduled_task
from MFramework.commands import register
from MFramework.utils.utils import tr

from datetime import datetime, timedelta, timezone
from MFramework.utils.utils import Embed
from MFramework.database import alchemy as db

from random import SystemRandom

@register(group='Mod', help='Duration: digits followed by s, m, h, d or w', alias='', category='')
async def giveaway(self, duration, winner_count, *prize, data, channel, language, **kwargs):
    '''Extended description to use with detailed help command'''
    channel = channel[0]
    prize = ' '.join(prize)
    winner_count = int(winner_count)
    duration = duration.split(' ')
    seconds, minutes, hours, days, weeks = 0,0,0,0,0
    for d in duration:
        if 's' in d:
            seconds = int(d.split('s')[0])
        elif 'm' in d:
            minutes = int(d.split('m')[0])
        elif 'h' in d:
            hours = int(d.split('h')[0])
        elif 'd' in d:
            days = int(d.split('d')[0])
        elif 'w' in d:
            weeks = int(d.split('w')[0])
    print(seconds, minutes, hours, days, weeks)
    finish = datetime.fromisoformat(data.timestamp) + timedelta(days=days, seconds=seconds, minutes=minutes, hours=hours, weeks=weeks)
    e = createGiveawayEmbed(language, finish, prize, winner_count)
    msg = await self.embed(channel, '', e)
    await self.create_reaction(channel, msg['id'], '🎉')
    add_task(self, data.guild_id, 'giveaway', channel, msg['id'], data.author.id, data.timestamp, finish, prize, winner_count)

def createGiveawayEmbed(l, finish, prize, winner_count, finished=False, winners='', chance=''):
    translationStrings = ['title', 'description', 'endTime']
    t = {}
    for i in translationStrings:
        translation = 'commands.giveaway.'+i
        if finished:
            translation += 'Finished'
        t[i] = tr(translation, l, prize=prize, count=winner_count, winners=winners, chance=chance)
    e = Embed().setFooter('', t['endTime']).setTimestamp(finish.isoformat()).setTitle(t['title']).setDescription(t['description'])
    return e.embed


@scheduledTask
async def giveaway(self, t):
    await wait_for_scheduled_task(self, t.TimestampEnd)
    s = self.db.sql.session()
    task = s.query(db.Tasks).filter(db.Tasks.GuildID == t.GuildID).filter(db.Tasks.Type == t.Type).filter(db.Tasks.TimestampStart == t.TimestampStart).filter(db.Tasks.Finished == False).first()
    language = self.cache[t.GuildID].language
    from MFramework.utils.utils import get_all_reactions
    users = await get_all_reactions(self, task.ChannelID, task.MessageID, '🎉')
    sample = SystemRandom().sample

    if task.WinnerCount > len(users):
        winnerCount = len(users)
    else:
        winnerCount = task.WinnerCount

    _winners = [f'<@{i.id}>' for i in sample(users, winnerCount)]
    winners = ', '.join(_winners)
    try:
        chance = '{:.3%}'.format(1 / len(users)).replace('.000', '')
    except ZeroDivisionError:
        chance = ''
    e = createGiveawayEmbed(language, task.TimestampEnd, task.Prize, winnerCount, True, winners, chance)
    await self.edit_message(task.ChannelID, task.MessageID, '', e)
    await self.message(task.ChannelID, tr("commands.giveaway.endMessage", language, count=len(_winners), winners=winners, prize=task.Prize, participants=len(users), server=task.GuildID, channel=task.ChannelID, message=task.MessageID))
    task.Finished = True
    s.commit()


@register(group='System', help='Deletes Giveaway', alias='', category='')
async def giveaway_delete(self, message_id, *args, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    task = self.cache[data.guild_id].tasks.get('giveaway', {}).get(int(message_id), None)
    if task is not None:
        task.cancel()
    s = self.db.sql.session()
    r = s.query(db.Tasks).filter(db.Tasks.GuildID == data.guild_id).filter(db.Tasks.Type == 'giveaway').filter(db.Tasks.MessageID == int(message_id)).first()
    s.delete(r)
    s.commit()
    await self.create_reaction(data.channel_id, data.id, self.emoji['success'])

@register(group='System', help='Ends Giveaway', alias='', category='')
async def giveaway_end(self, message_id, *args, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    task = self.cache[data.guild_id].tasks.get('giveaway', {}).get(int(message_id), None)
    task.cancel()
    session = self.db.sql.session()
    task = session.query(db.Tasks).filter(db.Tasks.GuildID == data.guild_id).filter(db.Tasks.Finished == False).filter(db.Tasks.MessageID == int(message_id)).first()
    task.TimestampEnd = datetime.now(tz=timezone.utc)
    await giveaway(self, task)
