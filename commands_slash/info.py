from MFramework import register, Groups, Context, Embed, UserID, Snowflake, RoleID, ChannelID

@register()
async def info(ctx: Context, *args, language, **kwargs):
    '''Shows info'''
    pass

@register(group=Groups.GLOBAL, main=info)
async def user(ctx: Context, user_id: UserID = 0, *args, language, group, **kwargs):
    '''Shows user info'''
    await ctx.deferred()
    if group < Groups.MODERATOR or user_id == 0:
        user_id = ctx.member.user.id
    user = await ctx.bot.get_user(user_id)
    member = await ctx.bot.get_guild_member(ctx.guild_id, user_id)
    print(member.user == user) #If True, we don't need to query get_user

    embed = Embed().setTitle("User Info").setThumbnail("").setDescription("")

    await ctx.reply(embeds=[embed])

@register(group=Groups.MODERATOR, main=info)
async def server(ctx: Context, guild_id: Snowflake = 0, *args, language, group, **kwargs):
    '''Shows server info'''
    await ctx.deferred()
    if group < Groups.SYSTEM or guild_id == 0:
        guild_id = ctx.guild_id
    guild = await ctx.bot.get_guild(guild_id, True)
    channel_names = {"Widget":guild.widget_channel_id, "Rules":guild.rules_channel_id, "Public Updates":guild.public_updates_channel_id, "AFK":guild.afk_channel_id, "System":guild.system_channel_id}
    channels = [f"{key} Channel <#{value}>" for key, value in channel_names.items() if value]
    fields = {
        "Channels": f'Total Channels: {len(guild.channels)}\n'+'\n'.join(channels),
        "Emojis": f'Total Emojis: {len(guild.emojis)}',
        "Roles": f'Total Roles: {len(guild.roles)}',
        "Presences": f"Total Presences: {len(guild.presences)}",
        "Voice": f"{len(guild.voice_states)}\nAFK Timeout: {guild.afk_timeout}s",
        "Limits": f"Members: {guild.max_members}\nPresences: {guild.max_presences}\nVideo Users: {guild.max_video_channel_users}",
        "Boosters": f"Tier: {guild.premium_tier}\nBoosters: {guild.premium_subscription_count}",
        "Approximate Counts": f"Members: {guild.approximate_member_count}\nPresences: {guild.approximate_presence_count}", #TODO
        "Settings": "", #TODO
        "Region": f"Voice: {guild.region}\nLanguage: {guild.preferred_locale}",
        #"Widget": f"{guild.widget_enabled}", #TODO
        "Permissions": "", #TODO
        "Features": "", #TODO
        "General": f"{guild.member_count}" #TODO
    }
    embed = (
        Embed()
            .setTitle(guild.name)
            .setFooter(f"Server ID: {guild.id}")
            .setThumbnail(guild.get_icon(), width=500, height=500)
            .setImage(guild.get_splash())
            .setDescription(guild.description if guild.description else None)
            .setTimestamp(guild.id.as_date)
            .setAuthor(ctx.cache.members[guild.owner_id].user.username)
    )
    for field in fields:
        if fields[field] != "":
            embed.addField(field, fields[field], True)

    bans = await ctx.bot.get_guild_bans(guild_id)
    if bans != []:
        embed.addField(f"Amount of Bans", str(len(bans)), True)

    await ctx.reply(embeds=[embed])

@register(group=Groups.MODERATOR, main=info)
async def role(ctx: Context, role_id: RoleID = 0, *args, language, group, **kwargs):
    '''Shows role info'''
    await ctx.deferred()
    if role_id == 0:
        role_id = ctx.guild_id #Usually @everyone role has same id as guild
    roles = await ctx.bot.get_guild_roles(ctx.guild_id)
    role = list(filter(lambda x: x.id == role_id, roles))[0]

    color = str(hex(role.color)).replace("0x", "#")
    import time
    embed = (
        Embed()
            .setTitle(role.name)
            .setFooter(f"Role ID: {role.id}")
            .setTimestamp(role.id.as_date)
            .addField("Position", str(role.position), True)
            .addField("Displayed separately", str(role.hoist), True)
            .addField("Color", color, True)
            .addField("Mentionable", str(role.mentionable), True)
            .addField("Integration", str(role.managed), True)
            .addField("Permissions", str(role.permissions), True)
            .addField(
                "Created",
                str(
                    time.strftime(
                        "%Y-%m-%d %H:%M:%S",
                        role.id.as_date.timetuple(),
                    )
                ),
                True,
            )
            .setThumbnail("attachment://color.png")
    )
    embed.setColor(role.color)
    f = None
    if role.color:
        from mlib.colors import buffered_image
        from PIL import Image
        f = buffered_image(Image.new("RGB", (100, 100), color))
    await ctx.reply(embeds=[embed], file=f, filename="color.png")

@register(group=Groups.MODERATOR, main=info)
async def channel(ctx: Context, channel_id: ChannelID = 0, *args, language, group, **kwargs):
    '''Shows channel info'''
    await ctx.deferred()
    if channel_id == 0:
        channel_id = ctx.channel_id
    channel = await ctx.bot.get_channel(channel_id)

    embed = Embed().setTitle("Channel Info").setThumbnail("").setDescription("")

    await ctx.reply(embeds=[embed])

@register(group=Groups.GLOBAL, main=info)
async def created(ctx: Context, snowflake: Snowflake, *args, language, **kwargs):
    '''
    Shows when the snowflake was created
    Params
    ------
    snowflake:
        Snowflake to check
    '''
    await ctx.deferred()
    embed = Embed().setFooter('Dates are in format YYYY/MM/DD HH:MM UTC')
    import time
    r = '\nOn Discord since: ' + str(time.strftime("%Y-%m-%d %H:%M", snowflake.as_date.timetuple()))
    try:
        member = await ctx.bot.get_guild_member(ctx.guild_id, snowflake)
        r += '\nJoined Server at: ' + str(time.strftime("%Y-%m-%d %H:%M", member.joined_at.timetuple()))
        try:
            r += '\nBooster since: ' + str(time.strftime("%Y-%m-%d %H:%M", member.premium_since.timetuple()))
        except:
            pass
    except:
        pass
    embed.addField("\u200b",f"<@{snowflake}>"+r)
    await ctx.reply(embeds=[embed])
