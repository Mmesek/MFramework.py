from MFramework import RoleID, UserID, ChannelID, Role, User, Channel, Guild_Member, GuildID
from ._utils import detect_group, find_command, is_nested, iterate_commands

from MFramework import Snowflake, Interaction, Guild#, create_guild_application_command, create_global_application_command, get_global_application_commands, get_guild_application_commands

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
