from MFramework import register, Groups, ChannelID, Snowflake, Embed

from datetime import datetime, timezone
from MFramework.bot import Context
from MFramework.utils.utils import replaceMultiple, total_seconds
from mlib.localization import tr
from mlib.random import chance, pick
from MFramework.utils.scheduler import scheduledTask, add_task, wait_for_scheduled_task
import MFramework.database.alchemy.models as db

@register()
async def giveaway(ctx: Context, *args, language, **kwargs):
    '''Giveaways'''
    pass

@register(group=Groups.MODERATOR, main=giveaway)
async def create(ctx: Context, prize: str, duration: str = '1h', description: str=None, winner_count: int=1, reactions: str = '🎉', channel: ChannelID=None, hidden:bool=False, *args, language, **kwargs):
    '''Create new giveaway
    Params
    ------
    prize:
        Giveaway's prize
    duration:
        Digits followed by either s, m, h, d or w. For example: 1d 12h 30m 45s
    description: 
        [Optional] Description of the giveaway
    winner_count:
        Amount of winners, default 1
    reactions:
        Whether it should use different emoji than 🎉 or multiple (Separate using ,)
    channel:
        Channel in which giveaway should be created
    hidden:
        Whether reactions should be removed
    '''
    finish = datetime.now() + total_seconds(duration)
    msg = await ctx.bot.create_message(channel, embed=createGiveawayEmbed(language, finish, prize, winner_count, custom_description=description))
    for reaction in reactions.split(','):
        await msg.react(replaceMultiple(reaction.strip(), ['<:',':>', '>'],''))
    ctx.cache.giveaway_messages.append(msg.id)
    add_task(ctx, ctx.guild_id, 'giveaway' if not hidden else 'hidden_giveaway', channel, msg.id, ctx.member.user.id, datetime.now(), finish, prize, winner_count)
    await ctx.reply("Created", private=True)

@register(group=Groups.MODERATOR, main=giveaway)
async def delete(ctx: Context, message_id: Snowflake, *args, language, **kwargs):
    '''
    Deletes Giveaway
    Params
    ------
    message_id:
        ID of giveaway message to delete
    '''
    task = ctx.cache.tasks.get('giveaway', {}).get(int(message_id), None)
    if task is not None:
        task.cancel()
    s = ctx.db.sql.session()
    r = s.query(db.Tasks).filter(db.Tasks.server_id == ctx.guild_id).filter(db.Tasks.type == 'giveaway').filter(db.Tasks.message_id == int(message_id)).first()
    s.delete(r)
    s.commit()
    await ctx.reply("Giveaway deleted Successfully", private=True)

@register(group=Groups.MODERATOR, main=giveaway)
async def end(ctx: Context, message_id: Snowflake, *args, language, **kwargs):
    '''
    Ends Giveaway
    Params
    ------
    message_id:
        ID of giveaway message to finish
    '''
    task = ctx.cache.tasks.get('giveaway', {}).get(int(message_id), None)
    task.cancel()
    s = ctx.db.sql.session()
    task = s.query(db.Tasks).filter(db.Tasks.server_id == ctx.guild_id).filter(db.Tasks.finished == False).filter(db.Tasks.message_id == int(message_id)).first()
    task.TimestampEnd = datetime.now(tz=timezone.utc)
    await giveaway(ctx, task)
    await ctx.reply("Giveaway ended Successfully")

@register(group=Groups.MODERATOR, main=giveaway)
async def reroll(ctx: Context, message_id: Snowflake, amount: int=0, *args, language, **kwargs):
    '''
    Rerolls giveaway
    Params
    ------
    message_id:
        ID of giveaway message to reroll
    amount:
        Amount of rewards to reroll, defaults to all
    '''
    s = ctx.db.sql.session()
    task = s.query(db.Tasks).filter(db.Tasks.server_id == ctx.guild_id).filter(db.Tasks.type == 'giveaway').filter(db.Tasks.message_id == message_id).first()
    from MFramework.utils.utils import get_all_reactions
    users = await get_all_reactions(ctx, task.channel_id, task.message_id, '🎉')
    winners = [f'<@{i}>' for i in pick([i.id for i in users], amount)]
    winners = ', '.join(winners)
    await ctx.create_message(task.ChannelID, 
        tr("commands.giveaway.rerollMessage", 
            language, 
            count=len(winners.split(',')), 
            winners=winners, 
            prize=task.Prize, 
            participants=len(users), 
            server=task.GuildID, 
            channel=task.ChannelID, 
            message=task.MessageID
        )
    )
    await ctx.reply("Giveaway rerolled Successfully")

def createGiveawayEmbed(l, finish, prize, winner_count, finished=False, winners='', chance='', custom_description=None):
    translationStrings = ['title', 'description', 'endTime']
    t = {}
    for i in translationStrings:
        translation = 'commands.giveaway.'+i
        if finished:
            translation += 'Finished'
        if i == 'description' and custom_description:
            t[i] = custom_description
        else:
            t[i] = tr(translation, l, prize=prize, count=winner_count, winners=winners, chance=chance)
    return Embed().setFooter(text=t['endTime']).setTimestamp(finish.isoformat()).setTitle(t['title']).setDescription(t['description'])

@scheduledTask
async def giveaway(ctx: Context, t):
    await wait_for_scheduled_task(ctx, t.end)
    s = ctx.db.sql.session()
    task = s.query(db.Tasks).filter(db.Tasks.server_id == t.server_id).filter(db.Tasks.type == t.type).filter(db.Tasks.timestamp == t.timestamp).filter(db.Tasks.finished == False).first()
    language = ctx.cache[t.GuildID].language
    if 'hidden' not in task.Type:
        from MFramework.utils.utils import get_all_reactions
        users = await get_all_reactions(ctx, task.channel_id, task.message_id, '🎉')
    else:
        users = [] # FIXME?
        #users = s.query(db.GiveawayParticipants).filter(db.GiveawayParticipants.server_id == t.server_id, db.GiveawayParticipants.message_id == task.message_id, db.GiveawayParticipants.Reaction == 'Rune_Fehu:817360053651767335').all()
    winners = [f'<@{i}>' for i in pick([i.user_id if "hidden" in task.type else i.id for i in users], task.WinnerCount)]
    winnerCount = len(winners)
    winners = ', '.join(winners)

    e = createGiveawayEmbed(language, task.timestamp_end, task.prize, winnerCount, True, winners, chance(len(users)))
    await ctx.bot.edit_message(task.channel_id, task.message_id, None, e, None, None)
    await ctx.bot.create_message(task.channel_id, 
        tr("commands.giveaway.endMessage", language, count=winnerCount, winners=winners, prize=task.Prize, participants=len(users), server=task.GuildID, channel=task.ChannelID, message=task.MessageID)
    )
    task.Finished = True
    s.commit()

@scheduledTask
async def hidden_giveaway(ctx: Context, t):
    await giveaway(ctx, t)