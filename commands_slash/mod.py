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
