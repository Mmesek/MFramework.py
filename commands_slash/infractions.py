from MFramework import register, Groups, Context, Interaction, UserID, User, Embed
#/infraction 
#  | | |---- InfractionType
#  | |           |--------- [User] [reason] [duration]
#  | |------ list           [User]
#  |-------- counter
#                |--------- [User] increase [reason]
#                |--------- [User] decrease [reason]
from MFramework.database.alchemy.types import Infraction as Infractions
#TODO:
# Each infraction as separate command instead of choice type?
# Action on infraction like ban or kick
# Fix logging DMs when not set
# move everything to infraction command group?
# or make infraction list an info subcommand or some other?
# Perhaps alias interaction?
# List recently joined users and provide filter/sorter
@register(group=Groups.MODERATOR)
async def infraction(ctx: Context, type: Infractions, user: User=None, reason:str="", duration:str=None, *args, language, **kwargs):
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
    '''
    await ctx.deferred()
    if duration:
        from mlib.converters import total_seconds
        duration = total_seconds(duration)

    session = ctx.db.sql.session()
    from MFramework.database.alchemy.models import Infraction, User
    u = User.fetch_or_add(session, id=user.id)
    if ctx.bot.emoji.get('fake_infraction', '😜') not in reason or type not in {Infractions.Unban, Infractions.Unmute, Infractions.DM_Unmute, Infractions.Report}:
        from MFramework.database.alchemy import log, types
        log.Statistic.increment(session, ctx.guild_id, user.id, types.Statistic.Infractions_Active)
        log.Statistic.increment(session, ctx.guild_id, user.id, types.Statistic.Infractions_Total)
        active = log.Statistic.get(session, ctx.guild_id, user.id, types.Statistic.Infractions_Active)
        if active.value == ctx.cache.settings.get(types.Setting.Auto_Mute_Infractions, None):
            MUTED_ROLE = None
            await ctx.bot.add_guild_member_role(ctx.guild_id, user.id, MUTED_ROLE, reason=f"{active.value} active infractions")
        elif active.value == ctx.cache.settings.get(types.Setting.Auto_Ban_Infractions, None):
            await ctx.bot.create_guild_ban(ctx.guild_id, user.id, reason=f"{active.value} active infractions")
        # TODO: If either of above, LOG IT AS WELL

    i = Infraction(server_id=ctx.guild_id, user_id=user.id, moderator_id=ctx.user.id, type=type.name, reason=reason, duration=duration)
    ctx.db.sql.add(i)

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


@register(group=Groups.GLOBAL)
async def infractions(ctx: Context, user: User=None, *args, language, **kwargs):
    '''Lists user's infractions'''
    await ctx.deferred()
    session = ctx.db.sql.session()
    from MFramework.database.alchemy.models import Infraction
    _infractions = session.query(Infraction)
    if not False:#show_all:
        _infractions = _infractions.filter(Infraction.server_id == ctx.guild_id)
    _infractions = _infractions.filter(Infraction.user_id == user.id).all()
    _infractions.reverse()
    str_infractions = ""
    e = Embed()
    for x, infraction in enumerate(_infractions):
        str_infractions += f'\n[<t:{int(infraction.timestamp.timestamp())}:d>] `[{infraction.type.name}]` "{infraction.reason}" by <@{infraction.moderator_id}>'
        if infraction.duration:
            from mlib.localization import secondsToText
            str_infractions += f" for {secondsToText(int(infraction.duration.total_seconds()))}"
        if x == 10:
            e.addField("Total infractions", f"{len(_infractions)}")
            break
    if str_infractions != "":
        from mlib.colors import get_main_color
        e.setDescription(str_infractions).setAuthor(f"{user.username}'s infractions", icon_url=user.get_avatar()).setColor(get_main_color(user.get_avatar()))
        from MFramework.database.alchemy import log, types
        a = log.Statistic.get(session, ctx.guild_id, user.id, types.Statistic.Infractions_Active)
        t = log.Statistic.get(session, ctx.guild_id, user.id, types.Statistic.Infractions_Total)
        total = ctx.cache.settings.get(types.Setting.Auto_Ban_Infractions, 5)
        danger = ctx.cache.settings.get(types.Setting.Auto_Mute_Infractions, 3)
        currently_active = ["🔴"] * a.value
        remaining_to_auto_mute = (danger-a.value)
        if remaining_to_auto_mute > 0:
            currently_active += ["🟢"] * remaining_to_auto_mute
        remaining_to_auto_ban = (total-a.value)
        if remaining_to_auto_mute > 0:
            remaining_to_auto_ban -= remaining_to_auto_mute
        if remaining_to_auto_ban > 0:
            currently_active += ["🟡"] * remaining_to_auto_ban
        e.setFooter("["+"-".join(currently_active) + f"] | Active: {a.value} | Total: {t.value}")
        return await ctx.reply(embeds=[e])
    return await ctx.reply("No Infractions")

