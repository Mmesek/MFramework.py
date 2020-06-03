from MFramework.commands import register

from MFramework.utils.utils import Embed, created, datetime, time

from PIL import Image
from io import BytesIO
import re
@register(group="Mod", help="Sends user DM as a bot")
async def dm(self, user, *message, data, language, **kwargs):
    uid = re.findall(r'\d+', user)
    if uid == []:
        await self.message(data.channel_id, "No UserID found in message. @User or provide their ID")
        return await self.create_reaction(data.channel_id, data.id, self.emoji['failure'])
    dm = await self.create_dm(uid[0])
    if await self.message(dm.id, ' '.join(message)) == []:
        await self.message(data.channel_id, "Couldn't Deliver message to specified user.")
        return await self.create_reaction(data.channel_id, data.id, self.emoji['failure'])
    return await self.create_reaction(data.channel_id, data.id, self.emoji['success'])

async def _dm(self, user, message, embed={}):
    if user not in self.cache['dm']:
        dm = await self.create_dm(user)
    if await self.embed(dm.id, message) == []:
        return False
    return True

@register(group="Mod", help="Sends message to a channel as a bot. DOES NOT SEND CHANNEL MENTIONS")
async def say(self, *message, data, channel, **kwargs):
    if await self.message(channel[0], ' '.join(message)) == []:
        return await self.create_reaction(data.channel_id, data.id, self.emoji['failure'])
    return await self.create_reaction(data.channel_id, data.id, self.emoji['success'])


@register(group="Mod", help="Reacts to a message with emoji as a bot")
async def react(self, messageID, *reactions, data, channel, **kwargs):
    for each in reactions:
        await self.create_reaction(channel[0], messageID, each.replace("<:", "").replace(">", ""))
    return await self.create_reaction(data.channel_id, data.id, self.emoji['success'])

import asyncio
async def fetch_members(self, guild):
    server = self.cache[guild]
    m_retries = 0
    if len(server.joined) != server.member_count:
        if len(server.joined) >= server.member_count:
            server.joined = []
        await self.request_guild_members(guild)
    while len(server.joined) != server.member_count and len(server.joined) < server.member_count:
        await asyncio.sleep(0.1)
        m_retries+=1
        if m_retries == 75:
            break

