from typing import Any

from . import Context


class Settings_Namespace:
    def items(self) -> dict[str, Any]:
        return {i: getattr(self, i) for i in dir(self) if not i.startswith("_") and not callable(getattr(self, i))}


class Settings_Context(Context):
    settings: Settings_Namespace
    """Loaded Settings"""

    async def _load_cached_settings(self) -> None:
        """Load cached settings"""
        self.cache.settings

    async def _load_settings(self) -> None:
        """Force loading settings from database"""

    async def _cache_settings(self) -> None:
        """Cache settings locally. Overwrites existing settings"""

    async def _save_settings(self) -> None:
        """Save settings to database. Merges with existing settings"""


"""
Context that handles settings management. Useful for commands that utilize specific settings.

- New settings should be added to namespace in-code
- settings should be loaded into local cache on startup
- settings should be loaded from local cache on initialization
- settings should be saved to database and their cache should be updated as well
- settings should be used as namespace members
"""
