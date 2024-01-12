import re
from MFramework import Groups
from MFramework.cache.base import Base, Commands, RuntimeCommands, Trigger


class TestBot:
    username = "Test"
    user_id = 1
    alias = "?"


def test_cached_roles():
    cache = Base()

    assert cache.cached_roles([]) != Groups.ADMIN

    cache.groups = {Groups.ADMIN: {1}, Groups.MODERATOR: {2, 3}, Groups.MUTED: {4}, Groups.EVERYONE: {}}

    assert cache.cached_roles([1, 2, 3]) == Groups.ADMIN
    assert cache.cached_roles([]) == Groups.GLOBAL
    assert cache.cached_roles([]) == Groups.EVERYONE
    assert cache.cached_roles([4]) == Groups.MUTED


def test_default_alias():
    cache = Commands(bot=TestBot())

    assert cache.alias == re.compile(r"\?|Test|1>")


def test_set_alias():
    bot = TestBot()
    cache = Commands(bot=bot)

    cache.set_alias(bot, "!")
    assert cache.alias == re.compile(r"!|Test|1>")

    bot.username = "Test 3"
    cache.set_alias(bot, "@")
    assert cache.alias == re.compile(r"@|Test\ 3|1>")

    cache.set_alias(bot, "Very Long Alias")
    assert cache.alias == re.compile(r"Very\ Long\ Alias|Test\ 3|1>")


def test_recompile_triggers():
    cache = RuntimeCommands(bot=TestBot())

    test_1 = Trigger(Groups.ADMIN, "Test", "test trigger", None, None)
    test_2 = Trigger(Groups.ADMIN, "Test2", "test trigger 2", None, None)
    test_3 = Trigger(Groups.NITRO, "Test", "test", None, None)
    test_4 = Trigger(Groups.GLOBAL, "Test3", "test_", None, None)

    cache.recompile_triggers([test_1, test_2, test_3, test_4])
    assert cache.triggers == {"Test": test_3, "Test2": test_2, "Test3": test_4}

    assert cache.responses == {
        Groups.ADMIN: re.compile(r"(?:(?P<Test>test trigger)|(?P<Test2>test trigger 2))", re.IGNORECASE),
        Groups.NITRO: re.compile(r"(?:(?P<Test>test))", re.IGNORECASE),
        Groups.GLOBAL: re.compile(r"(?:(?P<Test3>test_))", re.IGNORECASE),
    }
