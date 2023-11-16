from enum import IntFlag
from datetime import timedelta

from . import Context


class Context_Keys(IntFlag):
    USER = (0x1, "user_id")
    MESSAGE = (0x2, "message_id")
    CHANNEL = (0x4, "channel_id")
    SERVER = (0x8, "guild_id")
    GROUP = (0x10, "permission_level")

    def __new__(cls, value: int, field=None):
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.member = field
        return obj

    def __init__(self, value: int, field: str = "") -> None:
        self._value_ = value
        self.member = field


class Custom_Context(Context):
    key: Context_Keys = Context_Keys.USER | Context_Keys.SERVER
    """Unique key under which context can be found"""
    expire_after: timedelta = timedelta(days=1)
    """How long context should remain active/in cache"""

    def __hash__(self) -> int:
        # TODO: Fetch member values from self.key, then assemble unique-ish key based on it
        return hash((getattr(self, key.member) for key in self.key))

    def namespace(self) -> str:
        return ":".join(reversed([str(getattr(self, key.member)) for key in self.key]))


"""
Data Structure that can be passed between multiple commands that retains it's content depending on key settings
- context.key is bitshifted value for merging multiple keys
- context should be cachable
- context should be serializable/deserializable
- context can be passed as type to function. Runner will automatically detect it from data type and fetch or create new one
- context can contain methods that are commands within, in that case regular Context should be injected into it as self
- should namespace be used and cached instead of context? 
    - Namespace would prohibit modifying regular context while guaranteeing context variables to always be an up to date environment related
    - Namespace would also be passed as type to functions instead of context. However that means namespace needs to be explicitly stated, context would do so automatically
    - Namespace couuld act as custom data structure that can be used in functions as type which could work in more generalized situations
    - Otherwise serializer would need to only serialize final variables and strip rest
"""
