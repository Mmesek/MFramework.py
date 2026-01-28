import asyncio
import enum
import inspect
import types

from MFramework.commands import command as cmd_mod
from MFramework.commands.command import parse_signature, run_func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session


def test_run_func_with_sync_session():
    async def sample(session):
        return ("got", session)

    class DB:
        class sql:
            @staticmethod
            def session():
                class Ctx:
                    def __enter__(self):
                        return "sync_session"

                    def __exit__(self, *a):
                        return False

                return Ctx()

    ctx = type("Ctx", (), {"db": DB()})()

    param = cmd_mod.Parameter(None, Session, "", {}, "POSITIONAL_OR_KEYWORD", "session")

    async def runner():
        res = await cmd_mod.run_func(sample, ctx, {"session": param}, {})
        assert res == ("got", "sync_session")

    asyncio.run(runner())


def test_run_func_with_async_session():
    async def sample(session):
        return ("got", session)

    class DB:
        class sql:
            @staticmethod
            def session():
                class Ctx:
                    async def __aenter__(self):
                        return "async_session"

                    async def __aexit__(self, *a):
                        return False

                return Ctx()

    ctx = type("Ctx", (), {"db": DB()})()

    param = cmd_mod.Parameter(None, AsyncSession, "", {}, "POSITIONAL_OR_KEYWORD", "session")

    async def runner():
        res = await cmd_mod.run_func(sample, ctx, {"session": param}, {})
        assert res == ("got", "async_session")

    asyncio.run(runner())


def test_parse_signature_basic():
    def f(a: int, b: str = "x"):
        pass

    docs = {"a": "An integer", "b": "A string"}
    params = parse_signature(f, docs)

    assert "a" in params and "b" in params
    assert params["a"].default is inspect._empty
    assert params["b"].default == "x"
    assert params["a"].type == int
    assert params["b"].type == str
    assert params["a"].description == "An integer"


def test_parse_signature_enum_choices():
    class Color(enum.Enum):
        RED = 1
        BLUE = 2

    def f(c: Color):
        pass

    params = parse_signature(f, {})
    assert "c" in params
    assert isinstance(params["c"].choices, dict)
    assert params["c"].choices.get("RED") == 1


def test_run_func_without_session():
    async def sample(a, b=1):
        return {"a": a, "b": b}

    async def runner():
        res = await run_func(sample, None, {}, {"a": 2})
        assert res == {"a": 2, "b": 1}

    asyncio.run(runner())


class DummyBot:
    def __init__(self):
        self.created = []
        self.username = "bot"
        self.cfg = {self.username.lower(): {}}

    async def create_interaction_response(self, *a, **k):
        self.created.append(("interaction_response", a, k))

    async def create_message(self, *a, **k):
        self.created.append(("create_message", a, k))


class DummyDB:
    class influx:
        @staticmethod
        def commitCommandUsage(*a, **k):
            pass

    class sql:
        @staticmethod
        def session():
            class Ctx:
                def __enter__(self):
                    return object()

                def __exit__(self, *a):
                    return False

            return Ctx()


class Ctx:
    def __init__(self):
        self.replied = []
        self.bot = DummyBot()
        self.db = DummyDB()
        self.data = types.SimpleNamespace(id=1, token="t", locale="en-US")
        self.channel_id = 123
        self.user_id = 456
        self.guild_id = 789
        self.is_message = True

    async def reply(self, content=None, **kwargs):
        self.replied.append((content, kwargs))


def test_parse_docstring_simple():
    def f():
        """Summary

        Params
        - a:
            An arg
        """

    doc = cmd_mod.parse_docstring(f)
    assert "_doc" in doc and "a" in doc


def test_parse_arguments_and_iterate(monkeypatch):
    def f(a: int, b: str = "x"):
        """Docs

        Params
        - a:
            an int
        - b:
            a str
        """

    c = cmd_mod.Command(f)
    # prevent actual localization lookups
    c.translate = lambda locale, key, default=None: default or key

    options = cmd_mod.parse_arguments(c)
    assert any(o.name == "a" for o in options)

    # make sure iterate_commands yields our command
    monkeypatch.setitem(cmd_mod.commands, "f", c)
    out = list(cmd_mod.iterate_commands(registered=[], guild_id=None, bot_id=None))
    # should yield one tuple
    assert any(item[1] is c for item in out)


def test_compare_detects_difference():
    class D:
        __annotations__ = {"name": str, "description": str}

        def __init__(self, name, description):
            self.name = name
            self.description = description

    a = D("x", "one")
    b = D("x", "two")
    assert cmd_mod.compare(a, b) is True


