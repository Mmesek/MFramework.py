from MFramework import onDispatch, Bot, Guild_Ban_Add, Guild_Ban_Remove

async def get_ban_data(self: Bot, data, type, audit_type):
    import asyncio
    await asyncio.sleep(3)
    audit = await self.get_guild_audit_log(data.guild_id, action_type=audit_type)
    reason = None
    for obj in audit.audit_log_entries:
        #Try to find ban in Audit Log
        if int(obj.target_id) == data.user.id:
            moderator = obj.user_id
            reason = obj.reason
            break
    if reason is None and type == 'ban':
        #Fall back to fetching ban manually
        reason = await self.get_guild_ban(data.guild_id, data.user.id)
        reason = reason.reason
    r = None #TODO: Get from database
    if r is None:
        #TODO: Add to Databse
        return reason, moderator
    return False, False

@onDispatch
async def guild_ban_add(self: Bot, data: Guild_Ban_Add):
    reason, moderator = await get_ban_data(self, data, "ban", 22)
    if reason is not False:
        await self.cache[data.guild_id].logging["infraction_event"](data, type="banned", reason=reason, by_user=moderator)

@onDispatch
async def guild_ban_remove(self: Bot, data: Guild_Ban_Remove):
    reason, moderator = await get_ban_data(self, data, "unban", 23)
    if reason is not False:
        await self.cache[data.guild_id].logging["infraction_event"](data, type="unbanned", reason=reason, by_user=moderator)
