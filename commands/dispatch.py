from MFramework.discord.mbot import onDispatch
from MFramework.commands import execute, parse, compilePatterns
from MFramework.discord.objects import *
from MFramework.database.cache import Cache, CacheDM
from MFramework.utils import log, utils

import time, datetime


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

import re, random
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
        if data.channel_id == 463437626515652618:
            reg = re.findall(r"\*.+\*", data.content)
            if reg:
                v = random.randint(1, 600)
                reactions = {
                    1:'1️⃣',2:'2️⃣',3:'3️⃣',
                    4:'4️⃣',5:'5️⃣',6:'6️⃣'
                }
                await self.create_reaction(data.channel_id, data.id, reactions.get(int(v / 100) + 1))
        elif data.channel_id == 466643151470198786:
            embed = utils.Embed().setDescription(data.content)
            await self.webhook([embed.embed],'','569802933227618318/6AJW6rQjG0mlGvTFNZDfGiUqJCkd3EHDkAIDyJ7rwx-SA9uXP2xITwV9OGHg2YLwzgTS', data.author.username, f'https://cdn.discordapp.com/avatars/{data.author.id}/{data.author.avatar}.png')
        self.cache[data.guild_id].message(data.id, data)
        if data.channel_id not in self.cache[data.guild_id].disabled_channels and not any(r in data.member.roles for r in self.cache[data.guild_id].disabled_roles):
            session = self.db.sql.session()
            last = self.cache[data.guild_id].exp.get(data.author.id, 0)
            timestamp = datetime.datetime.fromisoformat(data.timestamp)
            if last == 0:
                e = db.UserLevels(data.guild_id, data.author.id, 1, 0, timestamp)
                self.cache[data.guild_id].exp[data.author.id] = timestamp
                self.db.sql.add(e)
            elif (last == None or (timestamp - last).total_seconds() > 60) and (len(set(data.content.split(' '))) >= 2):
                #if (len(self.cache[data.guild_id].messages) > 1) and (self.cache[data.guild_id].messages[list(self.cache[data.guild_id].messages.keys())[-1]].content == data.content):
                #    return
                e = session.query(db.UserLevels).filter(db.UserLevels.GuildID == data.guild_id).filter(db.UserLevels.UserID == data.author.id).first()
                e.EXP += 1
                e.LastMessage = timestamp
                self.cache[data.guild_id].exp[data.author.id] = timestamp
                session.commit()
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
    elif data.channel_id == 466643151470198786:
        embed = utils.Embed().setDescription(data.content).setTitle("MESSAGE UPDATE")
        await self.webhook([embed.embed],'','569802933227618318/6AJW6rQjG0mlGvTFNZDfGiUqJCkd3EHDkAIDyJ7rwx-SA9uXP2xITwV9OGHg2YLwzgTS', data.author.username, f'https://cdn.discordapp.com/avatars/{data.author.id}/{data.author.avatar}.png')
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
    if guild.id not in self.cache:
        self.cache[guild.id] = Cache(guild, self.db, self.user_id, self.alias)


@onDispatch(Guild_Member)
async def guild_member_add(self, data):
    await self.db.influx.influxMember(data.guild_id, data.user.id, True, data.joined_at)


@onDispatch(Guild_Member_Remove)
async def guild_member_remove(self, data):
    await self.db.influx.influxMember(data.guild_id, data.user.id, False)


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
    if data.guild_id == 0 or data.user.bot or (len(data.client_status) == 1 and 'web' in data.client_status):
        return
    if self.cache[data.guild_id].trackPresence:
        #session = self.db.sql.session()
        #g = session.query(db.Games).filter(db.Games.UserID == data.user.id).filter(db.Games.Title == data.game.name).first()
        #if g == None:
        #    g = db.Games(data.user.id, data.game.name)
        #g.LastPlayed = data.game.created_at
        #session.commit()
        if data.user.id not in self.cache[data.guild_id].presence and data.game is not None and data.game.type == 0 and data.game.name is not None:
            self.cache[data.guild_id].presence[data.user.id] = (data.game.name, data.game.created_at)
            #print('new in cache')
        elif data.user.id in self.cache[data.guild_id].presence and data.game.name is None:
            s = self.cache[data.guild_id].presence.pop(data.user.id)
            #print('removing from cache')
            e = int(time.time()) - int(s[1]/1000)
            session = self.db.sql.session()
            g = session.query(db.Games).filter(db.Games.UserID == data.user.id).filter(db.Games.Title == s[0]).first()
            if g == None:
                g = db.Games(data.user.id, s[0], int(time.time()), e)
                self.db.sql.add(g)
            else:
                g.LastPlayed = int(time.time())
                #g.LastPlayed += e
                g.TotalPlayed += e
            session.commit()
            self.db.influx.commitPresence(data.guild_id, data.user.id, s[0], e)
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