def test_maybe_reply_fallback(monkeypatch):
    c = cmd_mod.Command(lambda: None)
    ctx = Ctx()

    async def bad_reply(*a, **k):
        raise RuntimeError("boom")

    ctx.reply = bad_reply

    # should fallback to bot.create_message without raising
    asyncio.run(c.maybe_reply(ctx, "hi", prefix=""))
    assert ctx.bot.created, "fallback create_message should be called"


def test_execute_various_returns(monkeypatch):
    # Patch types in module to simple dummies so isinstance checks work
    class Msg:
        def __init__(self, content="ok"):
            self.content = content
            self.embeds = []
            self.components = []
            self.attachments = []

    class Emb:
        pass

    class Comp:
        pass

    class Att:
        pass

    class Emo:
        def __init__(self):
            self.name = "e"
            self.id = 1
            self.animated = False

    monkeypatch.setattr(cmd_mod, "Message", Msg)
    monkeypatch.setattr(cmd_mod, "Embed", Emb)
    monkeypatch.setattr(cmd_mod, "Component", Comp)
    monkeypatch.setattr(cmd_mod, "Attachment", Att)
    monkeypatch.setattr(cmd_mod, "Emoji", Emo)

    # function returning Message
    async def f_msg():
        return Msg("hello")

    c = cmd_mod.Command(f_msg)
    ctx = Ctx()
    asyncio.run(c.execute(ctx, {}))
    assert ctx.replied or ctx.bot.created

    # function returning Embed
    async def f_emb():
        return Emb()

    c2 = cmd_mod.Command(f_emb)
    ctx2 = Ctx()
    asyncio.run(c2.execute(ctx2, {}))

    # function returning list of Components
    async def f_comp():
        return [Comp()]

    c3 = cmd_mod.Command(f_comp)
    ctx3 = Ctx()
    asyncio.run(c3.execute(ctx3, {}))

    # function returning Emoji
    async def f_emoji():
        return Emo()

    c4 = cmd_mod.Command(f_emoji)
    ctx4 = Ctx()
    ctx4.is_message = False
    asyncio.run(c4.execute(ctx4, {}))


def test_execute_typeerror_and_exception(monkeypatch):
    async def bad_type():
        raise TypeError("missing 'a'")

    async def bad_other():
        raise Exception("fail")

    cmd1 = cmd_mod.Command(bad_type)
    cmd2 = cmd_mod.Command(bad_other)
    ctx = Ctx()
    asyncio.run(cmd1.execute(ctx, {}))
    asyncio.run(cmd2.execute(ctx, {}))


def test_parse_docstring_choices():
    def f():
        """Summary

        Params
        - a:
            first param
        - Choices:
            RED = 1
            BLUE = 2
        """

    doc = cmd_mod.parse_docstring(f)
    # choices should have been parsed for param 'a'
    assert "a" in doc and doc.get("choices")
    assert "RED" in doc["choices"].get("a")


def test_parse_signature_autocomplete():
    def ac(q: int):
        pass

    def f(p: ac):
        pass

    params = cmd_mod.parse_signature(f, {})
    assert "p" in params
    assert params["p"].is_autocomplete
    assert "q" in params["p"].autocomplete_parameters


def test_compare_list_branch():
    class Inner:
        __annotations__ = {"v": str}

        def __init__(self, v):
            self.v = v

    class Wrapper:
        __annotations__ = {"items": list}

        def __init__(self, items):
            self.items = items

    a = Wrapper([Inner("one")])
    b = Wrapper([Inner("two")])
    assert cmd_mod.compare(a, b) is True


def test_iterate_commands_skips(monkeypatch):
    # create a command that should be skipped by iterate_commands
    def f():
        pass

    c = cmd_mod.Command(f)
    c.interaction = False
    monkeypatch.setitem(cmd_mod.commands, "skip_cmd", c)

    out = list(cmd_mod.iterate_commands(registered=[], guild_id=None, bot_id=None))
    assert all(item[1] is not c for item in out)


def test_parse_arguments_localizations(monkeypatch):
    # ensure LOCALIZATIONS is present
    import importlib

    loc = importlib.import_module("MFramework.utils.localizations")
    monkeypatch.setattr(loc, "LOCALIZATIONS", ["en-US", "pl"], raising=False)

    def f(a: int):
        """Doc

        Params
        - a:
            an int
        """

    c = cmd_mod.Command(f)
    c.translate = lambda locale, key, default=None: (default or key)[:100]
    opts = cmd_mod.parse_arguments(c)
    # name_localizations should be set on the created option
    assert opts and isinstance(opts[0].name_localizations, dict)
