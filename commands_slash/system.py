from MFramework import register, Groups, Context
from MFramework.utils.timers import *
from MFramework.database.alchemy.types import Flags

@register(group=Groups.SYSTEM, interaction=False)
async def shutdown(ctx: Context, *args, **kwargs):
    '''Shuts bot down.'''
    if ctx.cache.is_tracking(Flags.Voice):
        for v in ctx.cache.voice:
            users = []
            for u in ctx.cache.voice[v]:
                users.append(u)
            for u in users:
                finalize(ctx.bot, ctx.guild_id, v, u)
    if ctx.cache.context:
        s = ''
        for channel_id, author_id in ctx.cache.context[ctx.guild_id]:
            s += f'\n<#{channel_id}> <@{author_id}>'
            #await self.message(channel_id, "Context ended. To retry type the command that started context again later.")
        if s!='':
            await ctx.reply("Ended contexts: "+s)
    await ctx.bot.close()
    from MFramework import log
    log.info("Received shutdown command. Shutting down.")

@register(group=Groups.SYSTEM, interaction=False)
async def updateStatus(ctx: Context, status="How the World Burns", status_kind="Online", status_type=3, afk=False, *args, **kwargs):
    """Changes Bot's status
    Params
    ------
    Kind:
        Online/dnd/idle/invisible/offline
    Type:
        0 - Playing, 1 - Streaming, 2 - Listening, 3 - Watching"""
    await ctx.bot.presence_update(status_kind, status, status_type, afk)

@register(group=Groups.SYSTEM, interaction=False)
async def reloadCommands(ctx: Context, *args, **kwargs):
    """Reloads commands files.
    This probably needs to be placed in another file but well, it's here currently FOR SCIENCE."""
    import importlib
    importlib.reload(__name__)

@register(group=Groups.SYSTEM, interaction=False)
async def update(ctx: Context, *args, language, **kwargs):
    '''Pulls new commits'''
    import git
    try:
        git.Repo().remotes.origin.pull()
        await ctx.bot.create_reaction(ctx.channel_id, ctx.message_id, ctx.bot.emoji['success'])
    except:
        await ctx.bot.create_reaction(ctx.channel_id, ctx.message_id, ctx.bot.emoji['failure'])