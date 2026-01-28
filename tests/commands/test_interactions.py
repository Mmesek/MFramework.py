from types import SimpleNamespace

import MFramework.commands.interactions as interactions
import pytest


class FakeClient:
    def __init__(self):
        self.username = "bot"
        self.user_id = 1
        self.application = SimpleNamespace(id=10)
        self.registered = False
        self.called = {}

    async def get_current_bot_application_information(self):
        self.called["get_current"] = True
        return SimpleNamespace(id=10)

    async def get_global_application_commands(self, application_id, with_localizations):
        self.called["get_global"] = (application_id, with_localizations)
        return []

    async def get_guild_application_commands(self, application_id, guild_id, with_localizations):
        self.called["get_guild"] = (application_id, guild_id, with_localizations)
        return []

    async def create_global_application_command(self, **kwargs):
        self.called["create_global"] = kwargs
        return SimpleNamespace(**kwargs)

    async def create_guild_application_command(self, **kwargs):
        self.called["create_guild"] = kwargs
        return SimpleNamespace(**kwargs)

    async def edit_global_application_command(self, **kwargs):
        self.called["edit_global"] = kwargs
        return SimpleNamespace(**kwargs)

    async def edit_guild_application_command(self, **kwargs):
        self.called["edit_guild"] = kwargs
        return SimpleNamespace(**kwargs)

    async def delete_global_application_command(self, application_id, command_id):
        self.called["delete_global"] = (application_id, command_id)

    async def delete_guild_application_command(self, application_id, guild_id, command_id):
        self.called["delete_guild"] = (application_id, guild_id, command_id)

    async def bulk_overwrite_global_application_commands(self, application_id, payload=None):
        self.called["overwrite_global"] = (application_id, payload)
        return payload

    async def bulk_overwrite_guild_application_commands(self, application_id, guild_id, payload=None):
        self.called["overwrite_guild"] = (application_id, guild_id, payload)
        return payload


def make_app_cmd(name="x"):
    return SimpleNamespace(name=name, id=123, description="d", options=None, default_permission=True, type=None)


@pytest.mark.asyncio
async def test_ready_early_return(monkeypatch):
    client = FakeClient()
    client.registered = True
    await interactions.ready(client, SimpleNamespace())
    # should not call get_current when registered
    assert "get_current" not in client.called


@pytest.mark.asyncio
async def test_ready_calls_register(monkeypatch):
    client = FakeClient()
    client.registered = False

    async def fake_register(c):
        c.called["registered_called"] = True

    monkeypatch.setattr(interactions, "register_commands", fake_register)
    await interactions.ready(client, SimpleNamespace())
    assert client.called.get("get_current")
    assert client.called.get("registered_called")


@pytest.mark.asyncio
async def test_guild_create_with_application(monkeypatch):
    client = FakeClient()
    guild = SimpleNamespace(id=7)

    called = {}

    async def fake_register(c, g=None):
        called["ok"] = True
        return [make_app_cmd("a")]

    monkeypatch.setattr(interactions, "register_commands", fake_register)
    await interactions.guild_create(client, guild)
    assert called.get("ok") is True


@pytest.mark.asyncio
async def test_get_commands_routes(monkeypatch):
    client = FakeClient()
    client.application = SimpleNamespace(id=55)
    # guild None -> global
    res = await interactions.get_commands(client, None)
    assert isinstance(res, list)
    # guild provided -> guild
    res2 = await interactions.get_commands(client, SimpleNamespace(id=9))
    assert isinstance(res2, list)


@pytest.mark.asyncio
async def test_register_commands_user_option_skips(monkeypatch):
    client = FakeClient()
    # registered contains same name -> should skip adding
    registered = [make_app_cmd("u")]

    async def fake_get_commands(c, g=None):
        return registered

    monkeypatch.setattr(interactions, "get_commands", fake_get_commands)

    # iterate_commands yields a command with USER option
    def fake_iterate(registered_list, guild_id, bot_id):
        opt = SimpleNamespace(type=interactions.Application_Command_Option_Type.USER)
        _cmd = SimpleNamespace(
            description="d", group=interactions.Groups.GLOBAL, translate=lambda locale, key, default=None: default
        )
        yield ("u", _cmd, [opt])

    monkeypatch.setattr(interactions, "iterate_commands", fake_iterate)

    # fail the test if add_command is called
    async def fail_add(*a, **k):
        raise AssertionError("add_command should not be called")

    monkeypatch.setattr(interactions, "add_command", fail_add)

    await interactions.register_commands(client, None)


