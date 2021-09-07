# -*- coding: utf-8 -*-
'''
Interactions
------------

Interaction commands registery & execution framework

:copyright: (c) 2021 Mmesek
'''
from datetime import timedelta
from MFramework import (onDispatch, Ready, Interaction_Type,
    RoleID, UserID, ChannelID, Role, User, Channel, Guild_Member, Snowflake, Message,
    Interaction, Guild, Application_Command, Application_Command_Option_Type,
    Context, Bot, Groups, log,
    Application_Command_Permissions, Application_Command_Permission_Type, Guild_Application_Command_Permissions,
    Application_Command_Type
    )

from ._utils import is_nested, iterate_commands, set_default_arguments, commands, add_extra_arguments, Command

@onDispatch
async def interaction_create(client: Bot, interaction: Interaction):
    '''Called after receiving event INTERACTION_CREATE from Discord'''
    if interaction.type != Interaction_Type.APPLICATION_COMMAND:
        return
    ctx = Context(client.cache, client, interaction)
    name = interaction.data.name
    f = commands.get(name, None)
    g = ctx.permission_group
    if not f or f.group.value < g.value:
        if not f:
            log.debug("Command %s not found", name)
        return
    if len(interaction.data.options) and interaction.data.options[0].type in {Application_Command_Option_Type.SUB_COMMAND_GROUP, Application_Command_Option_Type.SUB_COMMAND}:
        f = is_nested(g, f, interaction.data.options[0].name)
        interaction.data.options = interaction.data.options[0].options
        if len(interaction.data.options) and interaction.data.options[0].type in {Application_Command_Option_Type.SUB_COMMAND}:
            f = is_nested(g, f, interaction.data.options[0].name)
            interaction.data.options = interaction.data.options[0].options
    if f.group.value < g.value:
        return
    kwargs = {}
    kwargs = add_extra_arguments(f, kwargs, ctx=ctx, client= client, interaction=interaction, language='en')
    for option in interaction.data.options:
        t = f.arguments[option.name].type
        if issubclass(t, Snowflake) and not option.value.isdigit():
            from MFramework.utils.utils import parseMention
            option.value = parseMention(option.value)
        if t not in [Channel, Role, User, Guild_Member, ChannelID, UserID, RoleID]:
            if type(option.value) is str and option.value.isdigit():
                option.value = int(option.value)
            if type(t) is timedelta:
                from mlib.converters import total_seconds
                v = total_seconds(option.value)
            else:
                v = f.arguments[option.name].type(option.value)
            kwargs[option.name] = v
        elif issubclass(t, Snowflake):
            # We are casting it to Snowflake due to some recursion error. 
            # Otherwise, the above should be sufficient
            kwargs[option.name] = Snowflake(option.value) 
        else:
            o = getattr(interaction.data.resolved, t.__name__.lower().replace('guild_','')+'s', {}).get(str(option.value), t())
            if t is Guild_Member:
                o.user = interaction.data.resolved.users.get(str(option.value), User())
            kwargs[option.name] = o
    if not interaction.data.options and interaction.data.resolved:
        for arg in f.arguments.values():
            if arg.type in {Guild_Member, User, UserID, Channel, Role, ChannelID, RoleID, Message}:
                t = f.arguments[arg.name].type
                o = list(getattr(interaction.data.resolved, t.__name__.lower().replace('guild_','')+'s', {}).values())
                o = o[0] if o else t()
                if t is Guild_Member:
                    _user = list(interaction.data.resolved.users.values())[0]
                    o.user = _user or User()
                kwargs[arg.name] = o
    kwargs = set_default_arguments(ctx, f, kwargs)
    await f.execute(ctx, kwargs)


from mlib import arguments
CLEAR_INTERACTIONS = getattr(arguments.parse(), 'clear_interactions', False)
UPDATE_PERMISSIONS = getattr(arguments.parse(), 'update_permissions', False)

@onDispatch(priority=101)
async def ready(client: Bot, ready: Ready):
    '''Called after connecting with Discord. Preferably after receiving READY event'''
    if getattr(client, 'registered', False):
        return
    client.application = await client.get_current_bot_application_information()
    await register_commands(client)

@onDispatch(priority=101)
async def guild_create(client: Bot, guild: Guild):
    '''Called after GUILD_CREATE'''
    if not client.application:
        import asyncio
        await asyncio.sleep(3)
        return await guild_create(client, guild)
    
    _commands = await register_commands(client, guild)
    
    if client.cache[guild.id]._permissions_set is False or UPDATE_PERMISSIONS:
        await set_permissions(client, guild.id, _commands)

