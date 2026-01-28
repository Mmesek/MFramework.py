from datetime import timedelta
from types import SimpleNamespace

import pytest
from mdiscord.exceptions import UserError
from MFramework import Channel, Guild_Member, Role, Snowflake, User
from MFramework.commands.arguments import Arguments


class FakeParam:
    def __init__(self, name, type_, kind="POSITIONAL_OR_KEYWORD", choices=None, is_autocomplete=False):
        self.name = name
        self.type = type_
        self.kind = kind
        self.choices = choices or {}
        self.is_autocomplete = is_autocomplete


class FakeCmd:
    def __init__(self, arguments: dict):
        self.arguments = arguments


class FakeResolved:
    def __init__(self, users=None, members=None):
        self.users = users or {}
        self.members = members or {}


class FakeData:
    def __init__(self, options=None, resolved=None, mentions=None, mention_roles=None, mention_channels=None):
        self.data = SimpleNamespace(options=options or [], resolved=resolved)
        # message-like fields
        self.mentions = mentions or []
        self.mention_roles = mention_roles or []
        self.mention_channels = mention_channels or []


class FakeCache:
    def __init__(self, members=None, channels=None, roles=None):
        self.members = members or {}
        self.channels = channels or {}
        self.roles = roles or {}


def make_ctx(**kwargs):
    # defaults useful for DEFAULTS-based tests
    ctx = SimpleNamespace()
    ctx.is_interaction = kwargs.get("is_interaction", False)
    ctx.is_message = kwargs.get("is_message", False)
    ctx.is_dm = kwargs.get("is_dm", False)
    ctx.data = kwargs.get("data", FakeData())
    ctx.cache = kwargs.get("cache", SimpleNamespace(members={}, channels={}, roles={}))
    ctx.bot = kwargs.get("bot", SimpleNamespace())
    ctx.language = kwargs.get("language", "en")
    # defaults used by _set_defaults
    ctx.channel_id = kwargs.get("channel_id", 111)
    ctx.guild_id = kwargs.get("guild_id", 222)
    ctx.user_id = kwargs.get("user_id", 333)
    ctx.user = kwargs.get("user", None)
    ctx.member = kwargs.get("member", None)
    return ctx


def test_set_kwargs_basic_types_and_choices_and_timedelta_and_autocomplete():
    cmd = FakeCmd({
        "num": FakeParam("num", int),
        "td": FakeParam("td", timedelta),
        "choice": FakeParam("choice", dict, choices={"a": "val_a"}),
        "ac": FakeParam("ac", str, is_autocomplete=True),
    })

    a = Arguments.__new__(Arguments)
    a.cmd = cmd
    a.ctx = make_ctx(is_message=True)
    a.kwargs = {}

    # call _set_kwargs directly to exercise conversions
    a._set_kwargs({"num": "5", "td": "1h", "choice": "val_a", "ac": "autocomplete-value"})

    assert a.kwargs["num"] == 5
    assert isinstance(a.kwargs["td"], timedelta)
    # choice should become tuple (choice_key, original_value)
    assert a.kwargs["choice"] == ("a", "val_a")
    assert a.kwargs["ac"] == "autocomplete-value"


def test_snowflake_and_interaction_resolved_and_set_resolved_flow():
    # prepare command with user, member and snowflake args
    cmd = FakeCmd({
        "user": FakeParam("user", User),
        "member": FakeParam("member", Guild_Member),
        "snow": FakeParam("snow", Snowflake),
    })

    # prepare resolved mapping with user and member
    resolved = FakeResolved(users={"123": User(id=123)}, members={"456": Guild_Member(user=User(id=456))})
    data = FakeData(options=[], resolved=resolved)
    ctx = make_ctx(is_interaction=True, data=data)

    args = Arguments(cmd, ctx)

    # _set_resolved should populate from resolved dicts
    assert isinstance(args.kwargs["user"], User)
    assert isinstance(args.kwargs["member"], Guild_Member)
    # Snowflake is not part of resolved-type set and should not be present
    assert "snow" not in args.kwargs


def test_set_kwargs_message_mentions_and_cache_and_invalid_mention_raises():
    # Test message mention resolving and handling invalid mention
    cmd = FakeCmd({"user": FakeParam("user", User)})

    # create a User mention in data
    mentioned = User(id=Snowflake(123))
    data = FakeData(mentions=[mentioned])
    cache = FakeCache(members={Snowflake(999): Guild_Member(user=User(id=999))})
    ctx = make_ctx(is_message=True, is_interaction=False, data=data, cache=cache)

    a = Arguments.__new__(Arguments)
    a.cmd = cmd
    a.ctx = ctx
    a.kwargs = {}

    # valid mention string -> finds mentioned user
    a._set_kwargs({"user": "<@123>"})
    assert isinstance(a.kwargs["user"], User)

    # invalid mention (non-digit after parse) should raise UserError
    a.kwargs = {}
    with pytest.raises(UserError):
        a._set_kwargs({"user": "<@abc>"})


def test_set_defaults_and_add_extra_and_strip_extra():
    # ensure defaults are applied and extra message param is added then stripped
    cmd = FakeCmd({
        "channel": FakeParam("channel", type(Channel)),
        "message": FakeParam("message", str),
        "unused": FakeParam("unused", int),
    })

    ctx = make_ctx(is_message=True, data=SimpleNamespace())
    # set the attribute that DEFAULTS maps for Channel type may not exist; use channel_id attr
    ctx.channel_id = 4242

    a = Arguments.__new__(Arguments)
    a.cmd = cmd
    a.ctx = ctx
    a.kwargs = {}

    # _set_defaults should use ctx.channel_id for Channel-like default lookup
    a._set_defaults()
    # The argument name 'channel' should be present but may be None (default mapping)
    assert "channel" in a.kwargs

    # _add_extra should add message when present in cmd.arguments
    a._add_extra(ctx=ctx, client=ctx, interaction=None, message=ctx.data, language="en")
    assert "message" in a.kwargs

    # _strip_extra should remove keys not in cmd.arguments or None
    a.kwargs["extra"] = None
    a._strip_extra()
    assert "extra" not in a.kwargs
