from MFramework import onDispatch, Bot, Guild_Member_Update
async def new_booster(ctx, user_id, guild_id):
    greeting, color, fine_print, if_interest, ending, note = [], [], [], [], [], []
    from random import choice
    cmd_line = "`/role` `color: #HexadecimalColor` `name: Name of your role`"
    message = ' '.join([choice(greeting).format(user=user_id), choice(color), choice(fine_print), choice(if_interest).format(cmd_line), choice(ending), choice(note)])
    await ctx.create_message(ctx.cache[guild_id].nitro_channel, message)

async def end_booster(ctx, user_id):
    #TODO
    pass

@onDispatch
async def guild_member_update(self: Bot, data: Guild_Member_Update):
    await self.cache[data.guild_id].logging["member_update"](data)
    await self.cache[data.guild_id].logging["muted_change"](data)
    is_boosting = await self.cache[data.guild_id].logging["nitro_change"](data)

    if is_boosting and self.cache[data.guild_id].nitro_channel:
        await new_booster(self, data.user.id, data.guild_id)
    elif is_boosting is False and self.cache[data.guild_id].nitro_channel:
        await end_booster(self, data.user.id, data.guild_id)

    self.cache[data.guild_id].members.update(data)