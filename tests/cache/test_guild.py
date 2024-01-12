import pytest

from MFramework.cache.guild import GuildCache, ObjectCollections, BotMeta, Logging
from MFramework import Groups, Guild, Role, Guild_Member, User, Channel

class Bot:
    cfg: dict = {}
    user_id = 1

BOT_COLOR = 35

roles=[
    Role(id=1, name="Admin", color=4, position=10, permissions=1 << 0),
    Role(id=2, name="Bot", managed=True, color=BOT_COLOR, position=9, permissions=1 << 1),
    Role(id=3, name="Another Bot", managed=True, color=20, position=8, permissions=1 << 2),
    Role(id=4, name="Someone", color=40, position=7, permissions=1 << 3),
    Role(id=5, name="nitro", position=16, color=50, permissions=1 << 4),
    Role(id=6, name="vip", position=4, permissions=1 << 5),
    Role(id=7, name="VIP", position=3, permissions=1 << 6),
    Role(id=8, name="Contributor", position=30, permissions=1 << 7),
    Role(id=9, name="Nitro Booster", color=60, position=5, permissions=1 << 8),
]

def test_guild_cache():
    guild = Guild(id=1)
    cache = GuildCache(guild=guild)
    assert cache.guild_id == 1
    assert cache.guild == guild

@pytest.mark.asyncio
async def test_collections_cache():
    members = [Guild_Member(user=User(id=15)), Guild_Member(user=User(id=10))]
    roles = [Role(id=1), Role(id=2)]
    channels = [Channel(id=12), Channel(id=5)]
    guild = Guild(members=members, roles=roles, channels=channels)
    cache = ObjectCollections(bot=Bot(), guild=guild)
    await cache.initialize(guild=guild)
    assert all(m.user.id in cache.members for m in members)
    assert all(m.id in cache.roles for m in roles)
    assert all(m.id in cache.channels for m in channels)


def test_collections_set_groups():
    guild = Guild(id=1, roles=roles)
    cache = ObjectCollections(bot=Bot(), guild=guild)
    cache.set_role_groups({r.id: r  for r in roles})
    assert cache.groups[Groups.ADMIN].symmetric_difference({1}) == set()
    assert cache.groups[Groups.NITRO].symmetric_difference({9}) == set()
    assert cache.groups[Groups.VIP].symmetric_difference({6,7, 8}) == set()

@pytest.mark.asyncio
async def test_meta_cache():
    members = [
        Guild_Member(roles=[2, 1, 4], user=User(id=1),nick="Test Bot"), 
        Guild_Member(roles=[5], user=User(id=5), nick="Booster")
    ]
    guild = Guild(id=1, roles=roles, members=members)
    cache = BotMeta(bot=Bot(), guild=guild)
    await cache.initialize(bot=Bot(), guild=guild)
    assert cache.bot == members[0]
    assert cache.name == "Test Bot"
    assert cache.color == BOT_COLOR
    assert cache.permissions == 11

@pytest.mark.asyncio
async def test_meta_color():
    guild = Guild(id=1, roles=roles)
    cache = BotMeta(bot=Bot(), guild=guild)
    await cache.initialize(bot=Bot(), guild=guild)
    assert await cache.get_top_color(roles=[1,2,4,5,6,7,8]) == 35 # not-highest with Bot role
    assert await cache.get_top_color(roles=[2,3,4]) == 35 # two bot roles
    assert await cache.get_top_color(roles=[1,4]) == 4 # highest non-bot role
    assert await cache.get_top_color(roles=[1,4,5,9]) == 50 # highest non-bot role
    assert await cache.get_top_color(roles=[6,7,8]) == 0 # No color


@pytest.mark.asyncio
async def test_meta_permissions():
    guild = Guild(id=1, roles=roles)
    cache = BotMeta(bot=Bot(), guild=guild)
    await cache.initialize(bot=Bot(), guild=guild)
    assert await cache.calculate_permissions([1,2,3]) == 7
    assert await cache.calculate_permissions([9,3]) == 260
    assert await cache.calculate_permissions([5,3,4]) == 28

@pytest.mark.asyncio
async def test_logging_cache():
    guild = Guild(id=1, roles=roles)
    cache = Logging(bot=Bot(), guild=guild)
    await cache.initialize(bot=Bot(), guild=guild)
    assert cache.webhooks == {}
    assert cache.logging == {}
    raise NotImplementedError

@pytest.mark.asyncio
async def test_logging_get_webhooks():
    guild = Guild(id=1, roles=roles)
    cache = Logging(bot=Bot(), guild=guild)
    await cache.initialize(bot=Bot(), guild=guild)
    assert cache.webhooks == {}
    assert cache.logging == {}
    raise NotImplementedError

@pytest.mark.asyncio
async def test_logging_set_loggers():
    guild = Guild(id=1, roles=roles)
    cache = Logging(bot=Bot(), guild=guild)
    await cache.initialize(bot=Bot(), guild=guild)
    assert cache.webhooks == {}
    assert cache.logging == {}
    raise NotImplementedError
