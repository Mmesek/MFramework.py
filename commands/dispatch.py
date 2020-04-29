from MFramework.discord.mbot import onDispatch
from MFramework.commands import execute, parse, compilePatterns
from MFramework.discord.objects import *
from MFramework.database.cache import Cache, CacheDM
from MFramework.utils import log

import time


@onDispatch(Ready)
async def ready(self, data):
    self.session_id = data.session_id
    self.user_id = data.user.id
    self.username = data.user.username
    self.startTime = time.time()
    compilePatterns(self)
    print("Conntected as:", data.user.username)


def isDM(data) -> bool:
    return (
        data.webhook_id == 0
        and data.author != None
        and data.guild_id == 0
        and data.author.bot is False
        and data.content != ""
    )


@onDispatch(Message)
async def message_create(self, data: Message):
    if (
        data.webhook_id == 0
        and data.author != None
        and data.guild_id != 0
        and data.author.bot is False
        and data.content != ""
    ):
        if (
            (self.username.lower() in data.content.lower())
            or any(i in data.content.lower()[0] for i in [self.cache[data.guild_id].alias, self.alias])
            or self.user_id in [u.id for u in data.mentions]
        ) and await execute(self, data) != 0:
            return
        elif "discordapp.com/channels/" in data.content:
            return  # await quote(self, data)
        elif await parse(self, data) == None:
            return
        self.cache[data.guild_id].message(data.id, data)
    elif data.author.bot is False and data.guild_id == 0:
        await log.DirectMessage(self, data)
        if data.channel_id not in self.cache["dm"]:
            self.cache["dm"][data.channel_id] = CacheDM()
        self.cache["dm"][data.channel_id].message(data)
    return


@onDispatch(Message)
async def message_update(self, data):
    if data.guild_id == 0 or data.webhook_id != 0 or data.content == None:
        return
    webhook = self.cache[data.guild_id].logging
    if not any(i in webhook for i in ["all", "message_update"]):
        return
    if "message_update" in webhook:
        webhook = webhook["message_update"]
    else:
        webhook = webhook["all"]
    embed = log.MessageUpdated(self, data)
    if embed == None:
        return
    if webhook == []:
        return
    await self.webhook([embed.embed], "", webhook[0])
    self.cache[data.guild_id].message(data)


@onDispatch(Guild)
async def guild_create(self, guild):
    self.cache[guild.id] = Cache(guild, self.db, self.user_id, self.alias)


@onDispatch(Guild_Member)
async def guild_member_add(self, data):
    await self.db.influxMember(data.guild_id, data.user.id, True, data.joined_at)


@onDispatch(Guild_Member_Remove)
async def guild_member_remove(self, data):
    await self.db.influxMember(data.guild_id, data.user.id, False)


@onDispatch(Guild_Members_Chunk)
async def guild_members_chunk(self, data):
    s = self.cache[data.guild_id]
    if type(s.joined) != list:
        s.joined = []
    for member in data.members:
        s.joined += [(member.user.id, member.joined_at, member.premium_since)]


@onDispatch(Message_Delete)
async def message_delete(self, data):
    if data.guild_id == 0:
        return
    webhook = self.cache[data.guild_id].logging
    if not any(i in webhook for i in ["all", "message_delete"]):
        return
    if "message_delete" in webhook:
        webhook = webhook["message_delete"]
    else:
        webhook = webhook["all"]
    embed = log.MessageRemoved(self, data)
    if embed == None:
        return
    webhook = self.cache[data.guild_id]["logging"]["all"]
    if webhook == "" or webhook == None or webhook == []:
        return
    return await self.webhook([embed], "", webhook[0])


@onDispatch(Message_Reaction_Add)
async def message_reaction_add(self, data):
    if data.guild_id == 0 or data.member.user.bot:
        return
    roles = self.cache[data.guild_id].reactionRoles
    if roles == {}:
        return
    r = None
    for group in roles:
        for m in roles[group]:
            if data.message_id == m:
                r = roles[group][data.message_id][f"{data.emoji.name}:{data.emoji.id}"]
                if r == None:
                    return
                for role in data.member.roles:
                    if group == "None":
                        continue
                    for emoji in roles[group][data.message_id].values():
                        if emoji == role:
                            return await self.delete_user_reaction(
                                data.channel_id, data.message_id, f"{data.emoji.name}:{data.emoji.id}", data.user_id,
                            )
                    if r == role:
                        return
    if r == None:
        return
    for i in r:
        await self.add_guild_member_role(data.guild_id, data.user_id, i, "Reaction Role")


@onDispatch(Message_Reaction_Remove)
async def message_reaction_remove(self, data):
    if data.guild_id == 0:
        return
    roles = self.cache[data.guild_id].reactionRoles
    if roles == {}:
        return
    role = None
    for group in roles:
        for g in roles[group]:
            if data.message_id in roles[group]:
                role = roles[group][data.message_id][f"{data.emoji.name}:{data.emoji.id}"]
                if role == None:
                    return
                break
    if role == None:
        return
    for i in role:
        await self.remove_guild_member_role(data.guild_id, data.user_id, i, "Reaction Role")

import MFramework.database.alchemy as db
@onDispatch(Presence_Update)
async def presence_update(self, data):
    if data.guild_id == 0 or data.user.bot:
        return
    if self.cache[data.guild_id].trackPresence:
        session = self.db.sql.session()
        g = session.query(db.Games).filter(db.Games.UserID == data.user.id).filter(db.Games.Title == data.game.name).first()
        if g == None:
            g = db.Games(data.user.id, data.game.name)
        g.LastPlayed = data.game.created_at
        session.commit()
    roles = self.cache[data.guild_id].presenceRoles
    if roles == None:
        return
    role = None
    for group in roles:
        for g in roles[group]:
            if data.game.type == 0 and data.game.name in roles[group].keys():
                role = roles[group][data.game.name]
                if role == None or role in data.roles:
                    return
                break
    return await self.add_guild_member_role(data.guild_id, data.user.id, role, "Presence Role")
