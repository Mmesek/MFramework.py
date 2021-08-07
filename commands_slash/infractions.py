from datetime import datetime, timedelta, timezone
from MFramework import register, Groups, Context, UserID, User, Embed, shortcut, Message
#/infraction 
#  | | |---- InfractionType
#  | |           |--------- [User] [reason] [duration]
#  | |------ list           [User]
#  |-------- counter
#                |--------- [User] increase [reason]
#                |--------- [User] decrease [reason]
from MFramework.database.alchemy import types, models
#TODO:
# Each infraction as separate command instead of choice type?
# Action on infraction like ban or kick
# move everything to infraction command group?
# or make infraction list an info subcommand or some other?
# Perhaps alias interaction?
# List recently joined users and provide filter/sorter
@register(group=Groups.HELPER, main_only=True)
#@shortcut(name="warn", group=Groups.HELPER, type=types.Infraction.Warn, help="Warns user")
#@shortcut(name="mute", group=Groups.MODERATOR, type=types.Infraction.Mute, help="Mutes user")
#@shortcut(name="kick", group=Groups.MODERATOR, type=types.Infraction.Kick, help="Kicks user")
#@shortcut(name="ban", group=Groups.MODERATOR, type=types.Infraction.Ban, help="Bans user")
#@shortcut(name="tempmute", group=Groups.HELPER, type=types.Infraction.Temp_Mute, help="Temporarly mutes user")
#@shortcut(name="tempban", group=Groups.HELPER, type=types.Infraction.Temp_Ban, help="Temporarly bans user")
#@shortcut(name="unmute", group=Groups.MODERATOR, type=types.Infraction.Unban, help="Unmutes user")
#@shortcut(name="unban", group=Groups.ADMIN, type=types.Infraction.Unmute, help="Unbans user")
async def infraction(ctx: Context, *, type: types.Infraction, user: User=None, reason:str="", duration:timedelta=None, increase_counter: bool=True):
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
    u = models.User.fetch_or_add(session, id=user.id)
    active = False
    if (ctx.bot.emoji.get('fake_infraction', '😜') not in reason or type not in {types.Infraction.Unban, types.Infraction.Unmute, types.Infraction.DM_Unmute, types.Infraction.Report}) and increase_counter:
        active = True
    u.add_infraction(server_id=ctx.guild_id, moderator_id=ctx.user.id, type=type.name, reason=reason, duration=duration, active=active)

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


@register(group=Groups.GLOBAL, main=infraction, aliases=["infractions"])
async def list_(ctx: Context, user: User=None, *, language):
    '''Lists user's infractions'''
    await ctx.deferred()
    session = ctx.db.sql.session()
    u = models.User.fetch_or_add(session, id = user.id)
    _infractions = u.infractions
    if not False:#show_all:
        _infractions = list(filter(lambda x: x.server_id == ctx.guild_id, u.infractions))
    width, id_width, active = 0, 0, 0
    user_infractions = []
    from collections import namedtuple
    Row = namedtuple("Row", ['id', 'timestamp', 'type', 'reason', 'moderator_id', 'duration', 'active'])
    from mlib.localization import tr, secondsToText
    for infraction in _infractions:
        translated = tr(f"commands.infractions.types.{infraction.type.name}", language)
        if len(translated) > width:
            width = len(translated)
        if len(str(infraction.id)) > id_width:
            id_width = len(str(infraction.id))
        if infraction.active and infraction.duration and infraction.timestamp + infraction.duration < datetime.now(tz=timezone.utc):
            infraction.active = False
        user_infractions.append(
            Row(
                id=infraction.id,
                timestamp=int(infraction.timestamp.timestamp()),
                type=translated,
                reason=infraction.reason,
                moderator_id=infraction.moderator_id,
                duration=tr("commands.infractions.for_duration", language, 
                        duration=secondsToText(int(infraction.duration.total_seconds()), language)) 
                        if infraction.duration else "",
                active="~~" if not infraction.active else ""
            )
        )
        if infraction.active:
            active+=1
    session.commit()
    str_infractions = '\n'.join(tr("commands.infractions.row", language, width=width, id_width=id_width, **i._asdict()).format(type=i.type, id=i.id).strip() for i in user_infractions[:10])
    if str_infractions != "":
        from mlib.colors import get_main_color
        e = Embed()
        e.setDescription(str_infractions).setAuthor(tr("commands.infractions.title", language, username=user.username), icon_url=user.get_avatar()).setColor(get_main_color(user.get_avatar()))
        total = ctx.cache.settings.get(types.Setting.Auto_Ban_Infractions, 5)
        danger = ctx.cache.settings.get(types.Setting.Auto_Mute_Infractions, 3)
        currently_active = ["🔴"] * active
        remaining_to_auto_mute = (danger-active)
        if remaining_to_auto_mute > 0:
            currently_active += ["🟢"] * remaining_to_auto_mute
        remaining_to_auto_ban = (total-active)
        if remaining_to_auto_mute > 0:
            remaining_to_auto_ban -= remaining_to_auto_mute
        if remaining_to_auto_ban > 0:
            currently_active += ["🟡"] * remaining_to_auto_ban
        e.setFooter(tr("commands.infractions.counter", language, currently_active="-".join(currently_active), active=active, total=len(user_infractions)))
        return await ctx.reply(embeds=[e])
    return await ctx.reply(tr("commands.infractions.no_infractions", language))

