from MFramework import (onDispatch,
    RoleID, UserID, ChannelID, Role, User, Channel, Guild_Member, Snowflake, 
    Interaction, Guild, Application_Command,
    Context, Bot, Groups, log)

from ._utils import user_group, find_command, is_nested, iterate_commands, set_default_arguments

@onDispatch
async def interaction_create(client: Bot, interaction: Interaction):
    '''Called after receiving event INTERACTION_CREATE from Discord'''
    ctx = Context(client.cache, client, interaction)
    name = interaction.data.name
    g = user_group(ctx)

    f = find_command(g, name)
    if not f:
        log.debug("Command %s not found", name)
        return
    
    ##########TODO##FIXME###TODO################################################################
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
    ############################################################################################
    options = {i.name:f['arguments'] for i in interaction.data.options if i.name not in kwargs}

    kwargs = set_default_arguments(ctx, f, kwargs)
    await f['function'](client, interaction=interaction, language='en', group=g, **kwargs)


import sys
@onDispatch
async def ready(client: Bot):
    '''Called after connecting with Discord. Preferably after receiving READY event'''
    if getattr(client, 'registered', False):
        return
    client.application = await client.get_current_bot_application_information()

    registered = await client.get_global_application_commands(client.application.id)

    if '--clear_interactions' in sys.argv:
        for cmd in registered:
            log.info("Deleting Global command %s from bot %s", cmd, client.username)
            await client.delete_global_application_command(client.application.id, cmd.id)
        return
    
    new_commands = []
    for command, _command, options in iterate_commands(registered):
        if not _command['interaction'] or _command['guild'] or _command.get('master_command', False):
            log.debug("Skippging command %s from registering as Global. Eiter Guild-Only or it's a subCommand", command)
            continue
        log.info("Registering Global command %s on bot %s", command, client.username)
        new_commands.append(Application_Command(name=command, description=_command['help'][:100], options=options, default_permission=_command['group'] == Groups.GLOBAL))
    if new_commands != []:
        await client.bulk_overwrite_global_application_commands(client.application.id, new_commands)

@onDispatch
async def guild_create(client: Bot, guild: Guild):
    '''Called after GUILD_CREATE'''
    try:
        app = client.application
    except:
        import asyncio
        await asyncio.sleep(3)
        app = client.application

    registered = await client.get_guild_application_commands(app.id, guild.id)

    if '--clear_interactions' in sys.argv:
        for cmd in registered:
            log.info("Deleting Guild command %s from bot %s from %s", cmd.name, client.username, guild.id)
            await client.delete_guild_application_command(client.application.id, guild.id, cmd.id)
        return

    new_commands = []
    for command, _command, options in iterate_commands(registered):
        if not _command['interaction'] or _command['guild'] != guild.id or _command.get('master_command', False):
            continue
        log.info("Registering Guild command %s on bot %s for %s", command, client.username, guild.id)
        new_commands.append(Application_Command(name=command, description=_command['help'][:100], options=options, default_permission=_command['group'] == Groups.GLOBAL))
    if new_commands != []:
        await client.bulk_overwrite_guild_application_commands(client.application.id, guild.id, new_commands)
