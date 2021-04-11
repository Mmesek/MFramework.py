from inspect import signature, Signature

from mdiscord.types import GuildID

from MFramework import Snowflake, ChannelID, UserID, RoleID, Application_Command_Option, Application_Command_Option_Choice, Application_Command_Option_Type, Enum, Channel, User, Role, Guild_Member, Message

#from enum import Enum
class Groups(Enum):
    SYSTEM = 0
    ADMIN = 1
    MODERATOR = 2
    NITRO = 3
    VIP = 4
    GLOBAL = 5
    DM = 6
    MUTED = 7

group_names = {
    "System": 0,
    "Admin": 1,
    "Mod": 2,
    "Nitro": 3,
    "Vip": 4,
    "Global": 5,
    "Muted": 7
}

commands = {}
for group in Groups:
    commands[group] = {}

def detect_group(Client, user_id: Snowflake, guild_id: Snowflake, roles: Snowflake) -> Groups:
    if user_id != 273499695186444289:
        return Groups(group_names.get(Client.cache[guild_id].cachedRoles(roles).title(), 5)) #FIXME
    return Groups.SYSTEM

def find_command(group: Groups=Groups.GLOBAL, command: str="") -> dict:
    _groups = list(commands.keys())
    for current_group in list(_groups)[_groups.index(group):]:
        if command in commands[current_group]:
            return commands[current_group][command]

def is_nested(group: Groups, command: dict, name: str) -> dict:
    for sub_command in command["sub_commands"]:
        f = find_command(group, sub_command['name'])
        if name == sub_command['name']:
            return f
        if sub_command.get('sub_commands',[]) != []:
            return is_nested(group, f, name)
    return command

def parse_signature(f, docstring):
    sig = signature(f).parameters
    parameters = {}
    for parameter in sig:
        parameters[sig[parameter].name] = {
            'default': sig[parameter].default,# if sig[parameter].default is not Signature.empty else False,
            'type': sig[parameter].annotation,
            'help': docstring.get(sig[parameter].name, 'MISSING DOCSTRING'),
            'choices': docstring.get('choices').get(sig[parameter].name, []) 
                if not issubclass(sig[parameter].annotation, Enum) 
                else {k.name: k.value for k in sig[parameter]}
        }
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
        #TODO #FIXME #DONE? Add support for choices. 
        # Possible way: Split line if "Choices:"
        # Choices:
        #   A = 1
        #   B = 2
        #   C = 3
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
        
#    docstring = {
#        '_doc':f.__doc__.strip().split('Params',1)[0] or 'MISSING DOCSTRING', 
#        'choices':{'argument...':{'a':'e'}}, 
#        'argument...':'...'} #FIXME
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

def parse_arguments(_command: dict) -> list:
    options = []
    for i in _command['arguments']:
        if i.lower() in ['self', 'ctx', 'client', 'interaction']:
            continue
        elif i.lower() in ['data', 'args']:
            break
        elif i.lower() == 'message' and _command['arguments'][i]['type'] is Message:
            break
        _i = _command['arguments'][i]
        choices = []
        for choice in _i['choices']:
            choices.append(Application_Command_Option_Choice(name=choice, value=_i['choices'][choice]))

        options.append(Application_Command_Option(
            type=_types.get(_i['type'], Application_Command_Option_Type.STRING).value,
            name=i, description=_i['help'][:100], required=True if _i['default'] is Signature.empty else False, choices=choices, options=[] #FIXME default empty compare?
        ))
    for i in _command.get('sub_commands',[]):
        options.append(Application_Command_Option(
            type= Application_Command_Option_Type.SUB_COMMAND if i.get('sub_commands', None) is None else Application_Command_Option_Type.SUB_COMMAND_GROUP,
            name =i['name'], description=i['help'][:100], options=parse_arguments(i), choices=[]
        ))
    #TODO Support for subcommands #Done?
    return options

def iterate_commands(registered: list=[]):
    _groups = list(commands.keys())
    for current_group in _groups[_groups.index(Groups.GLOBAL)::-1]:
        for command in commands[current_group]:
            _command = commands[current_group][command]
            options = parse_arguments(_command)
            for i in registered:
                if command == i.name:
                    if i.options != options:
                        break
            else:
                if any(command == i.name for i in registered):
                    continue
            yield command, _command, options
