# -*- coding: utf-8 -*-
"""
Interactions
------------

Interaction commands registery & execution framework

:copyright: (c) 2021-2022 Mmesek
"""

from mlib import arguments

from MFramework import (
    Application_Command,
    Application_Command_Option_Type,
    Application_Command_Type,
    Bot,
    Groups,
    Guild,
    Message,
    Ready,
    log,
    onDispatch,
)

from .command import commands, iterate_commands

CLEAR_INTERACTIONS = getattr(arguments.parse(), "clear_interactions", False)
UPDATE_PERMISSIONS = getattr(arguments.parse(), "update_permissions", False)


@onDispatch(priority=101)
async def ready(client: Bot, ready: Ready):
    """Called after connecting with Discord. Preferably after receiving READY event"""
    if getattr(client, "registered", False):
        return
    client.application = await client.get_current_bot_application_information()
    await register_commands(client)


@onDispatch(priority=101)
async def guild_create(client: Bot, guild: Guild):
    """Called after GUILD_CREATE"""
    if not client.application:
        import asyncio

        await asyncio.sleep(3)
        return await guild_create(client, guild)

    _commands = await register_commands(client, guild)

    # if client.cache[guild.id]._permissions_set is False or UPDATE_PERMISSIONS:
    #    await set_permissions(client, guild.id, _commands)


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

    from MFramework.utils.localizations import LOCALIZATIONS

    for command, _command, options in iterate_commands(registered, guild.id if guild else None, client.user_id):
        cmd = Application_Command(
            name=command,
            description=_command.description[:100],
            options=options,
            default_permission=_command.group == Groups.GLOBAL,
        )
        cmd.name_localizations = {l: _command.translate(l, "name", default=command)[:100] for l in LOCALIZATIONS}
        cmd.description_localizations = {
            l: _command.translate(l, "description", default=_command.description)[:100] for l in LOCALIZATIONS
        }

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

    if len(new_commands) == len(commands) and len(registered) != 0 != len(commands):
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


async def get_commands(client: Bot, guild: Guild = None) -> list[Application_Command]:
    if guild:
        return await client.get_guild_application_commands(client.application.id, guild.id, True)
    return await client.get_global_application_commands(client.application.id, True)


async def add_command(client: Bot, cmd: Application_Command, guild: Guild = None) -> Application_Command:
    if guild:
        log.info(
            "Registering Guild [%s] command %s on bot %s",
            guild.id,
            cmd.name,
            client.username,
        )
        return await client.create_guild_application_command(
            client.application.id,
            guild.id,
            cmd.name,
            cmd.description,
            cmd.options,
            cmd.default_permission,
            type=cmd.type,
        )
    log.info("Registering Global command %s on bot %s", cmd.name, client.username)
    return await client.create_global_application_command(
        client.application.id,
        cmd.name,
        cmd.description,
        cmd.options,
        cmd.default_permission,
        type=cmd.type,
    )


async def edit_command(client: Bot, cmd: Application_Command, guild: Guild = None) -> Application_Command:
    if guild:
        log.info(
            "Editing existing Guild [%s] command %s on bot %s",
            guild.id,
            cmd.name,
            client.username,
        )
        return await client.edit_guild_application_command(
            client.application.id,
            guild.id,
            cmd.id,
            cmd.name,
            cmd.description,
            cmd.options,
            cmd.default_permission,
        )
    log.info("Editing existing Global command %s on bot %s", cmd.name, client.username)
    return await client.edit_global_application_command(
        client.application.id,
        cmd.id,
        cmd.name,
        cmd.description,
        cmd.options,
        cmd.default_permission,
    )


async def delete_command(client: Bot, cmd: Application_Command, guild: Guild = None) -> None:
    if guild:
        log.info(
            "Deleting Guild [%s] command %s from bot %s",
            guild.id,
            cmd.name,
            client.username,
        )
        return await client.delete_guild_application_command(client.application.id, guild.id, cmd.id)
    log.info("Deleting Global command %s from bot %s", cmd.name, client.username)
    return await client.delete_global_application_command(client.application.id, cmd.id)


async def overwrite_commands(
    client: Bot, commands: list[Application_Command] = [], guild: Guild = None
) -> list[Application_Command]:
    if guild:
        log.info(
            "Overwriting Guild [%s] commands [%s] on bot %s",
            guild.id,
            len(commands),
            client.username,
        )
        return await client.bulk_overwrite_guild_application_commands(client.application.id, guild.id, commands)
    log.info("Overwriting Global commands [%s] on bot %s", len(commands), client.username)
    return await client.bulk_overwrite_global_application_commands(client.application.id, commands)