@register(group='Admin', help='Lists members with specified role', alias='', category='')
async def listmembers(self, role, *args, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    rid = int(re.findall(r'\d+', role)[0])
    await self.trigger_typing_indicator(data.channel_id)
    await fetch_members(self, data.guild_id)
    s_member = self.cache[data.guild_id].joined
    total = []
    for each in s_member:
        if rid in each[3]:
            total += [each[0]]
    embed = Embed().setDescription(''.join([f'<@{i}>' for i in total])[:2024]).setFooter('', f'Total users: {len(total)}')
    for role in self.cache[data.guild_id].roles:
        if role.id == rid:
            embed.setColor(role.color).setTitle(f'List of members with role {role.name}')
    await self.embed(data.channel_id, '', embed.embed)

async def handleInfraction(self, data, infraction):
    params = data.content.split(" ", 1)
    uid = params[0]
    reason = params[1]
    if infraction[0] == "Warn":
        duration = 0
    else:
        duration = 0  # There is some need of handling it tho.
    await self.db.insert(
        "Infractions",
        "GuildID,UserID,Timestamp,Reason,ModeratorID,Duration,InfractionType",
        [data.guild_id, uid, data.timestamp, reason, data.author.id, duration, infraction[0]],
    )
    guild = await self.get_guild(data.guild_id)
    guild = guild.name
    cid = await self.make_dm(uid)
    result = await self.message(cid.id, f"You've been {infraction[1]} in {guild} server for {reason}")
    if "code" in result:
        await self.message(
            data.channel_id, f"Couldn't deliver {infraction[2]} to user <@{uid}> due to: {result.message}"
        )
    else:
        await self.message(data.channel_id, f"Delivered {infraction[2]} to user <@{uid}> for: {reason}")
    if uid == "273499695186444289":
        await self.message(data.channel_id, "No.")
        return
    if infraction[0] in {"Mute", "Kick", "Ban"}:
        delete = 0
        g = self.cache.cachedRoles(data.guild_id, data.mentions[0].member.roles)
        if g not in {"Global", "Vip", "Nitro"}:
            await self.message(
                data.channel_id,
                f"{infraction[1].capitalize()} 🔨... Can not ban <@{uid}> because CAN NOT BAN MODERATOR OR ADMINISTRATOR REEEEEEE",
            )
        else:
            if infraction[0] == "Mute":
                try:
                    role = self.cache[data.guild_id].groups["Muted"][0]
                    r = await self.role_add(
                        data.guild_id, uid, role, f"Requested by {data.author.username}"
                    )
                except:
                    await self.message(
                        data.channel_id, f"Couldn't perform operation. Muted role or permission is missing."
                    )
            elif infraction[0] == "Kick":
                r = await self.kick_user(
                    data.guild_id, uid, reason, f"Requested by {data.author.username}"
                )
            elif infraction[0] == "Ban":
                r = await self.ban_user(
                    data.guild_id, uid, reason, delete, f"Requested by {data.author.username}"
                )
            if "code" in r:
                await self.message(
                    data.channel_id,
                    f"Couldn't perform operation. Missing Permission. (Attempted action: {infraction[0]})",
                )
            else:
                await self.message(
                    data.channel_id, f"{infraction[1].capitalize()} 🔨 <@{uid}> for {reason}"
                )


@register(group="Mod", category="Moderation", help="Warns user.", notImpl=True)
async def warn(self, user, *reason, data, **kwargs):
    await handleInfraction(self, data, ["Warn", "warned", "Warning"])


@register(group="Mod", category="Moderation", help="Mutes user.", notImpl=True)
async def mute(self, user, time=0, *reason, data, **kwargs):
    await handleInfraction(self, data, ["Mute", "muted", "mute reason"])


@register(group="Mod", category="Moderation", help="Kicks user.", notImpl=True)
async def kick(self, user, *reason, data, **kwargs):
    await handleInfraction(self, data, ["Kick", "kicked", "kick reason"])


@register(group="Mod", category="Moderation", help="Bans user.", notImpl=True)
async def ban(self, user, time=0, *reason, data, **kwargs):
    await handleInfraction(self, data, ["Ban", "banned", "ban reason"])


@register(help="Shows Infractions of user.", notImpl=True)
async def infractions(self, *users, data, **kwargs):
    uids = data.content.split("!", 1)[0].split(" ")
    if uids == [""]:
        uids = [data.author.id]
    for uid in uids:
        member = await self.get_member(data.guild_id, uid)
        avatar = member.user.avatar
        joined = str(
            time.strftime("%Y-%m-%d %H:%M:%S", datetime.datetime.fromisoformat(member.joined_at).timetuple())
        )
        embed = (
            Embed()
            .setAuthor(
                f"{member.user.username}#{member.user.discriminator}",
                "",
                f"https://cdn.discordapp.com/avatars/{member.user.id}/{avatar}",
            )
            .setTimestamp(joined)
            .setTitle("Infractions")
            .setFooter("", f"User ID: {member.user.id}. Joined Server ")
        )
        infractions = await self.db.selectMultiple(
            "Infractions",
            "Timestamp,Reason,ModeratorID,Duration,InfractionType",
            "WHERE GuildID=? AND UserID=?",
            [data.guild_id, member.user.id],
        )
        infractions = reversed(infractions)
        if infractions != []:
            w, m, b = 0, 0, 0
            inf_total = ""
            for i in infractions:
                if i[4] == "Warn":
                    w += 1
                elif i[4] == "Mute":
                    m += 1
                elif i[4] == "Ban":
                    b += 1
                f = f"[{i[0][0:16].replace('T',' ')}] [{i[4]}] **{i[1]}** by <@{i[2]}>\n"
                if len(inf_total + f) < 2048:
                    inf_total += f
            infractions = inf_total
            total = f"Warns: [{w}]\nMutes: [{m}]\nBans: [{b}]"
            embed.setDescription(f"{infractions}").addField("Total Infractions", total, True)
    await self.embed(data.channel_id, "", embed.embed)

from MFramework.database import alchemy as db
@register(group="Mod", category="Moderation", help="Shows information about user.", notImpl=True)
async def userInfo(self, *users, data, **kwargs):
    uids = data.content.split("!", 1)[0].split(" ")
    if uids == [""]:
        uids = [data.author.id]
    for uid in uids:
        member = await self.get_guild_member(data.guild_id, uid)
        jdiscord = str(created(member.user.id))
        avatar = member.user.avatar
        if avatar[0:2] == "a_":
            avatar += ".gif"
        embed = (
            Embed()
            .setTitle(f"{member.user.username}#{member.user.discriminator}")
            .setFooter("", f"User ID: {member.user.id}")
            .setTimestamp(jdiscord)
            .setThumbnail(f"https://cdn.discordapp.com/avatars/{member.user.id}/{avatar}")
        )
        roles = ""
        for role in member.roles:
            if roles != "":
                roles += ", "
            if (len(roles) + len(role)) <= 1023:
                roles += f"<@&{role}>"
        joined = str(
            time.strftime("%Y-%m-%d %H:%M:%S", datetime.datetime.fromisoformat(member.joined_at).timetuple())
        )
        if member.premium_since != None:
            nitro = str(
                time.strftime("%Y-%m-%d %H:%M:%S", datetime.datetime.fromisoformat(member.premium_since).timetuple())
            )
        else:
            nitro = member.premium_since
        discord = str(time.strftime("%Y-%m-%d %H:%M:%S", datetime.datetime.fromisoformat(jdiscord).timetuple()))
        names = {
            "nick": ("Nick", f"{member.nick}", False),
            "roles": ("Roles", f"{roles}", False),
            "premium_since": ("Nitro", f"{nitro}", True),
            "joined_at": ("Joined", f"**Discord:**\n{discord}\n**Server:**\n{joined}", True),
            "mute": ("Voice", f"Guild Deaf: {member.deaf}\nGuild Mute: {member.mute}", True),
        }
        order = ["nick", "joined_at", "premium_since", "deaf", "roles"]
        for key in order:
            if (
                member[key] != None
                and member[key] != []
                and member[key] != False
                and member[key] != 0
                and key not in ["user"]
            ):
                res = names.get(key)
                if res != None:
                    embed.addField(f"{res[0]}", f"{res[1]}", res[2])
        session = self.db.sql.session()
        infractions = session.query(db.Infractions.timestamp, db.Infractions.reason, db.Infractions.ModeratorID, db.Infractions.Duration, db.Infractions.InfractionType).filter(db.Infractions.UserID == member.user.id).filter(db.Infractions.GuildID == data.guildID).first()
        if infractions != []:
            infractions = reversed(infractions)
            w, m, b = 0, 0, 0
            inf_total = ""
            for i in infractions:
                if i[4] == "Warn":
                    w += 1
                elif i[4] == "Mute":
                    m += 1
                elif i[4] == "Ban":
                    b += 1
                f = f"[{i[0][0:16].replace('T',' ')}] [{i[4]}] **{i[1]}** by <@{i[2]}>\n"
                if len(inf_total + f) < 1024:
                    inf_total += f
            infractions = inf_total
            total = f"Warns: [{w}]\nMutes: [{m}]\nBans: [{b}]"
            embed.addField("Infractions", f"{infractions}").addField("Total Infractions", total, True)
        embed.setDescription(f"Requested by <@{data.author.id}> for user <@{member.user.id}>")
        await self.embed(data.channel_id, "", embed.embed)


@register(group="Mod", category="Moderation", help="Shows information about server.", notImpl=True)
async def serverInfo(self, *args, data, **kwargs):
    server = await self.get_guild(data.guild_id)
    icon = server.icon
    if icon[0:2] == "a_":
        icon += ".gif"
    else:
        icon += ".png"
    features = ""
    if server.features != None:
        for feature in server.features:
            if features != "":
                features += ", "
            features += feature.lower().capitalize().replace("_", " ")
            features = features.replace(', ', '\n')

    verification = {
        0: "No",
        1: "Verified email",
        2: "Registered longer than 5 minutes",
        3: "Member for longer than 10 minutes",
        4: "Verified phone number"
    }
    notifications = {
        0: "All Messages",
        1: "Only Mentions"
    }
    explicit_filter = {
        0: "Disabled",
        1: "Members without roles",
        2: "All Members" 
    }
    mfa = {
        0: "None",
        1: "Elevated"
    }
    system_flags = {
        0: "?",
        1: "No member join message",
        2: "No boost message"
    }
    names = {
        "owner_id": ("Owner", f"<@{server.owner_id}>", True),
        "features": ("VIP Perks", f"{features}", False),
        "region": ("Region", f"Voice: {server.region}\nLanguage: {server.preferred_locale}", False),
        "afk_channel_id": (
            "AFK",
            f"Timeout: {server.afk_timeout/60}minutes\nChannel: <#{server.afk_channel_id}>",
            True,
        ),
        "default_message_notifications": ("Message Notifications", f"{notifications[server.default_message_notifications]}", True),
        "roles": ("Roles", f"{len(server.roles)}", True),
        "emojis": ("Emojis", f"{len(server.emojis)}", True),
        "premium_subscription_count": (
            "Boost",
            f"Tier: {server.premium_tier}\nBoosters: {server.premium_subscription_count}",
            True,
        ),
        "verification_level": ("Verification Level", f"{verification[server.verification_level]}", True),
        "vanity_url_code": (
            "Vanity URL",
            f"gg/[{server.vanity_url_code}](http://discord.gg/{server.vanity_url_code})",
            True,
        ),
        "mfa_level": ("MFA Level", f"{mfa[server.mfa_level]}", True),
        "explicit_content_filter": ("Content Filter", f"{explicit_filter[server.explicit_content_filter]}", True),
        "embed_enabled": (
            "Embed",
            f"<#{server.embed_channel_id}>",
            True,
        ),
        "widget_enabled": (
            "Widget",
            f"<#{server.widget_channel_id}>",
            True,
        ),
        "system_channel_id": (
            "System",
            f"<#{server.system_channel_id}>\n{system_flags[server.system_channel_flags]}",
            True,
        ),
        "application_id": ("Application ID", f"{server.application_id}"),
        "max_members":("Members", f"{self.cache[data.guild_id].member_count}", True)
    }
    order = [
        "owner_id",
        "vanity_url_code",
        "region",
        "roles",
        "emojis",
        "max_members",
        "features",
        "afk_channel_id",
        "embed_enabled",
        "widget_enabled",
        "system_channel_id",
        "verification_level",
        "mfa_level",
        "explicit_content_filter",
        "default_message_notifications",
        "premium_subscription_count",
    ]
    print("Embed")
    embed = (
        Embed()
        .setTitle(server.name)
        .setTimestamp(str(created(server.id)))
        .setFooter("", f"Server ID: {server.id}")
        .setThumbnail(f"https://cdn.discordapp.com/icons/{server.id}/{icon}")
        .setImage(f"https://cdn.discordapp.com/splashes/{server.id}/{server.splash}")
    )
    if server.description != None:
        embed.setDescription(server.description)
    for key in order:
        val = getattr(server, key, None)
        if  val!=0 and val is not None and val != [] and key not in ["icon", "name", "id", "splash", "banner"]:
            res = names.get(key, None)#getattr(server, key, None)
            if res != None:
                embed.addField(f"{res[0]}", f"{res[1]}", res[2])
    if False:
        if (
            server[key] != None
            and server[key] != []
            and server[key] != False
            and server[key] != 0
            and key not in ["icon", "name", "id", "splash", "banner"]
        ):
            res = names.get(key)
            if res != None:
                embed.addField(f"{res[0]}", f"{res[1]}", res[2])
    bans = await self.get_guild_bans(data.guild_id)
    if bans != []:
        embed.addField(f"Amount of Bans", len(bans), True)
    #embed.setColor(data.guild_id[:7])
    print("sending", embed.embed)
    print(await self.embed(data.channel_id, "", embed.embed))

from MFramework.utils.utils import replaceMultiple
@register(group="Mod", category="Moderation", help="Shows information about role.", notImpl=True)
async def roleInfo(self, *roles, data, **kwargs):
    rid = data.content.split("!", 1)[0].split(" ")
    if rid == [""]:
        rid = [data.member.roles[0]]
    roles = await self.get_guild_roles(data.guild_id)
    for r in rid:
        for role in roles:
            r = replaceMultiple(r, ['<','>','&', '@'], '')
            if role.id == int(r):
                color = str(hex(role.color)).replace("0x", "#")
                img = Image.new("RGB", (100, 100), color)
                embed = (
                    Embed()
                    .setColor(role.color)
                    .setTitle(role.name)
                    .setFooter("", f"Role ID: {role.id}")
                    .setTimestamp(str(created(role.id)))
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
                                datetime.datetime.fromisoformat(str(created(role.id))).timetuple(),
                            )
                        ),
                        True,
                    )
                    .setThumbnail("attachment://color.png")
                )
                buffered = BytesIO()
                img.save(buffered, format="PNG")
                img_str = buffered.getvalue()
                await self.withFile(data.channel_id, img_str, "color.png", "", embed.embed)

@register(group='Mod', help='Shows creation date based on provided snowflakes')
async def creationdate(self, *snowflake, data, **kwargs):
    embed = Embed().setFooter('','Dates are in format YYYY/MM/DD HH:MM UTC')
    for flake in snowflake:
        r = '\nOn Discord since: ' + str(time.strftime("%Y-%m-%d %H:%M", datetime.datetime.fromisoformat(str(created(flake))).timetuple()))
        try:
            member = await self.get_member(data.guild_id, flake)
            r += '\nJoined Server at: ' + str(time.strftime("%Y-%m-%d %H:%M", datetime.datetime.fromisoformat(member.joined_at).timetuple()))
            try:
                r += '\nBooster since: ' + str(time.strftime("%Y-%m-%d %H:%M", datetime.datetime.fromisoformat(member.premium_since).timetuple()))
            except:
                pass
        except:
            pass
        embed.addField("\u200b",f"<@{flake}>"+r)
    await self.embed(data.channel_id, '', embed.embed)
