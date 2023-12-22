from datetime import timedelta
from typing import TYPE_CHECKING, Any

from MFramework import (
    Attachment,
    Channel,
    ChannelID,
    Guild_Member,
    Guild_Member_Add,
    Guild_Member_Update,
    Message,
    Role,
    RoleID,
    Snowflake,
    User,
    UserID,
)
from MFramework.utils.utils import parseMention
from mdiscord.exceptions import UserError

from ._utils import DEFAULTS, Command, get_arguments

if TYPE_CHECKING:
    from MFramework import Context


# ARGUMENTS = re.compile("")
class Arguments:
    def __init__(self, cmd: Command, ctx: "Context", kwargs={}) -> None:
        self.cmd = cmd
        self.ctx = ctx
        self.kwargs = kwargs
        args = self._get_arguments()
        args = {k: v for k, v in args.items() if v is not None}
        self._set_kwargs(args)
        if ctx.is_interaction and (not ctx.data.data.options and ctx.data.data.resolved):
            self._set_resolved()
        self._set_defaults()
        self._add_extra(ctx=ctx, client=ctx.bot, interaction=ctx.data, message=ctx.data, language="en")
        self._strip_extra()

    def _get_arguments(self) -> dict[str, Any]:
        """Get arguments from interaction or parse them from message"""
        if self.ctx.is_interaction:
            return {
                option.name: option.value for option in self.ctx.data.data.options if option.name in self.cmd.arguments
            }
        args = iter(get_arguments(self.ctx.bot, self.ctx.data)[1:])
        positional = list(
            filter(
                lambda x: x.kind == "POSITIONAL_OR_KEYWORD" and x.name not in {"ctx", "interaction"},
                self.cmd.arguments.values(),
            )
        )
        return {
            arg.name: next(args, None) if arg.name != positional[-1].name else " ".join(list(args))
            for arg in positional
        }

    def _set_kwargs(self, arguments: dict[str, str]):
        """Sets arguments as keywords as well as casts to correct types"""
        if self.ctx.is_message:
            mentions = {
                User: self.ctx.data.mentions,
                Guild_Member: self.ctx.data.mentions,
                Channel: self.ctx.data.mention_channels,
                Role: self.ctx.data.mention_roles,
            }
        if not self.ctx.is_dm:
            caches = {
                User: self.ctx.cache.members,
                Guild_Member: self.ctx.cache.members,
                Channel: self.ctx.cache.channels,
                Role: self.ctx.cache.roles,
            }
        for name, value in arguments.items():
            t = self.cmd.arguments[name].type

            if issubclass(t, Snowflake) and not value.isdigit():
                value = parseMention(value)

            if t not in [Channel, Role, User, Guild_Member, ChannelID, UserID, RoleID, Attachment]:
                if type(value) is str and value.isdigit():
                    value = int(value)

                if t is timedelta:
                    from mlib.converters import total_seconds

                    v = total_seconds(value)

                elif t is dict:
                    v = ({v: k for k, v in self.cmd.arguments[name].choices.items()}.get(value), value)

                elif self.cmd.arguments[name].is_autocomplete:
                    v = value

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
                    try:
                        _id = Snowflake(parseMention(value))
                    except ValueError as ex:
                        raise UserError(f"ID needs to be a digit or a mention. Got `{ex}`")
                    o = next(filter(lambda i: i.id == _id, mentions.get(t)), None)

                    if not o or t is Guild_Member:
                        o = caches.get(t).get(_id, Guild_Member(user=User(id=_id, username=_id)))

                    if t is User and type(o) in {Guild_Member, Guild_Member_Update, Guild_Member_Add}:
                        o = o.user

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
        _k = {key: self.ctx.data, "language": self.ctx.language or "en"}
        _k.update(kwargs)
        for arg, value in _k.items():
            if arg in self.cmd.arguments and self.cmd.arguments[arg].kind not in {"KEYWORLD_ONLY"}:
                if not self.kwargs.get(arg):
                    # Make sure we are not overwriting, just in case
                    self.kwargs[arg] = value

    def _strip_extra(self):
        for arg in self.kwargs.copy():
            if arg not in self.cmd.arguments or self.kwargs[arg] is None:
                self.kwargs.pop(arg)
