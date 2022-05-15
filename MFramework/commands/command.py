from typing import List, Dict, Any, Type, Generator, Optional, Union, TYPE_CHECKING, Tuple
from types import FunctionType
from inspect import signature, Signature

from MFramework import (
    Snowflake,
    GuildID,
    ChannelID,
    UserID,
    RoleID,
    Channel,
    User,
    Role,
    Guild_Member,
    Message,
    Channel_Types,
    Application_Command,
    Application_Command_Option,
    Application_Command_Option_Choice,
    Application_Command_Option_Type,
    Embed,
    Component,
    Channel_Types,
    Interaction_Response,
    Interaction_Callback_Type,
    Interaction_Application_Command_Callback_Data,
    log,
    BadRequest,
    NotFound,
    Attachment,
    Interaction,
)
from . import Groups
from .components import Modal, TextInput, Row, Text_Input_Styles
from .exceptions import CooldownError, Error

LOCALIZATIONS = []
try:
    import i18n
    import os

    for path in i18n.load_path:
        for locale in os.listdir(path):
            if locale == "en":
                locale = "en-US"
            log.debug("Found directory for locale %s", locale)
            LOCALIZATIONS.append(locale)
except ImportError:
    log.debug("Package i18n not found. Localizations are unavailable")

if TYPE_CHECKING:
    from MFramework import Context


class Parameter:
    default: str
    type: type
    help: str
    choices: Dict[str, Any]
    kind: str
    name: str

    def __init__(
        self, default: str, type: Type, help: str, choices: Dict[str, Any], kind: str, name: str, types: List[str] = []
    ) -> None:
        self.default = default
        self.type = getattr(type, "__mbase__", type)
        if types and types != [""]:
            try:
                types = [Channel_Types.get("GUILD_" + i.upper()).value for i in types]
            except Exception as ex:
                breakpoint
        self.type_args = types or getattr(type, "__args__", [])
        self.help = help
        self.choices = choices
        self.kind = kind
        self.name = name