@pytest.mark.asyncio
async def test_register_commands_message_option_skips(monkeypatch):
    client = FakeClient()
    registered = [make_app_cmd("m")]

    async def fake_get_commands(c, g=None):
        return registered

    monkeypatch.setattr(interactions, "get_commands", fake_get_commands)

    def fake_iterate(registered_list, guild_id, bot_id):
        opt = SimpleNamespace(type=interactions.Message)
        _cmd = SimpleNamespace(
            description="d", group=interactions.Groups.GLOBAL, translate=lambda locale, key, default=None: default
        )
        yield ("m", _cmd, [opt])

    monkeypatch.setattr(interactions, "iterate_commands", fake_iterate)

    async def fail_add(*a, **k):
        raise AssertionError("add_command should not be called")

    monkeypatch.setattr(interactions, "add_command", fail_add)

    await interactions.register_commands(client, None)


@pytest.mark.asyncio
async def test_register_commands_updates_and_guild_permissions(monkeypatch):
    client = FakeClient()
    guild = SimpleNamespace(id=77)
    # set client.cache with guild entry
    client.cache = {guild.id: SimpleNamespace(_permissions_set=True)}

    # registered has one existing command 'exists'
    registered = [make_app_cmd("exists")]

    async def fake_get_commands(c, g=None):
        return registered

    monkeypatch.setattr(interactions, "get_commands", fake_get_commands)

    # have iterate_commands yield one updated and one new
    def fake_iterate(registered_list, guild_id, bot_id):
        _exists = SimpleNamespace(
            description="d", group=interactions.Groups.GLOBAL, translate=lambda locale, key, default=None: default
        )
        _new = SimpleNamespace(
            description="d", group=interactions.Groups.GLOBAL, translate=lambda locale, key, default=None: default
        )
        yield ("exists", _exists, [])
        yield ("brandnew", _new, [])

    monkeypatch.setattr(interactions, "iterate_commands", fake_iterate)

    # ensure interactions.commands contains 'exists' plus another so lengths differ
    monkeypatch.setattr(interactions, "commands", {"exists": True, "another": True})

    called = {"added": False, "edited": False}

    async def fake_add(client, cmd, guild=None):
        called["added"] = True
        return cmd

    async def fake_edit(client, cmd, guild=None):
        called["edited"] = True
        return cmd

    monkeypatch.setattr(interactions, "add_command", fake_add)
    monkeypatch.setattr(interactions, "edit_command", fake_edit)

    out = await interactions.register_commands(client, guild)
    # return should be registered + new cmds
    assert isinstance(out, list)
    assert called["added"] is True
    assert called["edited"] is True
    # permissions flag should be set to False
    assert client.cache[guild.id]._permissions_set is False


@pytest.mark.asyncio
async def test_register_commands_overwrite_when_lengths_equal(monkeypatch):
    client = FakeClient()

    # registered list length 1
    async def fake_get_commands(c, g=None):
        return [make_app_cmd("r")]

    monkeypatch.setattr(interactions, "get_commands", fake_get_commands)

    # interactions.commands has length 2
    monkeypatch.setattr(interactions, "commands", {"a": 1, "b": 2})

    # iterate_commands yields two new commands
    def fake_iterate(registered_list, guild_id, bot_id):
        _cmd = SimpleNamespace(
            description="d", group=interactions.Groups.GLOBAL, translate=lambda locale, key, default=None: default
        )
        yield ("a", _cmd, [])
        yield ("b", _cmd, [])

    monkeypatch.setattr(interactions, "iterate_commands", fake_iterate)

    called = {}

    async def fake_overwrite(client, payload, guild=None):
        called["payload"] = payload
        return ["overwritten"]

    monkeypatch.setattr(interactions, "overwrite_commands", fake_overwrite)

    await interactions.register_commands(client, None)
    assert "payload" in called

    @pytest.mark.asyncio
    async def test_register_commands_equal_lengths_but_no_registered(monkeypatch):
        client = FakeClient()

        async def fake_get_commands(c, g=None):
            return []

        monkeypatch.setattr(interactions, "get_commands", fake_get_commands)

        # interactions.commands length 1
        monkeypatch.setattr(interactions, "commands", {"a": 1})

        # iterate_commands yields one command 'a'
        def fake_iterate(registered_list, guild_id, bot_id):
            _cmd = SimpleNamespace(
                description="d", group=interactions.Groups.GLOBAL, translate=lambda locale, key, default=None: default
            )
            yield ("a", _cmd, [])

        monkeypatch.setattr(interactions, "iterate_commands", fake_iterate)

        called = {}

        async def fake_add(client, cmd, guild=None):
            called["added"] = True
            return cmd

        monkeypatch.setattr(interactions, "add_command", fake_add)

        await interactions.register_commands(client, None)
        assert called.get("added") is True


