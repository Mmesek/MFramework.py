from MFramework import register, Groups, Context, UserID, User, Embed
#/infraction 
#  | | |---- InfractionType
#  | |           |--------- [User] [reason] [duration]
#  | |------ list           [User]
#  |-------- counter
#                |--------- [User] increase [reason]
#                |--------- [User] decrease [reason]
from MFramework.database.alchemy import types
#TODO:
# Each infraction as separate command instead of choice type?
# Action on infraction like ban or kick
# move everything to infraction command group?
# or make infraction list an info subcommand or some other?
# Perhaps alias interaction?
# List recently joined users and provide filter/sorter
@register(group=Groups.MODERATOR)
async def infraction(ctx: Context, type: types.Infraction, user: User=None, reason:str="", duration:str=None, increase_counter: bool=True, *, language):
    '''Base command for infractions
    Params
    ------
    type:
        Type of Infraction
    user:
        User to take action upon
    reason:
        Reason of action
    duration:
        [Optional] Digits followed by either s, m, h, d or w. For example: 1d 12h 30m 45s
    increase_counter:
        Whether this infraction should increase currently active infractions
    '''
    await ctx.deferred()
    if duration:
        from mlib.converters import total_seconds
        duration = total_seconds(duration)

    session = ctx.db.sql.session()
    from MFramework.database.alchemy import models
    u = models.User.fetch_or_add(session, id=user.id)
    u.add_infraction(server_id=ctx.guild_id, moderator_id=ctx.user.id, type=type.name, reason=reason, duration=duration)

    await ctx.reply(f"{user.username} has been {type.name.replace('_',' ').lower()+('ed' if not type.name.endswith('e') else 'd')} for {reason}")

    _ = ctx.cache.logging.get("infraction", None)
    if _:
        await _(
            guild_id=ctx.guild_id, 
            moderator=ctx.user,
            user_id=user,
            reason=reason,
            duration=duration,
            type=type
        )
        if ctx.bot.user_id:
            r = await _.log_dm(
                type=type, 
                guild_id=ctx.guild_id,
                user_id=user,
                reason=reason,
                duration= duration
            )
            if not r:
                await ctx.send("Couldn't deliver DM message")
    
    if (ctx.bot.emoji.get('fake_infraction', '😜') not in reason or type not in {types.Infraction.Unban, types.Infraction.Unmute, types.Infraction.DM_Unmute, types.Infraction.Report}) and increase_counter:
        await auto_moderation(ctx, session, user, type)

async def auto_moderation(ctx: Context, session, user: User, type: types.Infraction, increase_counters: bool=True):
    from MFramework.database.alchemy import log, types
    if increase_counters:
        log.Statistic.increment(session, ctx.guild_id, user.id, types.Statistic.Infractions_Active)
        log.Statistic.increment(session, ctx.guild_id, user.id, types.Statistic.Infractions_Total)
    active = log.Statistic.get(session, ctx.guild_id, user.id, types.Statistic.Infractions_Active)
    automute = ctx.cache.settings.get(types.Setting.Auto_Mute_Infractions, None)
    autoban = ctx.cache.settings.get(types.Setting.Auto_Ban_Infractions, None)
    if automute and active.value == automute and type is not types.Infraction.Mute:
        MUTED_ROLE = ctx.cache.groups.get(Groups.MUTED, [None])[0]
        if MUTED_ROLE:
            await ctx.bot.add_guild_member_role(ctx.guild_id, user.id, MUTED_ROLE, reason=f"{active.value} active infractions")
            await infraction(ctx, types.Infraction.Mute, user, reason=f"{active.value} active infractions", duration=ctx.cache.settings.get(types.Setting.Auto_Mute_Duration, '12h'), increase_counter=False)
    elif autoban and active.value >= autoban and type is not types.Infraction.Ban:
        await ctx.bot.create_guild_ban(ctx.guild_id, user.id, reason=f"{active.value} active infractions")
        await infraction(ctx, types.Infraction.Ban, user, reason=f"{active.value} active infractions", increase_counter=False)


