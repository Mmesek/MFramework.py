from MFramework import onDispatch, Bot, Ready

@onDispatch
async def ready(self: Bot, ready: Ready):
    self.session_id = ready.session_id
    self.user_id = ready.user.id
    self.username = ready.user.username
    import time
    self.startTime = time.time()
    print("Conntected as:", ready.user.username)

@onDispatch
async def ready(self: Bot, ready: Ready):
    if getattr(self, 'registered', False):
        return
    self.application = await self.get_current_application_information()
    from MFramework.commands.interactions import register_interactions
    await register_interactions(self)
    self.registered = True

from MFramework import Presence_Update, Activity_Types

@onDispatch
async def presence_update(self: Bot, data: Presence_Update):
    if data.guild_id == 0 or data.user.bot or (data.client_status.web != ''):
        return
    from MFramework.database.alchemy.types import Tracking #FIXME
    from mlib.utils import bitflag
    if bitflag(self.cache[data.guild_id].tracking, Tracking.Presence):
        if (
            data.user.id in self.cache[data.guild_id].presence 
            and (data.activities is [] 
                or data.activities[0].name != self.cache[data.guild_id].presence[data.user.id][0])
        ):
            s = self.cache[data.guild_id].presence.pop(data.user.id)
            elapsed = 0 #TODO
            self.db.influx.commitPresence(data.guild_id, data.user.id, s[0], elapsed)
        if (
            data.user.id not in self.cache[data.guild_id].presence 
            and len(data.activities) > 0 
            and data.activities[0].type == 0 
            and data.activities[0].name is not None
        ):
            self.cache[data.guild_id].presence.store(data)

    for stream in filter(lambda x: x.type == Activity_Types.STREAMING, data.activities):
        if stream.name in self.cache[data.guild_id].tracked_streams:
            await self.cache[data.guild_id].logging["stream"](data, stream)
    
    for roles in self.cache[data.guild_id].presence_roles.values():
        for a in filter(lambda x: x.type == Activity_Types.GAME and x.name in roles.keys(), data.activities):
            for i in roles[a.name]:
                await self.add_guild_member_role(data.guild_id, data.user.id, i, "Presence Role")
            break
