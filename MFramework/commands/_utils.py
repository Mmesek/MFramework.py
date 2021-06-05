from inspect import signature, Signature
from mdiscord.models import Application_Command

from mdiscord.types import GuildID

from MFramework import Snowflake, ChannelID, UserID, RoleID, Application_Command_Option, Application_Command_Option_Choice, Application_Command_Option_Type, Channel, User, Role, Guild_Member, Message, Enum

class Groups(Enum):
    SYSTEM = 0
    ADMIN = 1
    MODERATOR = 2
    NITRO = 3
    VIP = 4
    GLOBAL = 5
    DM = 6
    MUTED = 7
    LIMBO = 8

from typing import List, Dict, Any
class Argument:
    default: str
    type: type
    help: str
    choices: Dict[str, Any]
    def __init__(self, default, type, help, choices) -> None:
        self.default = default
        self.type = type
        self.help = help
        self.choices =choices

class Command:
    name: str
    func: object
    help: str
    arguments: Dict[str, Argument]
    interaction: bool
    master_command: object
    group: Groups
    sub_commands: List['Command']
    choices: Dict[str, 'Command']
    guild: Snowflake
    def __init__(self, f, interaction: bool = True, main: object = False, group: Groups = Groups.GLOBAL, guild: Snowflake = None) -> None:
        self.name = f.__name__
        self.func = f
        _docs = parse_docstring(f)
        self.help = _docs['_doc']
        self.arguments = parse_signature(f, _docs)
        self.interaction = interaction
        self.master_command = main
        self.group = group
        self.sub_commands = []
        self.choices = {}
        self.guild = guild
    def add_subcommand(self, cmd: 'Command'):
        self.sub_commands.append(cmd)
    def add_choice(self, name: str, func: 'Command'):
        self.choices[name] = func

commands: Dict[str, Command] = {}
aliasList: Dict[str, str] = {}

def detect_group(Client, user_id: Snowflake, guild_id: Snowflake, roles: Snowflake) -> Groups:
    if user_id != 273499695186444289:
        return Client.cache[guild_id].cachedRoles(roles)
    return Groups.SYSTEM

def is_nested(group: Groups, command: Command, name: str) -> Command:
    for sub_command in command.sub_commands:
        if name == sub_command.name:
            return sub_command
        if sub_command.sub_commands != []:
            return is_nested(group, sub_command, name)
    return command

def parse_signature(f, docstring):
    sig = signature(f).parameters
    parameters = {}
    for parameter in sig:
        arg = Argument(
            default = sig[parameter].default,
            type = sig[parameter].annotation,
            help = docstring.get(sig[parameter].name, 'MISSING DOCSTRING'),
            choices = docstring.get('choices').get(sig[parameter].name, []
                if not issubclass(sig[parameter].annotation, Enum) 
                else {k.name: k.value for k in sig[parameter]})
            )
        parameters[sig[parameter].name] = arg
    return parameters

def parse_docstring(f):
    docstring = {
        '_doc':f.__doc__.strip().split('Params',1)[0] if f.__doc__ else 'MISSING DOCSTRING',
        'choices':{}
    }
    doc = f.__doc__.split('Params',1) if f.__doc__ else ['']
    _params = []
    if len(doc) > 1:
        params = [i.strip() for i in doc[1].replace('-','').split('\n') if i.strip() != '']
        for x, param in enumerate(params):
            if param.strip() == 'Choices:':
                choices = {}
                for y, choice in enumerate(params[x:]):
                    if y == 0:
                        continue
                    elif choice[-1] == ':':
                        docstring['choices'][params[x-2].strip(':')] = choices
                        break
                    choices.update({i.strip():j.strip() for i,j in [choice.split(' = ')]})
            elif param[-1] == ':':
                _params.append((param.strip(':'),params[x+1]))
    for param in _params:
        docstring[param[0]] = param[1]
    return docstring

_types = {
    str: Application_Command_Option_Type.STRING,
    int: Application_Command_Option_Type.INTEGER,
    bool: Application_Command_Option_Type.BOOLEAN,
    Snowflake: Application_Command_Option_Type.STRING,
    ChannelID: Application_Command_Option_Type.CHANNEL,
    UserID: Application_Command_Option_Type.USER,
    RoleID: Application_Command_Option_Type.ROLE,
    Role: Application_Command_Option_Type.ROLE,
    Channel: Application_Command_Option_Type.CHANNEL,
    User: Application_Command_Option_Type.USER,
    Guild_Member: Application_Command_Option_Type.USER,
    GuildID: Application_Command_Option_Type.STRING
}

def parse_arguments(_command: Command) -> list:
    options = []
    for i in _command.arguments:
        if i.lower() in ['self', 'ctx', 'client', 'interaction']:
            continue
        elif i.lower() in ['data', 'args']:
            break
        elif i.lower() == 'message' and _command.arguments[i].type is Message:
            break
        _i = _command.arguments[i]
        choices = []
        for choice in _i.choices:
            choices.append(Application_Command_Option_Choice(name=choice, value=_i.choices[choice]))

        options.append(Application_Command_Option(
            type=_types.get(_i.type, Application_Command_Option_Type.STRING).value,
            name=i, description=_i.help[:100], required=True if _i.default is Signature.empty else False, choices=choices, options=[]
        ))
    for i in _command.sub_commands:
        options.append(Application_Command_Option(
            type= Application_Command_Option_Type.SUB_COMMAND if i.sub_commands == [] else Application_Command_Option_Type.SUB_COMMAND_GROUP,
            name=i.name, description=i.help[:100], options=parse_arguments(i), choices=[]
        ))
    return options

def iterate_commands(registered: List[Application_Command]=[], guild_id: Snowflake = None):
    for command, cmd in commands.items():
        if guild_id != cmd.guild or cmd.master_command or not cmd.interaction:
            continue
        _command = commands[command]
        options = parse_arguments(_command)
        for i in registered:
            if command == i.name:
                if i.options != options:
                    break
        else:
            if any(command == i.name for i in registered):
                continue
        yield command, _command, options


def set_default_arguments(ctx, f, kwargs):
    for arg in f.arguments:
        if arg not in kwargs:
            _type = f.arguments[arg].type
            if _type is ChannelID:
                i = ctx.channel_id
            elif _type is RoleID:
                i = ctx.guild_id
            elif _type is UserID:
                i = ctx.user_id
            elif _type is User:
                i = ctx.user
            elif _type is Guild_Member:
                i = ctx.member or Guild_Member()
                i.user = ctx.user
            elif _type is GuildID:
                i = ctx.guild_id
            else:
                continue
            kwargs[arg] = i
    return kwargs

from MFramework import Application_Command_Permissions, Application_Command_Permission_Type, log, Guild_Application_Command_Permissions
async def set_permissions(client, guild_id: Snowflake, _commands):
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
        if command_permissions != []:
            permissions.append(Guild_Application_Command_Permissions(
                id = cmd.id,
                permissions=command_permissions
            ))
    if permissions != []:
        log.info("Editing permissions on server %s for #%s commands", guild_id, len(permissions))
        await client.batch_edit_application_command_permissions(client.application.id, guild_id, permissions)
