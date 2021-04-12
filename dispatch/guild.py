from MFramework import onDispatch, Bot, Guild, Guild_Member_Add, Guild_Member_Remove, Guild_Members_Chunk

@onDispatch
async def guild_create(self: Bot, guild: Guild):
    if guild.id not in self.cache:
        import time
        start = time.time()
        from MFramework.database.cache import GuildCache
        self.cache[guild.id] = GuildCache(self, guild)
        from MFramework.utils.scheduler import add_guild_tasks
        add_guild_tasks(self, guild.id)
        print('Guild', guild.id, 'initialized in:', time.time() - start)
    if len(self.cache[guild.id].members) < 10:
        await self.request_guild_members(guild.id)

@onDispatch
async def guild_member_add(self: Bot, data: Guild_Member_Add):
    await self.db.influx.influxMember(data.guild_id, data.user.id, True, data.joined_at)
    await self.cache[data.guild_id].logging["join"](data)
    self.cache[data.guild_id].members.store(data)

@onDispatch
async def guild_member_remove(self: Bot, data: Guild_Member_Remove):
    await self.db.influx.influxMember(data.guild_id, data.user.id, False)
    await self.cache[data.guild_id].logging["left"](data)
    self.cache[data.guild_id].members.delete(data.user.id)

@onDispatch
async def guild_members_chunk(self: Bot, data: Guild_Members_Chunk):
    self.cache[data.guild_id].members.update(data.members)