class Command:
    name: str
    func: object
    help: str
    arguments: Dict[str, Parameter]
    interaction: bool
    master_command: object
    group: Groups
    sub_commands: List["Command"]
    choices: Dict[str, "Command"]
    guild: Snowflake
    bot: Snowflake
    auto_deferred: bool
    private_response: bool
    modal: Interaction_Response

    def __init__(
        self,
        f: FunctionType,
        interaction: bool = True,
        main: object = False,
        group: Groups = Groups.GLOBAL,
        guild: Snowflake = None,
        main_only: bool = False,
        auto_defer: bool = True,
        private_response: bool = False,
        only_interaction: bool = False,
        only_message: bool = False,
        bot: Snowflake = None,
        **kwargs,
    ) -> None:
        self.name = f.__name__.strip("_")
        self.func = f
        _docs = parse_docstring(f)
        self.help = _docs["_doc"]
        self.arguments = parse_signature(f, _docs) if not main_only else {}
        self.auto_deferred = auto_defer
        self.modal = None
        if any(issubclass(arg.type, TextInput) for arg in self.arguments.values()):
            components = []
            for arg in self.arguments.values():
                if issubclass(arg.type, TextInput):
                    components.append(
                        Row(
                            TextInput(
                                label=arg.name.replace("_", " ").title(),
                                custom_id=str(arg.name),
                                style=Text_Input_Styles.Short
                                if int(arg.type.max_length) <= 150
                                else Text_Input_Styles.Paragraph,
                                min_length=int(arg.type.min_length),
                                max_length=int(arg.type.max_length),
                                placeholder=str(arg.default) if arg.default else None,
                                required=int(arg.type.min_length) > 0,
                            )
                        )
                    )
            self.modal = Interaction_Response(
                type=Interaction_Callback_Type.MODAL,
                data=Interaction_Application_Command_Callback_Data(
                    title=kwargs.get("modal_title") or self.name.replace("_", " ").title(),
                    custom_id=self.name + "-None",
                    components=components,
                ),
            )

        self._only_interaction = (
            only_interaction or self.arguments.get("Interaction", False) and not self.arguments.get("Message", False)
        )
        self._only_message = (
            only_message or self.arguments.get("Message", False) and not self.arguments.get("Interaction", False)
        )
        self.only_accept = Message if self._only_message else Interaction if self._only_interaction else None
        self.interaction = interaction
        self.master_command = main
        self.group = group
        self.sub_commands = []
        self.choices = {}
        self.guild = guild
        self.private_response = private_response
        self.bot = bot

    def add_subcommand(self, cmd: "Command"):
        self.sub_commands.append(cmd)

    def add_choice(self, name: str, func: "Command"):
        self.choices[name] = func

    async def execute(self, ctx: "Context", kwargs: Dict[str, Any]):
        try:
            r = await self.func(**kwargs)
            from MFramework import Emoji

            if isinstance(r, Message):
                await ctx.send(r.content, r.embeds, r.components)

            if isinstance(r, Embed) or (type(r) is list and all(isinstance(i, Embed) for i in r)):
                await self.maybe_reply(ctx, embeds=[r] if type(r) is not list else r)

            elif isinstance(r, Modal):
                await ctx.bot.create_interaction_response(
                    ctx.data.id,
                    ctx.data.token,
                    Interaction_Response(
                        type=Interaction_Callback_Type.MODAL,
                        data=Interaction_Application_Command_Callback_Data(
                            title=r.title, custom_id=r.custom_id, components=r.components
                        ),
                    ),
                )

            elif isinstance(r, Component) or (type(r) is list and all(isinstance(i, Component) for i in r)):
                await self.maybe_reply(ctx, components=[r] if type(r) is not list else r)

            elif isinstance(r, Emoji):
                if ctx.is_message:
                    await ctx.data.react(f"{r.name}:{r.id or 0}")
                else:
                    await self.maybe_reply(ctx, f"<{'a:' if r.animated else ''}{r.name}:{r.id or 0}>", prefix="")

            elif isinstance(r, Attachment) or (type(r) is list and all(isinstance(i, Attachment) for i in r)):
                await self.maybe_reply(ctx, attachments=[r] if type(r) is not list else r)

            elif callable(r):
                if hasattr(r, '_cmd'):
                    await ctx.bot.create_interaction_response(ctx.data.id, ctx.data.token, r._cmd.modal)

            elif r:
                await self.maybe_reply(ctx, str(r), prefix="")

            ctx.db.influx.commitCommandUsage(ctx.guild_id, self.name, ctx.bot.username, True, ctx.user_id)

        except TypeError as ex:
            log.exception("TypeError at command %s", self.name, exc_info=ex)
            if "missing" in str(ex):
                ex = str(ex).split(" ", 1)[1].replace("'", "`").capitalize()
            await self.maybe_reply(ctx, str(ex))

        except CooldownError as ex:
            log.debug("Cooldown triggered on command %s: %s", self.name, ex)
            from mlib.localization import secondsToText

            await self.maybe_reply(
                ctx, secondsToText(int(ex.args[0].total_seconds())), prefix="<@{user_id}>, Remaining Cooldown: "
            )

        except Error as ex:
            log.debug("Error at command %s: %s", self.name, ex)
            await self.maybe_reply(ctx, str(ex), prefix="<@{user_id}>: ")

        except BadRequest as ex:
            log.error(ex)
            _dm = ctx.bot.cfg.get(ctx.bot.username.lower(), {}).get("log_dm", None)

            if _dm:
                await ctx.bot.create_message(_dm, str(ex))

            ctx.db.influx.commitCommandUsage(ctx.guild_id, self.name, ctx.bot.username, False, ctx.user_id)

        except NotFound as ex:
            log.warning("%s Not Found", ex.path)
            await self.maybe_reply(
                ctx,
                f"Couldn't find Discord resource and respond, possibly due to expired interaction :( {'Try again.' if 'callback' in ex.path else ''}",
            )

        except Exception as ex:
            log.exception("Exception occured during command execution", exc_info=ex)
            ctx.db.influx.commitCommandUsage(ctx.guild_id, self.name, ctx.bot.username, False, ctx.user_id)
            await self.maybe_reply(ctx, str(ex))
            _dm = ctx.bot.cfg.get(ctx.bot.username.lower(), {}).get("log_dm", None)
            if _dm:
                await ctx.bot.create_message(_dm, str(ex))

    async def maybe_reply(
        self,
        ctx: "Context",
        msg: str = None,
        prefix: str = "<@{user_id}> an exception occured: ",
        embeds: List[Embed] = None,
        components: List[Component] = None,
        attachments: List[Attachment] = None,
    ):
        if msg:
            s = "{prefix}{msg}".format(prefix=prefix, msg=msg).format(user_id=ctx.user_id)
        else:
            s = None

        try:
            await ctx.reply(s, embeds=embeds, components=components, attachments=attachments)
        except Exception:
            log.debug("Failed to reply to message. Falling back to default Message creation")
            await ctx.bot.create_message(ctx.channel_id, s, embeds=embeds, components=components)


commands: Dict[str, Command] = {}
aliasList: Dict[str, str] = {}
COMPILED_REGEX: Dict[str, str] = {}
commands_regex: Dict[str, Command] = {}
command_shortcuts: Dict[str, Tuple[Command, Dict[str, Any]]] = {}
reactions: Dict[str, Command] = {}


def parse_signature(f: FunctionType, docstring: Dict[str, Any]) -> Dict[str, Parameter]:
    sig = signature(f).parameters
    parameters = {}
    for parameter in sig:
        import enum

        arg = Parameter(
            default=sig[parameter].default,
            type=sig[parameter].annotation
            if type(sig[parameter].annotation) is type or type(sig[parameter].annotation) is enum.EnumMeta
            else type(sig[parameter].annotation),
            help=docstring.get(sig[parameter].name, "MISSING DOCSTRING").strip(),
            choices=docstring.get("choices").get(
                sig[parameter].name,
                []
                if type(sig[parameter].annotation) is not dict and not issubclass(sig[parameter].annotation, enum.Enum)
                else sig[parameter].annotation
                if type(sig[parameter].annotation) is dict
                else {k.name: k.value for k in sig[parameter].annotation},
            ),
            kind=sig[parameter].kind.name,
            name=sig[parameter].name.strip(),
            types=docstring.get("_types", {}).get(sig[parameter].name.strip()),
        )
        parameters[sig[parameter].name] = arg
    return parameters