@register(group=Groups.GLOBAL)
async def infractions(ctx: Context, user: User=None, *, language):
    '''Lists user's infractions'''
    await ctx.deferred()
    session = ctx.db.sql.session()
    from MFramework.database.alchemy.models import Infraction
    _infractions = session.query(Infraction)
    if not False:#show_all:
        _infractions = _infractions.filter(Infraction.server_id == ctx.guild_id)
    _infractions = _infractions.filter(Infraction.user_id == user.id).all()
    _infractions.reverse()
    width = 0
    active = 0
    from mlib.localization import tr, secondsToText
    user_infractions = []
    from collections import namedtuple
    Row = namedtuple("Row", ['timestamp', 'type', 'reason', 'moderator_id', 'duration', 'active'])
    for infraction in _infractions:
        translated = tr(f"commands.infractions.types.{infraction.type.name}", language)
        if len(translated) > width:
            width = len(translated)
        user_infractions.append(
            Row(
                timestamp=int(infraction.timestamp.timestamp()),
                type=translated,
                reason=infraction.reason,
                moderator_id=infraction.moderator_id,
                duration=tr("commands.infractions.for_duration", language, 
                        duration=secondsToText(int(infraction.duration.total_seconds()), language)) 
                        if infraction.duration else "",
                active=tr("commands.infractions.active", language) 
                        if infraction.active else tr("commands.infractions.inactive", language)
            )
        )
        if infraction.active:
            active+=1
    str_infractions = '\n'.join(tr("commands.infractions.row", language, width=width, **i._asdict()).format(type=i.type).strip() for i in user_infractions[:10])
    if str_infractions != "":
        from mlib.colors import get_main_color
        e = Embed()
        e.setDescription(str_infractions).setAuthor(tr("commands.infractions.title", language, username=user.username), icon_url=user.get_avatar()).setColor(get_main_color(user.get_avatar()))
        a = active#log.Statistic.get(session, ctx.guild_id, user.id, types.Statistic.Infractions_Active)
        t = len(user_infractions)#log.Statistic.get(session, ctx.guild_id, user.id, types.Statistic.Infractions_Total)
        total = ctx.cache.settings.get(types.Setting.Auto_Ban_Infractions, 5)
        danger = ctx.cache.settings.get(types.Setting.Auto_Mute_Infractions, 3)
        currently_active = ["🔴"] * a#.value
        remaining_to_auto_mute = (danger-a)#.value)
        if remaining_to_auto_mute > 0:
            currently_active += ["🟢"] * remaining_to_auto_mute
        remaining_to_auto_ban = (total-a)#.value)
        if remaining_to_auto_mute > 0:
            remaining_to_auto_ban -= remaining_to_auto_mute
        if remaining_to_auto_ban > 0:
            currently_active += ["🟡"] * remaining_to_auto_ban
        e.setFooter(tr("commands.infractions.counter", language, currently_active="-".join(currently_active), active=a, total=t))
        return await ctx.reply(embeds=[e])
    return await ctx.reply(tr("commands.infractions.no_infractions", language))

@register(group=Groups.MODERATOR)
async def counter(ctx: Context, type: str, user: User, number: int=1, reason: str=None, affect_total: bool=False):
    '''
    Manages infraction counter
    Params
    ------
    type:
        Whether to increase or decrease currently active infractions
        Choices:
            Increase = Increase
            Decrease = Decrease
    user:
        User to modify
    number:
        Amount to change
    reason:
        Reason why it's being modified
    affect_total:
        Whether it should affect total count as well
    '''
    from MFramework.database.alchemy import log, types, models
    session = ctx.db.sql.session()
    #TODO: Save reason somewhere!
    u = models.User.fetch_or_add(session, id=user.id)

    i = models.Infraction(server_id=ctx.guild_id, user_id=user.id, moderator_id=ctx.user.id, type=types.Infraction.Counter, reason=reason)
    ctx.db.sql.add(i)
    active_infractions = log.Statistic.get(session, ctx.guild_id, user, types.Statistic.Infractions_Active)
    total_infractions = log.Statistic.get(session, ctx.guild_id, user, types.Statistic.Infractions_Total)
    if type == 'Increase':
        active_infractions.value += number
        if affect_total:
            total_infractions.value += number
        await auto_moderation(ctx, session, user, increase_counters=False)
    else:
        active_infractions.value -= number
        if affect_total:
            total_infractions.value -= number
    session.commit()
    await ctx.reply(f"Successfully changed. New count is {active_infractions.value}/{total_infractions.value}")


#@register(group=Groups.HELPER, main=infraction)
async def warn(ctx: Context, user: UserID, reason: str = "", *, language):
    '''Warns user'''
    return await infraction(ctx, types.Infraction.Warn, user, reason)

#@register(group=Groups.MODERATOR, main=infraction)
async def mute(ctx: Context, user: UserID, reason: str = "", *, language):
    '''Mutes user'''
    return await infraction(ctx, types.Infraction.Mute, user, reason)

#@register(group=Groups.MODERATOR, main=infraction)
async def kick(ctx: Context, user: UserID, reason: str = "", *, language):
    '''Kicks user'''
    return await infraction(ctx, types.Infraction.Kick, user, reason)

#@register(group=Groups.MODERATOR, main=infraction)
async def ban(ctx: Context, user: UserID, reason: str = "", *, language):
    '''Bans user'''
    return await infraction(ctx, types.Infraction.Ban, user, reason)

#@register(group=Groups.HELPER, main=infraction)
async def tempmute(ctx: Context, user: UserID, reason: str = "", duration: int=0, *, language):
    '''Temporarly mutes user'''
    return await infraction(ctx, types.Infraction.Temp_Mute, user, reason, duration)

#@register(group=Groups.HELPER, main=infraction)
async def tempban(ctx: Context, user: UserID, reason: str = "", duration: int=0, *, language):
    '''Temporarly bans user'''
    return await infraction(ctx, types.Infraction.Temp_Ban, user, reason, duration)

#@register(group=Groups.MODERATOR, main=infraction)
async def unmute(ctx: Context, user: UserID, reason: str = "", *, language):
    '''Unmutes user'''
    return await infraction(ctx, types.Infraction.Unmute, user, reason)

#@register(group=Groups.ADMIN, main=infraction)
async def unban(ctx: Context, user: UserID, reason: str = "", *, language):
    '''Unbans user'''
    return await infraction(ctx, types.Infraction.Unban, user, reason)
