from MFramework import register, Groups, Context, ChannelID, Snowflake

@register(group=Groups.ADMIN)
async def settings():
    '''Management of server related bot settings'''
    pass

@register(group=Groups.ADMIN, main=settings)
async def language(ctx: Context, new_language: str = None, channel: ChannelID=None, *, language):
    '''Management of language bot settings
    
    Params
    ------
    new_language:
        New language that should be set
    channel:
        Channel of which language should be changed. Leave empty if server-wide
    '''
    pass

class Tracking:
    Chat = "Chat"
    Voice = "Voice"
    Presence = "Presence"


@register(group=Groups.ADMIN, main=settings)
async def tracking(ctx: Context, type: Tracking, channel: ChannelID=None, *, language):
    '''Management of bot's tracking settings
    
    Params
    ------
    type:
        Tracking type to switch
    channel:
        Whether this channel should be disabled from tracking
    '''
    pass

@register(group=Groups.ADMIN, main=settings)
async def webhooks():
    '''Management of webhooks related bot settings'''
    pass

@register(group=Groups.ADMIN, main=webhooks)
async def subscribe(ctx: Context, source: str, channel: ChannelID = None, webhook: str = None, content: str = None, regex: str = None, *, language):
    '''Subscribe webhook to specified source
    
    Params
    ------
    source:
        Source to which this webhook/channel should be subscribed to
    webhook:
        Webhook URL to subscribe to. If empty, creates one
    content:
        Content of message to send alongside
    regex:
        Whether it should only be sent if there is matching pattern
    '''
    from MFramework.database.alchemy import models
    _w = models.Webhook()
    if webhook:
        webhooks = await ctx.bot.get_guild_webhooks(ctx.guild_id)
        for wh in filter(lambda x: x.channel_id == channel or ctx.channel_id, webhooks):
            if wh.user.id == ctx.bot.user_id or any(s in wh.name for s in {"RSS", "DM"}):
                _w.id = wh.id
                _w.token = wh.token
                break
    if not webhook and not _w.id:
        if "log" in source.lower():
            name = "Logging"
        elif "dm" not in source.lower():
            name = "RSS"
        else:
            name = "DM Inbox"
        wh = await ctx.bot.create_webhook(channel, name, f"Requested by {ctx.user.username}")
        _w.id = wh.id
        _w.token = wh.token
    _w.channel_id = channel
    _w.server_id = ctx.guild_id
    s = ctx.db.sql.session()
    s.add(_w)
    s.commit()


@register(group=Groups.ADMIN, main=webhooks)
async def ubsubscribe(ctx: Context, source: str, webhook: str=None, *, language):
    '''Unsubscribe this channel from provided source
    
    Params
    ------
    source:
        Source to unsubscribe from
    webhook:
        Webhook which should be unsubscribed
    '''
    pass

@register(group=Groups.ADMIN, main=settings)
async def roles():
    '''Management of role related bot settings'''
    pass

@register(group=Groups.ADMIN, main=settings)
async def channels():
    '''Management of channel related bot settings'''
    pass

class ChannelTypes:
    RPG = "RPG"
    Dynamic = "Dynamic"
    Buffer = "Buffer"

@register(group=Groups.ADMIN, main=channels)
async def type(ctx: Context, type: ChannelTypes, channel: ChannelID=None, name: str=None, parent_or_buffer_id: Snowflake=None, bitrate: int=64000, user_limit: int=0, postion: int=0, *, language):
    '''Sets type to specified channel
    
    Params
    ------
    type:
        type of channel
    '''
    pass