from MFramework.utils.timers import *
@onDispatch(Voice_State)
async def voice_state_update(self, data):
    if data.member.user.bot: #or not self.cache[data.guild_id].trackVoice:
        return
    if data.channel_id in self.cache[data.guild_id].disabled_channels and not any(r in data.member.roles for r in self.cache[data.guild_id].disabled_roles):
        data.channel_id = 0

    if self.cache[data.guild_id].VoiceLink:
        r = self.cache[data.guild_id].VoiceLink
        if data.channel_id != 0 and r not in data.member.roles:
            await self.add_guild_member_role(data.guild_id, data.user_id, r, "Voice Role")
        elif data.channel_id == 0 and r in data.member.roles:
            await self.remove_guild_member_role(data.guild_id, data.user_id, r, "Voice Role")

    if self.cache[data.guild_id].trackVoice:
        v = self.cache[data.guild_id].voice
        if data.channel_id != 0: #User is on the Voice Channel
            for channel in v:
                if data.user_id in v[channel]: #User is in cached channel
                    if channel != data.channel_id: #Moved to another channel
                        print('Moved')
                        finalize(self, data.guild_id, channel, data.user_id)
                    else:  #Channel is same as before
                        if data.self_deaf:  #User is now muted
                            print('Muted')
                            restartTimer(self, data.guild_id, data.channel_id, data.user_id, -1)
                        elif not data.self_deaf and v[data.channel_id][data.user_id] == -1:  #User is not muted anymore
                            #log(f'User {data.user_id} is unmuted')
                            if len(v[data.channel_id]) > 1:
                                print('Unmuted')
                                startTimer(self, data.guild_id, data.channel_id, data.user_id) #Unmuted
                            else:
                                print('Unmuted, Alone')
                                restartTimer(self, data.guild_id, data.channel_id, data.user_id) #Unmuted Alone
                        return

            if data.channel_id not in v: #Init channel
                v[data.channel_id] = {}

            if len(v[data.channel_id]) >= 1 and data.user_id not in v[data.channel_id]:  #New person Joined channel
                if data.self_deaf:
                    print('Joined Muted')
                    restartTimer(self, data.guild_id, data.channel_id, data.user_id, -1) #Muted Joined
                else:
                    print('Joined')
                    startTimer(self, data.guild_id, data.channel_id, data.user_id) #Unmuted Joined
                for u in v[data.channel_id]:
                    if v[data.channel_id][u] == 0:  #There was someone on VC without Timer 
                        print('Alone is not alone anymore')
                        startTimer(self, data.guild_id, data.channel_id, u)

            elif len(v[data.channel_id]) == 0:  #Joined empty channel
                if data.self_deaf:
                    print('Joined Empty Muted')
                    restartTimer(self, data.guild_id, data.channel_id, data.user_id, -1) #Joined Empty Channel Muted
                else:
                    print('Joined Empty')
                    restartTimer(self, data.guild_id, data.channel_id, data.user_id) #Joined Empty Channel unmuted

            else: #Not a channel switch event
                print('???')

        else:  #User is not on Voice channel anymore
            for channel in v:
                if data.user_id in v[channel]:
                    print('Left')
                    finalize(self, data.guild_id, channel, data.user_id)
                    #if len(v[channel]) == 1: #Someone is now left alone
                    #    u = list(v[channel].keys())[0]
                    #    print('Alone')
                    #    restartTimer(self, data.guild_id, channel, u) #Alone on channel
                    return
