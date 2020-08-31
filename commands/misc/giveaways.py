from MFramework.commands import register
from MFramework.utils.utils import tr

from datetime import datetime, timedelta, timezone
from MFramework.utils.utils import Embed
from MFramework.database import alchemy as db
import asyncio
from random import SystemRandom

@register(group='Admin', help='Duration: digits followed by s, m, h, d or w', alias='', category='')
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
    print(weeks, days, hours, minutes, seconds)
    finish = datetime.fromisoformat(data.timestamp) + timedelta(days=days, seconds=seconds, minutes=minutes, hours=hours, weeks=weeks)
    e = createGiveawayEmbed(language, finish, prize, winner_count)
    msg = await self.embed(channel, '', e)
    await self.create_reaction(channel, msg['id'], '🎉')
    s = self.db.sql.session()
    r = db.Tasks(data.guild_id, 'Giveaway', channel, msg['id'], data.author.id, data.timestamp, finish, prize, winner_count, False)
    self.db.sql.add(r)
    if 'giveaways' not in self.cache[data.guild_id].tasks:
        self.cache[data.guild_id].tasks['giveaways'] = {}
    self.cache[data.guild_id].tasks['giveaways'][int(msg['id'])] = asyncio.create_task(giveaway_end(self, finish, data.guild_id, channel, msg['id'], language, data.timestamp))

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

@register(group='System', help='Short description to use with help command', alias='', category='')
async def giveaway_delete(self, message_id, *args, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    s = self.db.sql.session()
    r = s.query(db.Tasks).filter(db.Tasks.GuildID == data.guild_id).filter(db.Tasks.Type == 'Giveaway').filter(db.Tasks.MessageID == int(message_id)).first()
    s.delete(r)
    s.commit()
    await self.create_reaction(data.channel_id, data.id, self.emoji['success'])

@register(group='System', help='Short description to use with help command', alias='', category='')
async def giveaway_end_now(self, message_id, *args, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    task = self.cache[data.guild_id].tasks.get('giveaways', {}).get(int(message_id), None)
    task.cancel()
    session = self.db.sql.session()
    task = session.query(db.Tasks).filter(db.Tasks.GuildID == data.guild_id).filter(db.Tasks.Finished == False).filter(db.Tasks.MessageID == int(message_id)).first()
    await giveaway_end(self, datetime.now(tz=timezone.utc), data.guild_id, task.ChannelID, task.MessageID, self.cache[data.guild_id].language, task.TimestampStart)

async def giveaway_end(self, finish, guild_id, channel_id, msg_id, language, start):
    s = (finish - datetime.now(tz=timezone.utc)).total_seconds()
    if s > 0:
        await asyncio.sleep(s)
    s = self.db.sql.session()
    r = s.query(db.Tasks).filter(db.Tasks.GuildID == guild_id).filter(db.Tasks.Type == 'Giveaway').filter(db.Tasks.TimestampStart == start).filter(db.Tasks.Finished == False).first()  #filter(db.Giveaways.ChannelID == channel_id).filter(db.Giveaways.MessageID == msg_id).first()
    if r.Finished == True:
        return
    msg = await self.get_channel_message(channel_id, msg_id)
    for reaction in msg.reactions:
        if reaction.emoji.name == '🎉':
            count = reaction.count
    users = []
    last_id = None
    for chunk in range(int(count / 100) + (count % 100 > 0)):
        users += await self.getreactions(channel_id, msg_id, '🎉', when="after", snowflake=last_id)
        last_id = users[-1].id
    users = [i for i in users if i.id != self.user_id]
    users = list(set(users))
    sample = SystemRandom().sample
    if r.WinnerCount > len(users):
        r.WinnerCount = len(users)
    _winners = [f'<@{i.id}>' for i in sample(users, r.WinnerCount)]
    winners = ', '.join(_winners)
    try:
        chance = '{:.3%}'.format(1 / len(users)).replace('.000', '')
    except ZeroDivisionError:
        chance = ''
    e = createGiveawayEmbed(language, finish, r.Prize, r.WinnerCount, True, winners, chance)
    await self.edit_message(channel_id, msg_id, '', e)
    await self.message(channel_id, tr("commands.giveaway.endMessage", language, count=len(_winners), winners=winners, prize=r.Prize, participants=len(users), server=guild_id, channel=channel_id, message=msg_id))
    r.Finished = True
    s.commit()