@pytest.mark.asyncio
async def test_add_edit_delete_overwrite_routes(monkeypatch):
    client = FakeClient()
    cmd = make_app_cmd("test")
    guild = SimpleNamespace(id=99)

    await interactions.add_command(client, cmd, None)
    assert client.called.get("create_global")
    await interactions.add_command(client, cmd, guild)
    assert client.called.get("create_guild")

    # edit
    await interactions.edit_command(client, cmd, None)
    assert client.called.get("edit_global")
    await interactions.edit_command(client, cmd, guild)
    assert client.called.get("edit_guild")

    # delete
    await interactions.delete_command(client, cmd, None)
    assert client.called.get("delete_global")
    await interactions.delete_command(client, cmd, guild)
    assert client.called.get("delete_guild")

    # overwrite
    await interactions.overwrite_commands(client, [cmd], None)
    assert client.called.get("overwrite_global")
    await interactions.overwrite_commands(client, [cmd], guild)
    assert client.called.get("overwrite_guild")


@pytest.mark.asyncio
async def test_register_commands_new_and_delete(monkeypatch):
    client = FakeClient()

    # simulate get_commands returning one registered unknown command
    reg_cmd = make_app_cmd("bad")

    async def fake_get_commands(c, g=None):
        return [reg_cmd]

    monkeypatch.setattr(interactions, "get_commands", fake_get_commands)

    # iterate_commands yields nothing so unrecognized_commands triggers delete
    async_calls = {}

    async def fake_delete(c, cmd, guild=None):
        async_calls["deleted"] = cmd.name

    monkeypatch.setattr(interactions, "delete_command", fake_delete)

    # ensure CLEAR_INTERACTIONS is False for this test
    monkeypatch.setattr(interactions, "CLEAR_INTERACTIONS", False)

    await interactions.register_commands(client, None)
    # delete_command should have been called for unrecognized command
    assert async_calls.get("deleted") == "bad"


@pytest.mark.asyncio
async def test_register_commands_adds_new(monkeypatch):
    client = FakeClient()

    async def fake_get_commands(c, g=None):
        return []

    monkeypatch.setattr(interactions, "get_commands", fake_get_commands)

    # iterate_commands yields one new command
    def fake_iterate(registered, guild_id, bot_id):
        # return tuple: (command_name, _command_obj, options)
        _cmd = SimpleNamespace(
            description="desc", group=interactions.Groups.GLOBAL, translate=lambda locale, key, default=None: default
        )
        yield ("newcmd", _cmd, [])

    monkeypatch.setattr(interactions, "iterate_commands", fake_iterate)

    called = {}

    async def fake_add(client, cmd, guild=None):
        called["added"] = cmd.name
        return cmd

    monkeypatch.setattr(interactions, "add_command", fake_add)

    await interactions.register_commands(client, None)
    assert called.get("added") == "newcmd"


@pytest.mark.asyncio
async def test_register_commands_clear_interactions(monkeypatch):
    client = FakeClient()
    monkeypatch.setattr(interactions, "CLEAR_INTERACTIONS", True)

    async def fake_overwrite(client, cmds, guild=None):
        return ["ok"]

    monkeypatch.setattr(interactions, "overwrite_commands", fake_overwrite)

    res = await interactions.register_commands(client, None)
    assert res == ["ok"]


@pytest.mark.asyncio
async def test_guild_create_waits_and_then_registers(monkeypatch):
    client = FakeClient()
    client.application = None
    guild = SimpleNamespace(id=5)

    called = {}

    async def fake_register(c, g=None):
        called["registered"] = True

    monkeypatch.setattr(interactions, "register_commands", fake_register)

    # monkeypatch asyncio.sleep to set client.application then return
    async def fake_sleep(sec):
        client.application = SimpleNamespace(id=42)

    import asyncio as _asyncio

    monkeypatch.setattr(_asyncio, "sleep", fake_sleep)

    await interactions.guild_create(client, guild)
    assert called.get("registered") is True


@pytest.mark.asyncio
async def test_register_commands_user_option_added_when_not_registered(monkeypatch):
    client = FakeClient()

    async def fake_get_commands(c, g=None):
        return []

    monkeypatch.setattr(interactions, "get_commands", fake_get_commands)

    def fake_iterate(registered_list, guild_id, bot_id):
        opt = SimpleNamespace(type=interactions.Application_Command_Option_Type.USER)
        _cmd = SimpleNamespace(
            description="d", group=interactions.Groups.GLOBAL, translate=lambda locale, key, default=None: default
        )
        yield ("u2", _cmd, [opt])

    monkeypatch.setattr(interactions, "iterate_commands", fake_iterate)

    called = {}

    async def fake_add(client, cmd, guild=None):
        called["added"] = cmd.name
        return cmd

    monkeypatch.setattr(interactions, "add_command", fake_add)

    await interactions.register_commands(client, None)
    assert called.get("added") == "u2"


