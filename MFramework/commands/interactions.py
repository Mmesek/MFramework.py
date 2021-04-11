from MFramework import RoleID, UserID, ChannelID, Role, User, Channel, Guild_Member, GuildID
from ._utils import Groups, commands, detect_group, find_command, is_nested, parse_docstring, parse_signature, iterate_commands

from MFramework import Snowflake, Interaction, Guild#, create_guild_application_command, create_global_application_command, get_global_application_commands, get_guild_application_commands

def register(group: Groups = Groups.GLOBAL, interaction: bool = True, main=False, guild: Snowflake = None, choice=None, **kwargs):
    '''Decorator for creating commands.
    
    Params
    ------
    group:
        is a lowest group that can access this command (Highest digit). DM and Muted are special groups
    interaction:
        whether this function should be an interaction or not
    main:
        is a function pointer. 
    guild: 
        is used when command is exclusive to a specific guild'''
    def inner(f):
        _name = f.__name__.lower()
        if main:
            _name = main.__name__.lower()+'.'+_name
        commands[group][_name] = {}
        commands[group][_name]['function'] = f
        _docstring = parse_docstring(f)
        commands[group][_name]['help'] = (f'[{group.name}] ' if group.value < 5 else '')+ _docstring['_doc']
        commands[group][_name]['arguments'] = parse_signature(f, _docstring)
        commands[group][_name]['interaction'] = interaction
        commands[group][_name]['master_command'] = main
        commands[group][_name]['sub_commands'] = []
        if main:
            _groups = list(commands.keys())
            for current_group in _groups[_groups.index(group):]:
                if main.__name__.lower() in commands[current_group]:
                    commands[current_group][main.__name__.lower()]['sub_commands'].append({"name":_name, "help":_docstring['_doc'], "arguments":parse_signature(f, _docstring), "function": f})
                    break
        commands[group][_name]['guild'] = guild
        return f
    return inner

from mdiscord import onDispatch
@onDispatch
async def interaction_create(Client, interaction: Interaction):
    '''Called after receiving event INTERACTION_CREATE from Discord'''
    if interaction.member is None:
        return # Command was issued in DM. While some commands could be used there, we don't support it right now
    name = interaction.data.name

    g = detect_group(Client, interaction.member.user.id, interaction.guild_id, interaction.member.roles)
    f = find_command(g, name)
    sub = name+'.'+interaction.data.options[0].name if len(interaction.data.options) > 0 and f['sub_commands'] != [] else name
    #TODO: Follow the rabbit hole if sub_commands are set
    if sub != name:
        f = is_nested(g, f, sub)
        interaction.data.options = interaction.data.options[0].options
    kwargs = {}
    for option in interaction.data.options:
        t = f['arguments'][option.name]['type']
        if t not in [Channel, Role, User, Guild_Member, ChannelID, UserID, RoleID]:
            kwargs[option.name] = f['arguments'][option.name]['type'](option.value)
        elif issubclass(t, Snowflake):
            # We are casting it to Snowflake due to some recursion error. 
            # Otherwise, the above should be sufficient
            kwargs[option.name] = Snowflake(option.value) 
        else:
            o = getattr(interaction.data.resolved, t.__name__.lower().replace('guild_','')+'s', {}).get(str(option.value), t())
            if t is Guild_Member:
                o.user = interaction.data.resolved.users.get(str(option.value), User())
            kwargs[option.name] = o
        if t is RoleID:
            print(issubclass(t, Snowflake))
    #kwargs = {option.name:f['arguments'][option.name]['type'](option.value) for option in interaction.data.options} #TODO: Scrap subcommands?
    options = {i.name:f['arguments'] for i in interaction.data.options if i.name not in kwargs}
    for arg in f['arguments']:
        if arg not in kwargs:
            t = f['arguments'][arg]['type']
            if t is ChannelID:
                i = interaction.channel_id
            elif t is RoleID:
                i = interaction.guild_id
            elif t is UserID:
                i = interaction.user.id
            elif t is User:
                i = interaction.user
            elif t is Guild_Member:
                i = interaction.member
                i.user = interaction.user
            elif t is GuildID:
                i = interaction.guild_id
            else:
                continue
            kwargs[arg] = i

    await f['function'](Client, interaction=interaction, language='en', group=g, **kwargs)

async def register_interactions(Client):
    '''Called after connecting with Discord. Preferably after receiving READY event'''
    registered = await Client.get_global_application_commands(Client.application.id)
#    for cmd in registered:
#        await Client.delete_global_application_command(Client.application.id, cmd.id)
    for command, _command, options in iterate_commands(registered):
        if not _command['interaction'] or _command['guild'] or _command['master_command']:
            continue
        print("Creating global command", command)
        #FIXME 
        #try:
        #await Client.create_global_application_command(Client.application.id, command, _command['help'][:100], options)
        #except Exception as ex:
        #    print(ex)

@onDispatch
async def guild_create(ctx, guild: Guild):
#async def register_guild_interactions(Client, guild_id: Snowflake):
    '''Called after GUILD_CREATE'''
    try:
        app = ctx.application
    except:
        import asyncio
        await asyncio.sleep(3)
        app = ctx.application
    try:
        registered = await ctx.get_guild_application_commands(app.id, guild.id)
#        for cmd in registered:
#            await ctx.delete_guild_application_command(ctx.application.id, guild.id, cmd.id)
    except:
        return
    for command, _command, options in iterate_commands(registered):
        if not _command['interaction'] or _command['guild'] != guild.id or _command.get('master_command', False):
            continue
        print(f"Creating {_command['guild']} command")
        #FIXME 
        #await ctx.create_guild_application_command(ctx.application.id, _command['guild'] or guild.id, command, _command['help'][:100], options)


def Event(*, month=None, day=None, hour=None, minute=None, year=None):
    '''Executes command only if it's during provided timeframe'''
    def inner(f):
        def wrapped(*args, **kwargs):
            from datetime import datetime
            t = datetime.today()
            d = datetime(year or t.year, month or t.month, day or t.day, hour if hour is not None else t.hour, minute if minute is not None else t.minute)
            t = t.replace(second=0, microsecond=0)
            if t == d:
                return f(*args, **kwargs)
        return wrapped
    return inner

def Cooldown(*, seconds=None, minutes=None, hours=None, days=None, weeks=None, logic=lambda x: x):
    '''Applies a cooldown on command.
    Use it with callable function accepting interaction returning boolean for conditional execution and datetime object with last execution timestamp for cooldown calculation'''
    def inner(f):
        def wrapped(interaction: Interaction= None, *args, **kwargs):
            should_execute, last_execution = logic(interaction)
            if should_execute:
                from datetime import datetime, timedelta
                cooldown = timedelta(days=days, seconds=seconds, minutes=minutes, hours=hours, weeks=weeks)
                if (datetime.now() - last_execution) > cooldown:
                    return f(interaction=interaction, *args, **kwargs)
        return wrapped
    return inner
