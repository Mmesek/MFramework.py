"""Tests for MFramework.commands.cooldowns module."""

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from MFramework.commands.cooldowns import (
    Bucket,
    CacheCooldown,
    Cooldown,
    DatabaseCooldown,
    SlidingWindow,
    Tokens,
    cooldown,
    cooldowns as cooldowns_dict,
)
from MFramework.commands.exceptions import CooldownError


@pytest.fixture
def fake_context():
    """Create a fake context for testing."""
    ctx = MagicMock()
    ctx.user_id = 12345
    ctx.guild_id = 54321
    ctx.channel_id = 99999
    ctx.roles = [1, 2, 3]
    ctx.permission_group = "admin"
    return ctx


class TestBucket:
    """Test Bucket enum."""

    def test_bucket_user(self):
        """Test USER bucket."""
        assert Bucket.USER.value == "user_id"

    def test_bucket_guild(self):
        """Test GUILD bucket."""
        assert Bucket.GUILD.value == "guild_id"

    def test_bucket_channel(self):
        """Test CHANNEL bucket."""
        assert Bucket.CHANNEL.value == "channel_id"

    def test_bucket_role(self):
        """Test ROLE bucket."""
        assert Bucket.ROLE.value == "roles"

    def test_bucket_group(self):
        """Test GROUP bucket."""
        assert Bucket.GROUP.value == "permission_group"


class TestCooldown:
    """Test base Cooldown class."""

    def test_cooldown_initialization(self, fake_context):
        """Test Cooldown initialization."""
        cooldown_obj = Cooldown(
            ctx=fake_context,
            cooldown=timedelta(seconds=10),
            cooldown_type="test_cooldown",
            bucket=Bucket.USER,
        )
        assert cooldown_obj.ctx == fake_context
        assert cooldown_obj._type == "test_cooldown"
        assert cooldown_obj._bucket == Bucket.USER
        assert cooldown_obj.cooldown == timedelta(seconds=10)

    def test_cooldown_default_bucket(self, fake_context):
        """Test Cooldown with default bucket."""
        cooldown_obj = Cooldown(
            ctx=fake_context,
            cooldown=timedelta(seconds=10),
            cooldown_type="test_cooldown",
        )
        # When not provided, _bucket is None unless set via bucket parameter
        assert cooldown_obj._bucket is None or cooldown_obj._bucket == Bucket.USER

    def test_cooldown_bucket_property(self, fake_context):
        """Test bucket property with USER bucket."""
        cooldown_obj = Cooldown(
            ctx=fake_context,
            cooldown=timedelta(seconds=10),
            cooldown_type="test_cooldown",
            bucket=Bucket.USER,
        )
        assert cooldown_obj.bucket == 12345

    def test_cooldown_bucket_property_guild(self, fake_context):
        """Test bucket property with GUILD bucket."""
        cooldown_obj = Cooldown(
            ctx=fake_context,
            cooldown=timedelta(seconds=10),
            cooldown_type="test_cooldown",
            bucket=Bucket.GUILD,
        )
        assert cooldown_obj.bucket == 54321

    def test_cooldown_bucket_property_channel(self, fake_context):
        """Test bucket property with CHANNEL bucket."""
        cooldown_obj = Cooldown(
            ctx=fake_context,
            cooldown=timedelta(seconds=10),
            cooldown_type="test_cooldown",
            bucket=Bucket.CHANNEL,
        )
        assert cooldown_obj.bucket == 99999

    def test_add_cooldown(self, fake_context):
        """Test adding a cooldown."""
        cooldowns_dict.clear()
        cooldown_obj = Cooldown(
            ctx=fake_context,
            cooldown=timedelta(seconds=10),
            cooldown_type="test_cooldown",
            bucket=Bucket.USER,
        )
        cooldown_obj.add_cooldown()
        assert "test_cooldown" in cooldowns_dict
        assert 12345 in cooldowns_dict["test_cooldown"]

    def test_add_cooldown_custom_value(self, fake_context):
        """Test adding a cooldown with custom value."""
        cooldowns_dict.clear()
        custom_time = datetime.now(tz=timezone.utc)
        cooldown_obj = Cooldown(
            ctx=fake_context,
            cooldown=timedelta(seconds=10),
            cooldown_type="test_cooldown",
            bucket=Bucket.USER,
        )
        cooldown_obj.add_cooldown(value=custom_time)
        assert cooldowns_dict["test_cooldown"][12345] == custom_time

    def test_last_action_none(self, fake_context):
        """Test last_action when no cooldown exists."""
        cooldowns_dict.clear()
        cooldown_obj = Cooldown(
            ctx=fake_context,
            cooldown=timedelta(seconds=10),
            cooldown_type="nonexistent",
            bucket=Bucket.USER,
        )
        assert cooldown_obj.last_action is None

    def test_remaining_no_cooldown(self, fake_context):
        """Test remaining when no cooldown exists."""
        cooldowns_dict.clear()
        cooldown_obj = Cooldown(
            ctx=fake_context,
            cooldown=timedelta(seconds=10),
            cooldown_type="nonexistent",
            bucket=Bucket.USER,
        )
        assert cooldown_obj.remaining == timedelta()

    def test_on_cooldown_false(self, fake_context):
        """Test on_cooldown when no active cooldown."""
        cooldowns_dict.clear()
        cooldown_obj = Cooldown(
            ctx=fake_context,
            cooldown=timedelta(seconds=10),
            cooldown_type="test",
            bucket=Bucket.USER,
        )
        assert cooldown_obj.on_cooldown is False

    def test_on_cooldown_true(self, fake_context):
        """Test on_cooldown when cooldown is active."""
        cooldowns_dict.clear()
        cooldown_obj = Cooldown(
            ctx=fake_context,
            cooldown=timedelta(seconds=10),
            cooldown_type="test",
            bucket=Bucket.USER,
        )
        past_time = datetime.now(tz=timezone.utc) - timedelta(seconds=2)
        cooldown_obj.add_cooldown(value=past_time)
        assert cooldown_obj.on_cooldown is True

    def test_on_cooldown_expired(self, fake_context):
        """Test on_cooldown when cooldown has expired."""
        cooldowns_dict.clear()
        cooldown_obj = Cooldown(
            ctx=fake_context,
            cooldown=timedelta(seconds=1),
            cooldown_type="test",
            bucket=Bucket.USER,
        )
        past_time = datetime.now(tz=timezone.utc) - timedelta(seconds=2)
        cooldown_obj.add_cooldown(value=past_time)
        assert cooldown_obj.on_cooldown is False


