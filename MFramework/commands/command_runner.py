import re

from typing import Dict, List, TYPE_CHECKING, Union
from datetime import timedelta
from MFramework import (
    onDispatch,
    Interaction,
    Message,
    Interaction_Type,
    Component_Types,
    Embed,
    RoleID,
    UserID,
    ChannelID,
    Role,
    User,
    Channel,
    Guild_Member,
    Snowflake,
    Attachment,
)
from MFramework.commands._utils import (
    Command,
    DEFAULTS,
    commands,
    set_context,
    get_original_cmd,
    CommandNotFound,
    WrongContext
)

if TYPE_CHECKING:
    from MFramework import Context, Bot


#ARGUMENTS = re.compile("")


def get_name(data: Union[Message, Interaction]) -> str:
    """Retrieves command name from arguments"""
    if type(data) is Interaction:
        if data.type is not Interaction_Type.MODAL_SUBMIT:
            name = data.data.name
        else:
            name = data.data.custom_id.split("-", 1)[0]
    else:
        name = get_arguments(data._Client, data)
        name = name[0]
    name = get_original_cmd(name)
    return name


def get_arguments(client: "Bot", message: Message) -> List[str]:
    """Retrieve list of arguments from text"""
    args = client.cache[message.guild_id].alias.split(message.content, 1)[-1].strip()
    args = args.split(" ")
    return args
    kwargs = {"positional": args.split(" ")}
    # for argument in ARGUMENTS.finditer(args):
    #    kwargs[argument.group("parameter")] = argument.group("argument")
    return kwargs


class Arguments(dict):
    def __init__(self, cmd: Command, ctx: "Context", kwargs={}) -> None:
        self.kwargs = {}
        self.cmd = cmd
        self.ctx = ctx
        self._kwargs = kwargs
        args = self._get_arguments()
        self._set_kwargs(args)
        if not ctx.data.data.options and ctx.data.data.resolved:
            self._set_resolved()
        self._set_defaults()
        self._add_extra(ctx=ctx, client=ctx.bot, interaction=ctx.data, message=ctx.data, language="en")

    def _get_arguments(self):
        """Get arguments"""
        if self.ctx.is_interaction:
            return {option.name: option.value for option in self.ctx.data.data.options}
        args = iter(get_arguments(self.ctx.bot, self.ctx.data))
        return {name: next(args) for name in self.cmd.arguments}

    def _set_kwargs(self, arguments: Dict[str, str]):
        """Sets arguments as keywords as well as casts to correct types"""
        for name, value in arguments.items():
            t = self.cmd.arguments[name].type

            if issubclass(t, Snowflake) and not value.isdigit():
                from MFramework.utils.utils import parseMention

                value = parseMention(value)

            if t not in [Channel, Role, User, Guild_Member, ChannelID, UserID, RoleID, Attachment]:
                if type(value) is str and value.isdigit():
                    value = int(value)

                elif t is timedelta:
                    from mlib.converters import total_seconds

                    v = total_seconds(value)

                elif t is dict:
                    v = ({v: k for k, v in self.cmd.arguments[name].choices.items()}.get(value), value)

                else:
                    v = self.cmd.arguments[name].type(value)

                self.kwargs[name] = v

            elif issubclass(t, Snowflake):
                # We are casting it to Snowflake due to some recursion error.
                # Otherwise, the above should be sufficient
                self.kwargs[name] = Snowflake(value)

            else:
                if self.ctx.is_interaction:
                    o = getattr(self.ctx.data.data.resolved, t.__name__.lower().replace("guild_", "") + "s", {}).get(
                        str(value), t()
                    )

                    if t is Guild_Member:
                        o.user = self.ctx.data.data.resolved.users.get(str(value), User())
                else:
                    # TODO: Version for message based!
                    o = None

                self.kwargs[name] = o

    def _set_resolved(self):
        # TODO: Fetch from cache in case of missing 
        for arg in self.cmd.arguments.values():
            if arg.type in {Guild_Member, User, UserID, Channel, Role, ChannelID, RoleID, Message}:
                t = self.cmd.arguments[arg.name].type
                if self.ctx.is_interaction:
                    o = list(
                        getattr(
                            self.ctx.data.data.resolved, t.__name__.lower().replace("guild_", "") + "s", {}
                        ).values()
                    )
                    o = o[0] if o else t()
                    if t is Guild_Member:
                        _user = list(self.ctx.data.data.resolved.users.values())[0]
                        o.user = _user or User()
                else:
                    # TODO: Branch for messages
                    pass
                self.kwargs[arg.name] = o

    def _set_defaults(self):
        """Sets default arguments when they are missing"""
        self.kwargs.update(
            {
                k: getattr(self.ctx, DEFAULTS.get(v.type, "None"), None)
                for k, v in self.cmd.arguments.items()
                if k not in self.kwargs
            }
        )

    def _add_extra(self, **kwargs):
        """Set extra arguments like built-in/library ones like language"""
        if self.ctx.is_interaction:
            key = "interaction"
        else:
            key = "message"
        _k = {key:self.ctx.data, "language": self.ctx.language or "en"}
        for arg, value in kwargs.items():
            if arg in self.cmd.arguments and self.cmd.arguments[arg].kind not in {"KEYWORLD_ONLY"}:
                if arg not in self.kwargs:
                    # Make sure we are not overwriting, just in case
                    self.kwargs[arg] = value


