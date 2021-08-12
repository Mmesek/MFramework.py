from typing import List, Dict, Any, Type, Generator, Optional, Union, TYPE_CHECKING, Tuple
from types import FunctionType
from inspect import signature, Signature

from MFramework import (Snowflake, GuildID, ChannelID, UserID, RoleID, 
    Channel, User, Role, Guild_Member, Message, Enum, Guild_Member_Update,
    Application_Command, Application_Command_Option, Application_Command_Option_Choice, Application_Command_Option_Type,
    log, BadRequest
    )

if TYPE_CHECKING:
    from MFramework import Bot, Context

class Groups(Enum):
    SYSTEM = 0
    OWNER = 5
    ADMIN = 10
    MODERATOR = 20
    HELPER = 30
    SUPPORT = 40
    PARTNER = 50
    NITRO = 60
    SUPPORTER = 70
    VIP = 80
    GLOBAL = 100
    DM = 200
    MUTED = 210
    LIMBO = 220
    def can_use(cls, value: 'Groups') -> bool:
        '''Checks if Group is higher or equal than provided one
        Params
        ------
        value:
            Group to compare to. For example, Minimal group that can use'''
        return cls.value <= value.value

class Argument:
    default: str
    type: type
    help: str
    choices: Dict[str, Any]
    kind: str
    name: str
    def __init__(self, default: str, type: Type, help: str, choices: Dict[str, Any], kind: str, name: str) -> None:
        self.default = default
        self.type = type
        self.help = help
        self.choices =choices
        self.kind = kind
        self.name = name

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
    def __init__(self, f: FunctionType, interaction: bool = True, main: object = False, group: Groups = Groups.GLOBAL, guild: Snowflake = None, main_only: bool=False) -> None:
        self.name = f.__name__.strip("_")
        self.func = f
        _docs = parse_docstring(f)
        self.help = _docs['_doc']
        self.arguments = parse_signature(f, _docs) if not main_only else {}
        self._only_interaction = self.arguments.get("Interaction", False) and not self.arguments.get("Message", False)
        self._only_message = self.arguments.get("Message", False) and not self.arguments.get("Interaction", False)
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
    async def execute(self, ctx: 'Context', kwargs: Dict[str, Any]):
        try:
            await self.func(**kwargs)
        except TypeError as ex:
            if 'missing' in str(ex):
                ex = str(ex).split(' ', 1)[1].replace("'", '`').capitalize()
            await self.maybe_reply(ctx, ex)
        except Error as ex:
            await self.maybe_reply(ctx, ex)
        except BadRequest as ex:
            log.error(ex)
        except Exception as ex:
            log.exception("Exception occured during command execution", exc_info=ex)
            await self.maybe_reply(ctx, str(ex))
    async def maybe_reply(self, ctx: 'Context', msg: str):
        try:
            await ctx.reply(str(msg))
        except Exception:
            log.debug("Failed to reply to message. Falling back to default Message creation")
            await ctx.bot.create_message(ctx.channel_id, str(msg))

class Error(Exception):
    pass

class CooldownError(Error):
    pass

commands: Dict[str, Command] = {}
aliasList: Dict[str, str] = {}
COMPILED_REGEX: Dict[str, str] = {}
commands_regex: Dict[str, Command] = {}
command_shortcuts: Dict[str, Tuple[Command, Dict[str, Any]]] = {}
reactions: Dict[str, Command] = {}

def detect_group(Client: 'Bot', user_id: Snowflake, guild_id: Snowflake, roles: Snowflake) -> Groups:
    if user_id != 273499695186444289:
        if user_id != Client.cache[guild_id].guild.owner_id:
            return Client.cache[guild_id].cachedRoles(roles)
        return Groups.OWNER
    return Groups.SYSTEM

def is_nested(group: Groups, command: Command, name: str) -> Command:
    for sub_command in command.sub_commands:
        if name.lower() == sub_command.name.lower():
            return sub_command
        if sub_command.sub_commands != []:
            return is_nested(group, sub_command, name)
    return command

def parse_signature(f: FunctionType, docstring: Dict[str, Any]) -> Dict[str, Argument]:
    sig = signature(f).parameters
    parameters = {}
    for parameter in sig:
        import enum
        arg = Argument(
            default = sig[parameter].default,
            type = sig[parameter].annotation,
            help = docstring.get(sig[parameter].name, 'MISSING DOCSTRING').strip(),
            choices = docstring.get('choices').get(sig[parameter].name, []
                if not issubclass(sig[parameter].annotation, enum.Enum) 
                else {k.name: k.value for k in sig[parameter].annotation}),
            kind = sig[parameter].kind.name,
            name = sig[parameter].name.strip()
            )
        parameters[sig[parameter].name] = arg
    return parameters

def parse_docstring(f: FunctionType) -> Dict[str, Union[str, Dict[str, str]]]:
    docstring = {
        '_doc':f.__doc__.strip().split('Params',1)[0].strip() if f.__doc__ else 'MISSING DOCSTRING',
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
        docstring[param[0]] = param[1].strip()
    return docstring

class Mentionable(Snowflake):
    '''Snowflake representing any (User, Role or Channel) mentionable object'''
    pass

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
    GuildID: Application_Command_Option_Type.STRING,
    Mentionable: Application_Command_Option_Type.MENTIONABLE,
    float: Application_Command_Option_Type.NUMBER
}