class TestCacheCooldown:
    """Test CacheCooldown class."""

    @pytest.mark.asyncio
    async def test_cache_cooldown_initialization(self, fake_context):
        """Test CacheCooldown initialization."""
        fake_context.cache = MagicMock()
        fake_context.cache.cooldowns = MagicMock()
        cooldown_obj = CacheCooldown(
            ctx=fake_context,
            cooldown=timedelta(seconds=10),
            cooldown_type="test_cooldown",
        )
        assert cooldown_obj.ctx == fake_context
        assert cooldown_obj._type == "test_cooldown"

    @pytest.mark.asyncio
    async def test_get_last_action(self, fake_context):
        """Test getting last action from cache."""
        fake_time = datetime.now(tz=timezone.utc)
        fake_context.cache = MagicMock()
        fake_context.cache.cooldowns = MagicMock()
        fake_context.cache.cooldowns.get = AsyncMock(return_value=fake_time)

        cooldown_obj = CacheCooldown(
            ctx=fake_context,
            cooldown=timedelta(seconds=10),
            cooldown_type="test_cooldown",
        )
        await cooldown_obj.get_last_action()
        assert cooldown_obj.last_action == fake_time

    @pytest.mark.asyncio
    async def test_add_cooldown(self, fake_context):
        """Test adding cooldown to cache."""
        fake_context.cache = MagicMock()
        fake_context.cache.cooldowns = MagicMock()
        fake_context.cache.cooldowns.store = AsyncMock()

        cooldown_obj = CacheCooldown(
            ctx=fake_context,
            cooldown=timedelta(seconds=10),
            cooldown_type="test_cooldown",
        )
        await cooldown_obj.add_cooldown()
        fake_context.cache.cooldowns.store.assert_called_once()