async def modal_response(bot: "Bot", data: Union[Message, Interaction], cmd: Command) -> Dict[str, str]:
    """Responds with modal for interactions, or with message based questions awaiting each input"""
    if type(data) is Interaction:
        await bot.create_interaction_response(data.id, data.token, response=cmd.modal)
        # NOTE: This way we can take additional arguments from regular command and can merge both.
        # Modals are usually ephemeral so timeout shouldn't be a problem.
        # However in case of "raw" Modal input, we still need legacy way to support while making modals from params
        interaction: Interaction = await bot.wait_for(
            "interaction_create",
            check=lambda _data: _data.type == Interaction_Type.MODAL_SUBMIT
            and _data.data.custom_id == cmd.modal.data.custom_id
            and (_data.member.user.id == data.user.id if not data.guild_id else _data.user.id == data.user.id),
            timeout=300,
            # NOTE: If somehow someone sends a modal after timeout expires, it should be handled by separate flow
        )
        return parse_modal_submit(interaction)

    # NOTE: This is message-based way to take parameters, considering modals are nicer, this is entirely useless
    # TODO: Extend this to take regular parameters in case of message-based command with partial arguments
    inputs = {}

    for text_input in cmd.modal.data.components:
        text_input = text_input.components[0]
        e = Embed()
        e.set_title(text_input.label)
        e.set_description(text_input.placeholder)
        e.add_field("Minimum characters", str(text_input.min_length), True)
        e.add_field("Maximum characters", str(text_input.max_length), True)
        e.add_field("Required", "Yes" if text_input.required else "Skip by sending `-`", True)
        await data.reply(embeds=[e])
        msg: Message = await bot.wait_for(
            "message_create" if not data.guild_id else "direct_message_create",
            check=lambda x: x.author.id == data.author.id
            and x.channel_id == data.channel_id
            and (
                (len(x.content) <= text_input.max_length and len(x.content) >= text_input.min_length)
                or (not text_input.required and x.content == "-")
            ),
            timeout=300,
        )
        inputs[text_input.label.lower().replace(" ", "_")] = msg.content

    return inputs


async def parse_modal_submit(interaction: Interaction):
    inputs = {}

    for row in interaction.data.components:
        # NOTE: This will work only for TextInput, it'll require updating when Modals will support more types!
        for text_input in filter(lambda x: x.type == Component_Types.TEXT_INPUT, row.components):
            inputs[text_input.custom_id.split("-", 1)[-1]] = text_input.value

    return inputs


def retrieve_command(name: str, type: type) -> Command:
    cmd = commands.get(name)
    if not cmd and type is Interaction:
        cmd = components.get(name)

    if not cmd:
        raise CommandNotFound(name)

    if cmd.only_accept and cmd.only_accept is not type:
        raise WrongContext(type, cmd.only_accept)

    return cmd


@onDispatch(event="message_create", optional=True, priority=5)
@onDispatch(event="direct_message_create", optional=True, priority=5)
@onDispatch(event="interaction_create")
async def run(client: "Bot", data: Union[Message, Interaction]) -> bool:
    if type(data) is Interaction and data.type not in {
        Interaction_Type.APPLICATION_COMMAND,
        Interaction_Type.MODAL_SUBMIT,
    }:
        return

    name = get_name(data)
    if not name:
        return

    cmd = retrieve_command(name, type(data))

    if type(data) is Interaction and data.type is Interaction_Type.MODAL_SUBMIT:
        inputs = await parse_modal_submit(data)

    elif cmd.modal:
        try:
            inputs = await modal_response(client, data, cmd)
        except TimeoutError:
            if type(data) is Message:
                # NOTE: This response is only for message, as interaction can be continued in separate MODAL_SUBMIT
                # However that's a problem if command accepts any other arguments before modal
                await data.reply("Waited too long for an answer. Use command again if you would like to retry")
            return False

    else:
        inputs = {}

    ctx = set_context(client, cmd, data)

    if cmd.auto_deferred:
        await ctx.deferred(cmd.private_response)

    kwargs = Arguments(cmd, ctx, inputs)
    await cmd.execute(ctx, kwargs.kwargs)
    return True
