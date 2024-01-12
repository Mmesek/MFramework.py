import re

from typing import List, TYPE_CHECKING, Union

from MFramework import (
    Interaction,
    Application_Command_Option_Type,
    Interaction_Type,
    Snowflake,
    Message,
    Interaction_Type,
    ChannelID,
    RoleID,
    UserID,
    User,
    Guild_Member,
    GuildID,
    Groups,
)
from .command import Command, commands, aliasList
from .exceptions import MissingPermissions, WrongContext, CommandNotFound, SoftError

if TYPE_CHECKING:
    from MFramework import Bot, Context

DEFAULTS = {
    ChannelID: "channel_id",
    RoleID: "guild_id",
    UserID: "user_id",
    User: "user",
    Guild_Member: "member",
    GuildID: "guild_id",
}

_FIRST_CHAR = re.compile("^")


def get_name(data: Union[Message, Interaction]) -> str:
    """Retrieves command name from arguments"""
    if type(data) is Interaction:
        if data.type is not Interaction_Type.MODAL_SUBMIT:
            return data.data.name
        return data.data.custom_id.split("-", 1)[0]
    name = get_arguments(data._Client, data)
    name = get_original_cmd(name[0])

    if not name:
        raise CommandNotFound

    return name


def get_arguments(client: "Bot", message: Message) -> List[str]:
    """Retrieve list of arguments from text"""
    if message.guild_id:
        alias = client.cache[message.guild_id].alias
    else:
        alias = _FIRST_CHAR

    if not alias.search(message.content):
        raise SoftError()

    args = alias.split(message.content, 1)[-1].strip()
    args = args.split(" ")
    return args
    kwargs = {"positional": args.split(" ")}
    # for argument in ARGUMENTS.finditer(args):
    #    kwargs[argument.group("parameter")] = argument.group("argument")
    return kwargs


def retrieve_command(data: Union[Message, Interaction]) -> Command:
    name = get_name(data)

    cmd = commands.get(name)
    if type(data) is Interaction:
        cmd = unnest_interaction(data, None, cmd)
    else:
        if "." in name:
            for sub in name.split("."):
                if sub in commands:
                    cmd = commands.get(sub)
                if cmd:
                    cmd = is_nested(None, cmd, sub)

    # if not cmd and type is Interaction:
    #    cmd = components.get(name)

    if not cmd:
        raise CommandNotFound(name)

    if cmd.only_accept and cmd.only_accept is not type(data):
        raise WrongContext(type(data), cmd.only_accept)

    return cmd


def unnest_interaction(interaction: Interaction, group: Groups, cmd: Command):
    """Returns nested command"""
    if len(interaction.data.options) and interaction.data.options[0].type in {
        Application_Command_Option_Type.SUB_COMMAND_GROUP,
        Application_Command_Option_Type.SUB_COMMAND,
    }:
        cmd = is_nested(group, cmd, interaction.data.options[0].name)
        interaction.data.options = interaction.data.options[0].options

        return unnest_interaction(interaction, group, cmd)
    return cmd


def get_original_cmd(_name: str) -> str:
    return aliasList.get(_name.lower(), _name)


def set_context(client: "Bot", cmd: Command, data: Union[Message, Interaction]) -> "Context":
    """Sets Context. Raises MissingPermissions"""
    ctx: "Context" = client._Context(client.cache, client, data, cmd=cmd)

    if not ctx.permission_group.can_use(cmd.group):
        raise MissingPermissions(ctx.permission_group, cmd.group)

    return ctx


def detect_group(Client: "Bot", user_id: Snowflake, guild_id: Snowflake, roles: Snowflake) -> Groups:
    if user_id != 273499695186444289:
        if user_id != Client.cache[guild_id].guild.owner_id:
            return Client.cache[guild_id].cached_roles(roles)
        return Groups.OWNER
    return Groups.SYSTEM


def is_nested(group: Groups, command: Command, name: str) -> Command:
    for sub_command in command.sub_commands:
        if name.lower() == sub_command.name.lower():
            return sub_command
        if sub_command.sub_commands != []:
            nested = is_nested(group, sub_command, name)
            if nested != sub_command:
                return nested
    return command