@register(group=Groups.MODERATOR, main=infraction)
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


@register(group=Groups.HELPER, main=infraction, aliases=["warn"])
async def warn(ctx: Context, user: User, reason: str = "", *, language):
    '''Warns user'''
    return await infraction(ctx, type=types.Infraction.Warn, user=user, reason=reason)

@register(group=Groups.MODERATOR, main=infraction, aliases=["mute"])
async def mute(ctx: Context, user: User, reason: str = "", *, language):
    '''Mutes user'''
    return await infraction(ctx, type=types.Infraction.Mute, user=user, reason=reason)

@register(group=Groups.MODERATOR, main=infraction, aliases=["kick"])
async def kick(ctx: Context, user: User, reason: str = "", *, language):
    '''Kicks user'''
    return await infraction(ctx, type=types.Infraction.Kick, user=user, reason=reason)

@register(group=Groups.MODERATOR, main=infraction, aliases=["ban"])
async def ban(ctx: Context, user: User, reason: str = "", *, language):
    '''Bans user'''
    return await infraction(ctx, type=types.Infraction.Ban, user=user, reason=reason)

@register(group=Groups.HELPER, main=infraction, aliases=["tempmute"])
async def tempmute(ctx: Context, user: User, duration: timedelta=None, reason: str = "", *, language):
    '''Temporarly mutes user'''
    return await infraction(ctx, type=types.Infraction.Temp_Mute, user=user, reason=reason, duration=duration)

@register(group=Groups.HELPER, main=infraction, aliases=["tempban"])
async def tempban(ctx: Context, user: User, duration: timedelta=None, reason: str = "", *, language):
    '''Temporarly bans user'''
    return await infraction(ctx, type=types.Infraction.Temp_Ban, user=user, reason=reason, duration=duration)

@register(group=Groups.MODERATOR, main=infraction, aliases=["unmute"])
async def unmute(ctx: Context, user: User, reason: str = "", *, language):
    '''Unmutes user'''
    return await infraction(ctx, type=types.Infraction.Unmute, user=user, reason=reason)

@register(group=Groups.ADMIN, main=infraction, aliases=["unban"])
async def unban(ctx: Context, user: User, reason: str = "", *, language):
    '''Unbans user'''
    return await infraction(ctx, type=types.Infraction.Unban, user=user, reason=reason)

@register(group=Groups.GLOBAL, interaction=False)
async def report(ctx: Context, message: Message, *msg: str, language, **kwargs):
    '''
    Report situation on server to Moderators
    Params
    ------
    msg:
        optional message about what's happening
    '''
    await ctx.cache.logging["report"](message)
    for moderator in filter(lambda x: message.channel_id in x["moderated_channels"] or language in x["languages"], ctx.cache.moderators):
        await ctx.cache.logging["report"].log_dm(message)
    await message.react(ctx.bot.emoji.get("success"))