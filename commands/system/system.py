from MFramework.commands import register
from MFramework.utils.timers import *

@register(group="System", help="Shuts bot down.")
async def shutdown(self, *args, data, **kwargs):
    if self.cache[data.guild_id].trackVoice:
        for v in self.cache[data.guild_id].voice:
            for u in self.cache[data.guild_id][v]:
                finalize(self, data.guild_id, v, u)
    await self.close()
    print("Received shutdown command. Shutting down.")

@register(group='System', help="Changes Bot's status")
async def updateStatus(self, status="How the World Burns", status_kind="Online", status_type=3, afk=False, *args, data, **kwargs):
    """Kind - Online/dnd/idle/invisible/offline\nType - 0 - Playing, 1 - Streaming, 2 - Listening, 3 - Watching"""
    await self.status_update(status_kind, status, status_type, afk)

@register(group="System", help="Reloads commands files.")
async def reloadCommands(self, *args, data, **kwargs):
    """This probably needs to be placed in another file but well, it's here currently FOR SCIENCE."""
    import importlib
    importlib.reload(__name__)