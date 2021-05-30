from MFramework import register, Groups, Context, Interaction, ChannelID, Snowflake, UserID, Bitwise_Permission_Flags, Channel, Overwrite, Role


@register(group=Groups.MODERATOR)
async def dm(ctx: Context, interaction: Interaction, user: UserID, message: str, *args, language, **kwargs):
    '''
    DMs user with specified message
    Params
    ------
    user:
        User to which Message should be send
    message:
        Message to send
    '''
    try:
        dm = await ctx.bot.create_dm(user)
        msg = await ctx.bot.create_message(dm.id, message)
        await interaction.respond_private(f"Message sent.\nChannelID: {dm.id}\nMessageID: {msg.id}")
    except:
        await interaction.respond_private("Couldn't Deliver message to specified user.")

@register(group=Groups.MODERATOR)
async def say(ctx: Context, interaction: Interaction, message: str, channel: ChannelID=None, *args, language, **kwargs):
    '''
    Sends message as a bot
    Params
    ------
    message:
        Message to send
    channel:
        Channel to which message should be send
    '''
    msg = await ctx.bot.create_message(channel, message)
    await interaction.respond_private(f"Message sent.\nChannelID: {msg.channel_id}\nMessageID: {msg.id}")

@register(group=Groups.MODERATOR)
async def react(ctx: Context, interaction: Interaction, reaction: str, message_id: Snowflake, channel: ChannelID=None, *args, language, **kwargs):
    '''
    Reacts to a message as a bot
    Params
    ------
    reaction:
        Reaction(s) which should be used to react.
    message_id:
        Message to which bot should react
    channel:
        Use it if Message is in a different channel
    '''
    for each in reaction.split(','):
        await ctx.bot.create_reaction(channel, message_id, each.replace("<:", "").replace(">", "").strip())
    await interaction.respond_private("Reacted")

@register(group=Groups.ADMIN)
async def slowmode(ctx: Context, interaction: Interaction, limit:int=0, duration: int=0, channel: ChannelID=None, all: bool=False, *args, language, **kwargs):
    '''
    Sets a slowmode on a channel
    Params
    ------
    limit:
        Slowmode duration
    duration:
        How long slowmode should last
    channel:
        Channel to slowmode
    all:
        Whether slowmode should be server-wide or not
    '''
    channels = {}
    d = int(duration)
    await interaction.respond_private(f"Applying Slowmode in progress...")
    if all:
        for channel in ctx.cache.channels.values():
            if channel.type == 0:
                try:
                    channels[channel.id] = channel.rate_limit_per_user
                    await ctx.bot.modify_channel(channel.id, rate_limit_per_user=limit, reason="Global Slow mode command")
                except:
                    pass
    else:
        channels[channel] = ctx.cache.channels.get(channel, Channel).rate_limit_per_user
        await ctx.bot.modify_channel(channel, rate_limit_per_user=limit, reason="Slow mode command")
    await interaction.edit_response(f"{'Server wide ' if all else ''}Slow mode activiated")
    if d > 0:
        import asyncio
        await asyncio.sleep(d)
        for channel in channels.values():
            try:
                previous_limit = channels[channel]
                await ctx.bot.modify_channel(channel, rate_limit_per_user=previous_limit, reason="Slow mode expired")
            except:
                pass
        await interaction.edit_response(f"{'Server wide ' if all else ''}Slow mode finished")

@register(group=Groups.ADMIN)
async def lockdown(ctx: Context, interaction: Interaction, duration: int=0, channel: ChannelID=None, all: bool=False, *args, language, **kwargs):
    '''
    Sets a lockdown on a channel
    Params
    ------
    duration:
        How long lockdown should last
    channel:
        Channel to lockdown
    all:
        Whether lockdown should be server-wide or not
    '''
    channels = {}
    d = int(duration)
    lockdown = Bitwise_Permission_Flags.SEND_MESSAGES.value | Bitwise_Permission_Flags.ADD_REACTIONS.value
    await interaction.respond_private(f"Applying Lockdown in progress...")
    if all:
        for channel in ctx.cache.channels.values():
            channels[channel.id] = channel.permission_overwrites
            channel_overwrites = []
            for overwrite in channel.permission_overwrites:
                channel_overwrites.append(Overwrite(id=overwrite.id, type=overwrite.type, allow=overwrite.allow, deny=overwrite.deny | lockdown))
            await ctx.bot.modify_channel(channel.id, permission_overwrites=channel_overwrites, reason="Global Lockdown command")
    else:
        channel = ctx.bot.cache[interaction.guild_id].channels.get(channel, Channel).permission_overwrites
        channels[channel] = channel
        channel_overwrites = []
        for overwrite in channel:
            channel_overwrites.append(Overwrite(id=overwrite.id, type=overwrite.type, allow=overwrite.allow, deny=int(overwrite.deny) | lockdown))
        await ctx.bot.modify_channel(channel, permission_overwrites=channel_overwrites, reason="Lockdown command")
    await interaction.edit_response(f"{'Server wide ' if all else ''}Lockdown activiated")
    if d > 0:
        import asyncio
        await asyncio.sleep(d)
        for channel in channels:
            previous_overwrites = channels[channel]
            await ctx.bot.modify_channel(channel, permission_overwrites=previous_overwrites, reason="Lockdown expired")
        await interaction.edit_response(f"{'Server wide ' if all else ''}Lockdown finished")

@register(group=Groups.ADMIN)
async def listmembers(ctx: Context, interaction: Interaction, role: Role, force_update: bool=False, *args, language, **kwargs):
    '''
    Lists users with provided role
    Params
    ------
    role:
        Role to fetch
    force_update:
        Whether new users should be pulled before counting (Delays response by around 30 seconds)
    '''
    await interaction.deferred_message(private=False)
    if force_update:
        await ctx.bot.request_guild_members(interaction.guild_id)
        import asyncio
        await asyncio.sleep(30)
    total = []
    for member_id, member in ctx.cache.members.items():
        if role.id in member.roles:
            total.append(member_id)
    from MFramework import Embed
    embed = Embed().setDescription(''.join([f'<@{i}>' for i in total])).setFooter(f'Total users/members: {len(total)}/{len(ctx.cache.members)}')
    embed.setColor(role.color).setTitle(f'List of members with role {role.name}')
    #await interaction.edit_response(embeds=[embed])
    await interaction.reply(embeds=[embed])