@register(group=Groups.MODERATOR)
async def counter(ctx: Context, type: str, user: UserID, number: int=1, reason: str=None, affect_total: bool=False, *args, language, **kwargs):
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
    from MFramework.database.alchemy import log, types
    session = ctx.db.sql.session()
    #TODO: Save reason somewhere!
    active_infractions = log.Statistic.get(session, ctx.guild_id, user, types.Statistic.Infractions_Active)
    total_infractions = log.Statistic.get(session, ctx.guild_id, user, types.Statistic.Infractions_Total)
    if type == 'Increase':
        active_infractions.value += number
        if affect_total:
            total_infractions.value += number
    else:
        active_infractions.value -= number
        if affect_total:
            total_infractions.value -= number
    session.commit()
    # TODO: Also perform action like auto mute or autoban here!
    await ctx.reply(f"Successfully changed. New count is {active_infractions.value}/{total_infractions.value}")


#@register(group=Groups.HELPER, main=infraction)
async def warn(ctx: Context, user: UserID, reason: str = "", *args, language, **kwargs):
    '''Warns user'''
    return await infraction(ctx, Infractions.Warn, user, reason)

#@register(group=Groups.MODERATOR, main=infraction)
async def mute(ctx: Context, user: UserID, reason: str = "", *args, language, **kwargs):
    '''Mutes user'''
    return await infraction(ctx, Infractions.Mute, user, reason)

#@register(group=Groups.MODERATOR, main=infraction)
async def kick(ctx: Context, user: UserID, reason: str = "", *args, language, **kwargs):
    '''Kicks user'''
    return await infraction(ctx, Infractions.Kick, user, reason)

#@register(group=Groups.MODERATOR, main=infraction)
async def ban(ctx: Context, user: UserID, reason: str = "", *args, language, **kwargs):
    '''Bans user'''
    return await infraction(ctx, Infractions.Ban, user, reason)

#@register(group=Groups.HELPER, main=infraction)
async def tempmute(ctx: Context, user: UserID, reason: str = "", duration: int=0, *args, language, **kwargs):
    '''Temporarly mutes user'''
    return await infraction(ctx, Infractions.Temp_Mute, user, reason, duration)

#@register(group=Groups.HELPER, main=infraction)
async def tempban(ctx: Context, user: UserID, reason: str = "", duration: int=0, *args, language, **kwargs):
    '''Temporarly bans user'''
    return await infraction(ctx, Infractions.Temp_Ban, user, reason, duration)

#@register(group=Groups.MODERATOR, main=infraction)
async def unmute(ctx: Context, user: UserID, reason: str = "", *args, language, **kwargs):
    '''Unmutes user'''
    return await infraction(ctx, Infractions.Unmute, user, reason)

#@register(group=Groups.ADMIN, main=infraction)
async def unban(ctx: Context, user: UserID, reason: str = "", *args, language, **kwargs):
    '''Unbans user'''
    return await infraction(ctx, Infractions.Unban, user, reason)


#@register(group='Mod', help='Warns user', alias='tempmute, mute, kick, tempban, ban, unban, unmute', category='infractions')
async def warn(self, user, *reason, data, language, cmd, **kwargs):
    '''Extended description to use with detailed help command'''
    interaction = Interaction(_Client=self, guild_id=data.guild_id, channel_id=data.channel_id, user=data.user)
    await infraction(self, interaction, cmd, user, ' '.join(reason), language=language)