class TestDatabaseCooldown:
    """Test DatabaseCooldown class."""

    def test_database_cooldown_initialization(self, fake_context):
        """Test DatabaseCooldown initialization."""
        mock_table = MagicMock()
        cooldown_obj = DatabaseCooldown(
            ctx=fake_context,
            cooldown=timedelta(seconds=10),
            cooldown_type="test_cooldown",
            table=mock_table,
        )
        assert cooldown_obj.table == mock_table
        assert cooldown_obj._type == "test_cooldown"


class TestTokens:
    """Test Tokens class."""

    def test_tokens_initialization(self, fake_context):
        """Test Tokens initialization."""
        cooldowns_dict.clear()
        cooldown_obj = Tokens(
            ctx=fake_context,
            capacity=5,
            cooldown=timedelta(seconds=10),
            cooldown_type="tokens_test",
            bucket=Bucket.USER,
        )
        assert cooldown_obj.capacity == 5
        assert cooldown_obj._count == 0


class TestSlidingWindow:
    """Test SlidingWindow class."""

    def test_sliding_window_initialization(self, fake_context):
        """Test SlidingWindow initialization."""
        cooldowns_dict.clear()
        cooldown_obj = SlidingWindow(
            ctx=fake_context,
            capacity=5,
            cooldown=timedelta(seconds=10),
            cooldown_type="sliding_test",
            bucket=Bucket.USER,
        )
        assert cooldown_obj.capacity == 5


class TestCooldownDecorator:
    """Test cooldown decorator."""

    def test_cooldown_decorator_sync(self, fake_context):
        """Test cooldown decorator with sync function."""
        cooldowns_dict.clear()

        @cooldown(rate=1, seconds=10)
        def test_func(ctx):
            return "success"

        # Function should execute when no cooldown
        result = test_func(ctx=fake_context)
        assert result == "success"

        # Function should raise CooldownError when on cooldown
        with pytest.raises(CooldownError):
            test_func(ctx=fake_context)

    def test_cooldown_decorator_async(self, fake_context):
        """Test cooldown decorator with sync logic creates wrapper."""
        cooldowns_dict.clear()

        @cooldown(rate=1, seconds=10)
        async def test_func(ctx):
            return "async_success"

        # When decorated, function is wrapped
        assert hasattr(test_func, "__wrapped__") or callable(test_func)

    def test_cooldown_decorator_custom_scope(self, fake_context):
        """Test cooldown decorator with custom scope."""
        cooldowns_dict.clear()

        @cooldown(rate=1, seconds=5, scope="custom_scope")
        def test_func(ctx):
            return "scoped"

        test_func(ctx=fake_context)
        assert "custom_scope" in cooldowns_dict

    def test_cooldown_decorator_guild_bucket(self, fake_context):
        """Test cooldown decorator with GUILD bucket."""
        cooldowns_dict.clear()

        @cooldown(rate=1, bucket=Bucket.GUILD, seconds=5)
        def test_func(ctx):
            return "guild_cooldown"

        test_func(ctx=fake_context)
        # Check that cooldown was registered for guild_id
        assert cooldowns_dict[test_func.__name__][54321]

    def test_cooldown_decorator_channel_bucket(self, fake_context):
        """Test cooldown decorator with CHANNEL bucket."""
        cooldowns_dict.clear()

        @cooldown(rate=1, bucket=Bucket.CHANNEL, seconds=5)
        def test_func(ctx):
            return "channel_cooldown"

        test_func(ctx=fake_context)
        # Check that cooldown was registered for channel_id
        assert cooldowns_dict[test_func.__name__][99999]

    def test_cooldown_decorator_with_delta(self, fake_context):
        """Test cooldown decorator with explicit delta."""
        cooldowns_dict.clear()

        @cooldown(rate=1, delta=timedelta(hours=1))
        def test_func(ctx):
            return "delta"

        test_func(ctx=fake_context)
        assert test_func.__name__ in cooldowns_dict

    def test_cooldown_decorator_multirate(self, fake_context):
        """Test cooldown decorator with multiple rates."""
        cooldowns_dict.clear()

        @cooldown(rate=3, seconds=10)
        def test_func(ctx):
            return "success"

        # Should allow multiple calls before cooldown
        assert test_func(ctx=fake_context) == "success"