@pytest.mark.asyncio
async def test_register_commands_message_option_added_when_not_registered(monkeypatch):
    client = FakeClient()

    async def fake_get_commands(c, g=None):
        return []

    monkeypatch.setattr(interactions, "get_commands", fake_get_commands)

    def fake_iterate(registered_list, guild_id, bot_id):
        opt = SimpleNamespace(type=interactions.Message)
        _cmd = SimpleNamespace(
            description="d", group=interactions.Groups.GLOBAL, translate=lambda locale, key, default=None: default
        )
        yield ("m2", _cmd, [opt])

    monkeypatch.setattr(interactions, "iterate_commands", fake_iterate)

    called = {}

    async def fake_add(client, cmd, guild=None):
        called["added"] = cmd.name
        return cmd

    monkeypatch.setattr(interactions, "add_command", fake_add)

    await interactions.register_commands(client, None)
    assert called.get("added") == "m2"


@pytest.mark.asyncio
async def test_add_command_badrequest_logs(monkeypatch):
    client = FakeClient()

    async def fake_get_commands(c, g=None):
        return []

    monkeypatch.setattr(interactions, "get_commands", fake_get_commands)

    def fake_iterate(registered_list, guild_id, bot_id):
        _cmd = SimpleNamespace(
            description="d", group=interactions.Groups.GLOBAL, translate=lambda locale, key, default=None: default
        )
        yield ("whoops", _cmd, [])

    monkeypatch.setattr(interactions, "iterate_commands", fake_iterate)

    # make add_command raise BadRequest (use test-local simple class to avoid constructor signature differences)
    class DummyBad(Exception):
        pass

    monkeypatch.setattr(interactions, "BadRequest", DummyBad)

    def raise_bad(*a, **k):
        raise DummyBad("boom")

    monkeypatch.setattr(interactions, "add_command", raise_bad)

    logged = {}

    def fake_warn(msg, *a, **k):
        logged["warn"] = True

    monkeypatch.setattr(interactions.log, "warning", fake_warn)

    # should not raise
    await interactions.register_commands(client, None)
    assert logged.get("warn") is True


@pytest.mark.asyncio
async def test_register_commands_zero_commands_nonzero_registered(monkeypatch):
    client = FakeClient()

    # registered non-empty
    async def fake_get_commands(c, g=None):
        return [make_app_cmd("r1")]

    monkeypatch.setattr(interactions, "get_commands", fake_get_commands)

    # iterate_commands yields nothing
    def fake_iterate(registered_list, guild_id, bot_id):
        if False:
            yield

    monkeypatch.setattr(interactions, "iterate_commands", fake_iterate)

    # ensure interactions.commands is empty
    monkeypatch.setattr(interactions, "commands", {})

    await interactions.register_commands(client, None)
    # client.registered_commands should be set to registered
    assert hasattr(client, "registered_commands") and client.registered_commands[0].name == "r1"


@pytest.mark.asyncio
async def test_register_commands_clear_interactions_with_guild(monkeypatch):
    client = FakeClient()
    guild = SimpleNamespace(id=11)
    client.cache = {guild.id: SimpleNamespace(_permissions_set=True)}
    monkeypatch.setattr(interactions, "CLEAR_INTERACTIONS", True)

    async def fake_overwrite(client, cmds, guild=None):
        return ["okg"]

    monkeypatch.setattr(interactions, "overwrite_commands", fake_overwrite)

    res = await interactions.register_commands(client, guild)
    assert res == ["okg"]


@pytest.mark.asyncio
async def test_edit_command_badrequest_logs(monkeypatch):
    client = FakeClient()

    # registered contains existing command to force updated_commands
    registered = [make_app_cmd("upd")]

    async def fake_get_commands(c, g=None):
        return registered

    monkeypatch.setattr(interactions, "get_commands", fake_get_commands)

    def fake_iterate(registered_list, guild_id, bot_id):
        _cmd = SimpleNamespace(
            description="d", group=interactions.Groups.GLOBAL, translate=lambda locale, key, default=None: default
        )
        yield ("upd", _cmd, [])

    monkeypatch.setattr(interactions, "iterate_commands", fake_iterate)
    monkeypatch.setattr(interactions, "commands", {"upd": True})

    class DummyBadEdit(Exception):
        pass

    monkeypatch.setattr(interactions, "BadRequest", DummyBadEdit)

    def raise_bad_edit(*a, **k):
        raise DummyBadEdit("boom")

    monkeypatch.setattr(interactions, "edit_command", raise_bad_edit)

    logged = {}

    def fake_warn(msg, *a, **k):
        logged["warn"] = True

    monkeypatch.setattr(interactions.log, "warning", fake_warn)

    await interactions.register_commands(client, None)
    assert logged.get("warn") is True