def parse_docstring(f: FunctionType) -> Dict[str, Union[str, Dict[str, str]]]:
    docstring = {
        "_doc": f.__doc__.strip().split("Params", 1)[0].strip() if f.__doc__ else "MISSING DOCSTRING",
        "_types": {},
        "choices": {},
    }
    doc = f.__doc__.split("Params", 1) if f.__doc__ else [""]
    _params = []
    if len(doc) > 1:
        params = [i.strip() for i in doc[1].replace("-", "").split("\n") if i.strip() != ""]
        for x, param in enumerate(params):
            if param.strip() == "Choices:":
                choices = {}
                for y, choice in enumerate(params[x:]):
                    if y == 0:
                        continue
                    elif choice[-1] == ":":
                        docstring["choices"][params[x - 2].strip(":")] = choices
                        break
                    choices.update({i.strip(): j.strip() for i, j in [choice.split(" = ")]})
                docstring["choices"][params[x - 2].strip(":")] = choices
            elif param[-1] == ":":
                _params.append((param.strip(":"), params[x + 1]))
            if param.strip().lower().startswith("channel:"):
                p = param.split(":", 1)
                if len(p) > 1:
                    docstring["_types"][p[0]] = [i.strip() for i in param.strip().split(":", 1)[1].split(",")]
                    docstring[p[0]] = params[x + 1]
    for param in _params:
        docstring[param[0]] = param[1].strip()
    return docstring


class Mentionable(Snowflake):
    """Snowflake representing any (User, Role or Channel) mentionable object"""

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
    Channel_Types: Application_Command_Option_Type.CHANNEL,
    User: Application_Command_Option_Type.USER,
    Guild_Member: Application_Command_Option_Type.USER,
    GuildID: Application_Command_Option_Type.STRING,
    Mentionable: Application_Command_Option_Type.MENTIONABLE,
    float: Application_Command_Option_Type.NUMBER,
    Attachment: Application_Command_Option_Type.ATTACHMENT,
    Message: Message,
}


def parse_arguments(_command: Command) -> List[str]:
    options = []
    for i, v in _command.arguments.items():
        if i.lower() in ["self", "ctx", "cls", "client", "interaction"]:
            continue
        elif v.kind in {"VAR_POSITIONAL", "KEYWORD_ONLY"}:
            break
        elif i.lower() == "_message" and _command.arguments[i].type is Message:
            break
        elif any(issubclass(v.type, t) for t in {TextInput}):
            continue
        _i = _command.arguments[i]
        choices = []
        for choice in _i.choices:
            name_localized = {}
            for locale in LOCALIZATIONS:
                from mlib.localization import check_translation

                name_localized[locale] = check_translation(
                    f"commands.{_command.name}.{i.lower()}.{choice.strip()}", locale, choice.strip()
                )
            _choice = Application_Command_Option_Choice(name=choice.strip(), value=_i.choices[choice])
            _choice.name_localizations = name_localized
            if _i.type in {int, bool}:
                # Workaround due to currently autocasting to str by constructor
                _choice.value = _i.type(_choice.value)
            # NOTE: This workaround is needed when value is of different type than str, which is possible. Come on, don't comment it out :madge:
            choices.append(_choice)

        a = Application_Command_Option(
            name=i.strip(),
            description=_i.help[:100].strip(),
            required=True if _i.default is Signature.empty else False,
            choices=choices,
            options=[],
            channel_types=_i.type_args,
        )

        name_localized = {}
        desc_localized = {}
        for locale in LOCALIZATIONS:
            from mlib.localization import check_translation

            name_localized[locale] = check_translation(f"commands.{_command.name}.{i.lower()}.name", locale, i.strip())
            desc_localized[locale] = check_translation(
                f"commands.{_command.name}.{i.lower()}.description", locale, _i.help[:100]
            )
        a.name_localizations = name_localized
        a.description_localizations = desc_localized

        a.type = _types.get(
            _i.type,
            Application_Command_Option_Type.INTEGER
            if issubclass(_i.type, int)
            else Application_Command_Option_Type.STRING,
        )
        options.append(a)
    for i in _command.sub_commands:
        options.append(
            Application_Command_Option(
                type=Application_Command_Option_Type.SUB_COMMAND
                if i.sub_commands == []
                else Application_Command_Option_Type.SUB_COMMAND_GROUP,
                name=i.name.strip(),
                description=i.help[:100].strip(),
                options=parse_arguments(i),
                choices=[],
            )
        )
    return options


def iterate_commands(
    registered: List[Application_Command] = [], guild_id: Optional[Snowflake] = None, bot_id: Optional[Snowflake] = None
) -> Generator[Tuple[str, Command, List[str]], None, None]:
    for command, cmd in commands.items():
        if guild_id != cmd.guild or cmd.master_command or not cmd.interaction or (cmd.bot and cmd.bot != bot_id):
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