async def register_commands(client: Bot, guild: Guild = None):
    registered = await get_commands(client, guild)

    registered_commands = {i.name: i.id for i in registered if i.name in commands}
    unrecognized_commands = [i for i in registered if i.name not in commands]

    new_commands = []
    updated_commands = []
    _cmds = []

    if CLEAR_INTERACTIONS:
        return await overwrite_commands(client, [], guild)
    else:
        for cmd in unrecognized_commands:
            await delete_command(client, cmd, guild)


    for command, _command, options in iterate_commands(registered, guild.id if guild else None):
        cmd = Application_Command(name=command, description=_command.help[:100], options=options, default_permission=_command.group == Groups.GLOBAL)
        if len(options) == 1 and options[0].type is Application_Command_Option_Type.USER:
            cmd.type = Application_Command_Type.USER
            cmd.description = None
            cmd.options = None
            if any(command == i.name for i in registered):
                continue
        elif len(options) == 1 and options[0].type is Message:
            cmd.type = Application_Command_Type.MESSAGE
            cmd.description = None
            cmd.options = None
            if any(command == i.name for i in registered):
                continue

        if command not in registered_commands:
            new_commands.append(cmd)
        else:
            cmd.id = registered_commands[cmd.name]
            updated_commands.append(cmd)


    if len(new_commands) == len(commands):
        _cmds = await overwrite_commands(client, new_commands + updated_commands, guild)
    else:
        for cmd in new_commands:
            _cmds.append(await add_command(client, cmd, guild))
        for cmd in updated_commands:
            _cmds.append(await edit_command(client, cmd, guild))

    if guild:
        _cmds = registered + _cmds

        if len(new_commands) > 0:
            client.cache[guild.id]._permissions_set = False
        return _cmds
    else:
        client.registered_commands = registered

from typing import List
async def set_permissions(client: Bot, guild_id: Snowflake, _commands: List[Command]) -> None:
    _commands = (_commands or []) + (client.registered_commands or [])
    groups = client.cache[guild_id].groups
    permissions = []
    for cmd in _commands:
        command_permissions = []
        for group, roles in groups.items():
            f = commands.get(cmd.name, None)
            if f and f.group != Groups.GLOBAL and group.value <= f.group.value:
                for role in roles:
                    log.info("Adding permission for role %s [%s] for command %s", role, group.name, cmd.name)
                    command_permissions.append(Application_Command_Permissions(
                        id=role,
                        type=Application_Command_Permission_Type.ROLE,
                        permission=True
                    ))
        log.debug("Adding permission for owner %s [%s] for command %s", client.cache[guild_id].guild.owner_id, guild_id, cmd.name)
        command_permissions.append(
            Application_Command_Permissions(
                id=client.cache[guild_id].guild.owner_id,
                type=Application_Command_Permission_Type.USER,
                permission=True
            )
        )
        if command_permissions != []:
            permissions.append(Guild_Application_Command_Permissions(
                id = cmd.id,
                permissions=command_permissions
            ))
    if permissions != []:
        log.info("Editing permissions on server %s for #%s commands", guild_id, len(permissions))
        await client.batch_edit_application_command_permissions(client.application.id, guild_id, permissions)
        client.cache[guild_id]._permissions_set = True

async def get_commands(client: Bot, guild: Guild = None) -> List[Application_Command]:
    if guild:
        return await client.get_guild_application_commands(client.application.id, guild.id)
    return await client.get_global_application_commands(client.application.id)

async def add_command(client: Bot, cmd: Application_Command, guild: Guild = None) -> Application_Command:
    if guild:
        log.info("Registering Guild [%s] command %s on bot %s", guild.id, cmd.name, client.username)
        return await client.create_guild_application_command(client.application.id, guild.id, cmd.name, cmd.description, cmd.options, cmd.default_permission, type=cmd.type)
    log.info("Registering Global command %s on bot %s", cmd.name, client.username)
    return await client.create_global_application_command(client.application.id, cmd.name, cmd.description, cmd.options, cmd.default_permission, type=cmd.type)

async def edit_command(client: Bot, cmd: Application_Command, guild: Guild = None) -> Application_Command:
    if guild:
        log.info("Editing existing Guild [%s] command %s on bot %s", guild.id, cmd.name, client.username)
        return await client.edit_guild_application_command(client.application.id, guild.id, cmd.id, cmd.name, cmd.description, cmd.options, cmd.default_permission)
    log.info("Editing existing Global command %s on bot %s", cmd.name, client.username)
    return await client.edit_global_application_command(client.application.id, cmd.id, cmd.name, cmd.description, cmd.options, cmd.default_permission)

async def delete_command(client: Bot, cmd: Application_Command, guild: Guild = None) -> None:
    if guild:
        log.info("Deleting Guild [%s] command %s from bot %s", guild.id, cmd.name, client.username)
        return await client.delete_guild_application_command(client.application.id, guild.id, cmd.id)
    log.info("Deleting Global command %s from bot %s", cmd.name, client.username)
    return await client.delete_global_application_command(client.application.id, cmd.id)

async def overwrite_commands(client: Bot, commands: List[Application_Command]=[], guild: Guild = None) -> List[Application_Command]:
    if guild:
        log.info("Overwriting Guild [%s] commands [%s] on bot %s", guild.id, len(commands), client.username)
        return await client.bulk_overwrite_guild_application_commands(client.application.id, guild.id, commands)
    log.info("Overwriting Global commands [%s] on bot %s", len(commands), client.username)
    return await client.bulk_overwrite_global_application_commands(client.application.id, commands)
