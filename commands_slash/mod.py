from MFramework import register, Groups, Context, Interaction, ChannelID, Snowflake, UserID, Role


@register(group=Groups.MODERATOR)
async def dm(ctx: Context, user: UserID, message: str, *args, language, **kwargs):
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
        await ctx.reply(f"Message sent.\nChannelID: {dm.id}\nMessageID: {msg.id}", private=True)
    except:
        await ctx.reply("Couldn't Deliver message to specified user.", private=True)

@register(group=Groups.MODERATOR)
async def say(ctx: Context, message: str, channel: ChannelID=None, *args, language, **kwargs):
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
    await ctx.reply(f"Message sent.\nChannelID: {msg.channel_id}\nMessageID: {msg.id}", private=True)

@register(group=Groups.MODERATOR)
async def react(ctx: Context, reaction: str, message_id: Snowflake, channel: ChannelID=None, *args, language, **kwargs):
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
    await ctx.reply("Reacted", private=True)

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
    await ctx.deferred(private=False)
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
    await ctx.reply(embeds=[embed])

@register(group=Groups.MODERATOR, interaction=False)
async def creationdate(ctx: Context, *snowflake: Snowflake, **kwargs):
    '''
    Shows creation date based on provided snowflakes
    Params
    ------
    snowflake:
        List of Snowflakes to show creation date for
    '''
    from MFramework import Embed
    import time
    embed = Embed()
    for flake in snowflake[0]:
        if not flake.isdigit():
            await ctx.reply(f"Snowflake {flake} has to be digits")
            continue
        r = [f"<@{flake}>", "On Discord since: {}".format(Snowflake(flake).styled_date())]
        try:
            member = await ctx.bot.get_guild_member(ctx.guild_id, flake)
            r.append("Joined Server at: <t:{}>".format(int(time.mktime(member.joined_at.timetuple()))))
            try:
                r.append("Booster since: <t:{}>".format(int(time.mktime(member.premium_since.timetuple()))))
            except:
                pass
        except:
            pass
        embed.addField(f"{flake}",'\n'.join(r))
    await ctx.reply(embeds=[embed])