def parse_arguments(_command: Command) -> List[str]:
    options = []
    for i, v in _command.arguments.items():
        if i.lower() in ['self', 'ctx', 'client', 'interaction']:
            continue
        elif v.kind in {'VAR_POSITIONAL', 'KEYWORD_ONLY'}:
            break
        elif i.lower() == 'message' and _command.arguments[i].type is Message:
            break
        _i = _command.arguments[i]
        choices = []
        for choice in _i.choices:
            choices.append(Application_Command_Option_Choice(name=choice.strip(), value=_i.choices[choice]))

        options.append(Application_Command_Option(
            type=_types.get(_i.type,
                Application_Command_Option_Type.INTEGER if issubclass(_i.type, int) else 
                Application_Command_Option_Type.STRING).value,
            name=i.strip(), description=_i.help[:100].strip(), required=True if _i.default is Signature.empty else False, choices=choices, options=[]
        ))
    for i in _command.sub_commands:
        options.append(Application_Command_Option(
            type= Application_Command_Option_Type.SUB_COMMAND if i.sub_commands == [] else Application_Command_Option_Type.SUB_COMMAND_GROUP,
            name=i.name.strip(), description=i.help[:100].strip(), options=parse_arguments(i), choices=[]
        ))
    return options

def iterate_commands(registered: List[Application_Command]=[], guild_id: Optional[Snowflake] = None) -> Generator[Tuple[str, Command, List[str]], None, None]:
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


def set_default_arguments(ctx: 'Context', f: Command, kwargs: Dict[str, Any]) -> Dict[str, Any]:
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

def add_extra_arguments(f: Command, _kwargs: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    for arg, value in kwargs.items():
        if arg in f.arguments and f.arguments[arg].kind not in {'KEYWORLD_ONLY'}:
            _kwargs[arg] = value
    return _kwargs

def strip_extra_arguments(f: Command, kwargs: Dict[str, Any]) -> Dict[str, Any]:
    for arg in kwargs:
        if arg not in f.arguments:
            kwargs.pop(arg)
    return kwargs

def get_trigger(client: 'Bot', message: Message) -> str:
    alias = client.cache[message.guild_id].alias
    if alias not in message.content[0] and client.username.lower() not in message.content.lower() and str(client.user_id) not in message.content:
        return False
    return alias

def get_arguments(client: 'Bot', message: Message) -> List[str]:
    args = message.content
    if client.username.lower() in message.content.lower():
        args = message.content.split(client.username, 1)[-1]
    elif str(client.user_id) in message.content:
        args = message.content.split(f'{client.user_id}>', 1)[-1]
    args = args.strip().split(' ')
    return args

def get_original_cmd(_name: str) -> str:
    return aliasList.get(_name.lower(), _name)

def set_ctx(client: 'Bot', message: Message, f: Command) -> 'Context':
    from MFramework import Context
    ctx = Context(client.cache, client, message)
    if not f or f.group < ctx.permission_group:
        return False
    return ctx

def set_kwargs(ctx: 'Context', f: Command, args: List[str]) -> Dict[str, Any]:
    # NOTE: Argument doesn't support any form of List. Neither it supports -flags or specifying keyword arguments at all  
    kwargs = {}
    
    flags = {i[0]:i[1] for i in [j.strip('-').split('=',1) for j in filter(lambda x: x.startswith('-') and '=' in x, args)]}
    args = list(filter(lambda x: not x.startswith('-') and x, args))
    positional = list(filter(lambda x: x.kind == 'POSITIONAL_OR_KEYWORD', f.arguments.values()))
    for x, option in enumerate(list(f.arguments.values())[1:]):
        from MFramework.utils.utils import parseMention
        if x >= len(args):
            break
        if option.type in {str, int, bool, float} or issubclass(option.type, Snowflake):
            if issubclass(option.type, Snowflake):
                args[x] = parseMention(args[x])
            if option.kind == 'POSITIONAL_OR_KEYWORD':
                kwargs[option.name] = option.type(args[x]) if option.name != positional[-1].name else " ".join(args[x:])
            elif option.kind == 'KEYWORD_ONLY' and option.name in flags:
                kwargs[option.name] = option.type(flags[option.name])
            elif option.kind == 'VAR_POSITIONAL':
                kwargs[option.name] = args[x:]
        elif option.type in {User, Channel, Role, Guild_Member}:
            mentions = {
                User: ctx.data.mentions,
                Guild_Member: ctx.data.mentions,
                Channel: ctx.data.mention_channels,
                Role: ctx.data.mention_roles
            }
            caches = {
                User: ctx.cache.members,
                Guild_Member: ctx.cache.members,
                Channel: ctx.cache.channels,
                Role: ctx.cache.roles
            }
            _id = Snowflake(parseMention(args[x]))
            mentioned = list(filter(lambda i: i.id == _id, mentions.get(option.type)))
            if not mentioned or option.type is Guild_Member:
                mentioned = [caches.get(option.type).get(_id, Guild_Member(user=User(id=_id, username=_id)))]
            if option.type is User and type(mentioned[0]) in {Guild_Member, Guild_Member_Update}:
                mentioned = [mentioned[0].user]
            kwargs[option.name] = mentioned[0]
    return set_default_arguments(ctx, f, kwargs)
