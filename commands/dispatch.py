from MFramework.discord.mbot import onDispatch
from MFramework.commands import execute, parse, compilePatterns, contextCommandList
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
        if (data.channel_id, data.author.id) in self.context[data.guild_id]:
            return await self.context[data.guild_id][(data.channel_id, data.author.id)].execute(data=data)
        elif (
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
            reg = re.findall(r"(?:(?=\*)(?<!\*).+?(?!\*\*)(?=\*))", data.content)
            if reg and set(reg) != {'*'}:
                if '*' in reg:
                    reg = set(reg)
                    reg.remove('*')
                    reg = list(reg)
                v = random.SystemRandom().randint(1, 6)
                #v = int(v / 100) + 1
                reactions = {
                    0:'0️⃣',
                    1:'1️⃣',2:'2️⃣',3:'3️⃣',
                    4:'4️⃣',5:'5️⃣',6:'6️⃣'
                }
                z = re.findall(r"(?i)zabij|wyryw|mord", reg[0])
                if z:
                    v = 0
                await self.create_reaction(data.channel_id, data.id, reactions.get(v))
        elif data.channel_id == 466643151470198786:
            embed = utils.Embed().setDescription(data.content)
            await self.webhook([embed.embed],'','569802933227618318/6AJW6rQjG0mlGvTFNZDfGiUqJCkd3EHDkAIDyJ7rwx-SA9uXP2xITwV9OGHg2YLwzgTS', data.author.username, f'https://cdn.discordapp.com/avatars/{data.author.id}/{data.author.avatar}.png')
        c = self.cache[data.guild_id].messages
        if (data.channel_id in c and (len(c[data.channel_id]) >= 1)) and (c[data.channel_id][list(c[data.channel_id].keys())[-1]].content == data.content) and (c[data.channel_id][list(c[data.channel_id].keys())[-1]].author.id == data.author.id):
            await self.delete_message(data.channel_id, data.id, 'Duplicate Message')
            return
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
                e = session.query(db.UserLevels).filter(db.UserLevels.GuildID == data.guild_id).filter(db.UserLevels.UserID == data.author.id).first()
                e.EXP += 1
                e.LastMessage = timestamp
                self.cache[data.guild_id].exp[data.author.id] = timestamp
                session.commit()
    elif data.author.bot is False and data.guild_id == 0:
        if 'dm' not in self.context:
            self.context['dm'] = {}
        cmd = data.content.split(' ')
        if (data.channel_id, data.author.id) in self.context['dm']:
            return await self.context['dm'][(data.channel_id, data.author.id)].execute(data=data)
        elif cmd[0].lower() in contextCommandList['dm']:
            self.context['dm'][(data.channel_id, data.author.id)] = contextCommandList['dm'].get(cmd[0].lower())(bot=self, data=data)
            await self.context['dm'][(data.channel_id, data.author.id)].execute(data=data)
        else:
            await log.DirectMessage(self, data)
            if data.channel_id not in self.cache["dm"]:
                self.cache["dm"][data.channel_id] = CacheDM()
            self.cache["dm"][data.channel_id].message(data)
    return


@onDispatch(Message)
async def message_update(self, data):
    if data.guild_id == 0:
        data.guild_id = 'dm'
    if (data.channel_id, data.author.id) in self.context[data.guild_id]:
        return await self.context[data.guild_id][(data.channel_id, data.author.id)].edit(data=data)
    elif data.guild_id == 0 or data.webhook_id != 0 or data.content == None or data.guild_id == 'dm':
        return
    #elif (data.channel_id, data.id) in self.cache[data.guild_id].commandMessages:
    #    c = self.cache[data.guild_id].commandMessages[(data.channel_id, data.id)]
    #    await execute(self, data)
    elif data.channel_id == 463437626515652618:
        m = await self.get_channel_message(data.channel_id, data.id)
        if not m.reactions:#data.reactions:
            reg = re.findall(r"(?:(?=\*)(?<!\*).+?(?!\*\*)(?=\*))", data.content)
            if reg and set(reg) != {'*'}:
                if '*' in reg:
                    reg = set(reg)
                    reg.remove('*')
                    reg = list(reg)
                v = random.SystemRandom().randint(1, 600)
                reactions = {
                    1:'1️⃣',2:'2️⃣',3:'3️⃣',
                    4:'4️⃣',5:'5️⃣',6:'6️⃣'
                }
                await self.create_reaction(data.channel_id, data.id, reactions.get(int(v / 100) + 1))
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
    if guild.id not in self.context:
        self.context[guild.id] = {}
    if len(self.cache[guild.id].members) < 10:
        await self.request_guild_members(guild.id)


@onDispatch(Guild_Member)
async def guild_member_add(self, data):
    await self.db.influx.influxMember(data.guild_id, data.user.id, True, data.joined_at)
    await log.UserJoinedGuild(self, data)
    if data.guild_id == 463433273620824104:
        print('New user joined guild! :D')
        dm = await self.create_dm(data.user.id)
        if dm:
            from .context.rpg import CreateCharacter
            self.context['dm'][(dm.id, data.user.id)] = CreateCharacter(bot=self, data=data, channel=dm)
            await self.context['dm'][(dm.id, data.user.id)].execute(data=dm)


@onDispatch(Guild_Member_Remove)
async def guild_member_remove(self, data):
    await self.db.influx.influxMember(data.guild_id, data.user.id, False)
    await log.UserLeftGuild(self, data)

@onDispatch(Guild_Member_Update)
async def guild_member_update(self, data):
    await log.MemberUpdate(self, data)
    is_boosting = await log.NitroChange(self, data)
    if is_boosting and data.guild_id == 289739584546275339:
        #TODO: Fetch from database channel/setting regarding nitro handling and message to send them
        nitro_channel = 589745007737700352
        greeting = [
        "Thank you for boosting the server, <@{user}>.", 
        "<@{user}> Thank you for boosting the server.",
        "<@{user}> Hello, thanks for boosting the server.",
        "<@{user}> Thanks for boosting."]

        color=[
        "As a booster, you can have your own custom role that you can choose the name and the color of.", 
        "As a booster you can have a role with your name and colour of choice.",
        "Alongside access to this channel, you can also get a custom role with any name (within ruleset) and any color.",
        "You can have a custom role as long as your boost persists."]

        fine_print = [
        "(As long as it doesn 't clash with Staff' s orange or Techland 's red.)",
        "(apart from Staff orange and Techland red)"]

        last = [
        "If you would like to have one, just contact one of the currently online staff.",
        "If that interests you, then just tell us what you'd like.",
        "If you would like to have one. Just write down the name and color, in hexadecimal if possible, in this channel.",
        "If you want one, just tell a staff member the name and color code you want for it."]
        from random import choice
        message = choice(greeting).format(user=data.user.id) + ' ' + choice(color) + ' ' + choice(fine_print) + ' '+ choice(last)
        await self.message(nitro_channel, message)
    await log.MutedChange(self, data)

@onDispatch(Guild_Members_Chunk)
async def guild_members_chunk(self, data):
    s = self.cache[data.guild_id]
    if type(s.joined) != list:
        s.joined = []
    for member in data.members:
        s.members[member.user.id] = member
        s.joined += [(member.user.id, member.joined_at, member.premium_since, member.roles)]


@onDispatch(Message_Delete)
async def message_delete(self, data):
    if data.guild_id == 0:
        return
    await log.MessageRemoved(self, data)
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
        if not data.member.user.bot and data.user_id != self.user_id:
            if (data.channel_id, data.user_id) in self.context['dm']:
                return await self.context['dm'][(data.channel_id, data.user_id)].react(data=data)
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
        if data.user.id in self.cache[data.guild_id].presence and (data.game.name is None or data.game.name != self.cache[data.guild_id].presence[data.user.id][0]):
            s = self.cache[data.guild_id].presence.pop(data.user.id)
            e = int(time.time()) - int(s[1]/1000)
            session = self.db.sql.session()
            g = session.query(db.Presences).filter(db.Presences.UserID == data.user.id).filter(db.Presences.Title == s[0]).first()
            if g == None:
                g = db.Presences(data.guild_id, data.user.id, s[0], int(time.time()), e, s[2], "Game")
                self.db.sql.add(g)
            else:
                g.LastPlayed = int(time.time())
                if s[2]:
                    g.AppID = s[2]
                g.TotalPlayed += e
            session.commit()
            self.db.influx.commitPresence(data.guild_id, data.user.id, s[0], e)
        if data.user.id not in self.cache[data.guild_id].presence and data.game is not None and data.game.type == 0 and data.game.name is not None:
            self.cache[data.guild_id].presence[data.user.id] = (data.game.name, data.game.created_at, data.game.application_id)
    if data.guild_id == 463433273620824104:
        if data.status == 'idle' and any(data.user.id in self.cache[data.guild_id].voice[channel] for channel in self.cache[data.guild_id].voice):
            await self.move_guild_member(data.guild_id, data.user.id, self.cache[data.guild_id].afk_channel, f"User {data.user.id} is AFK")
        elif data.status == 'online' and data.user.id in self.cache[data.guild_id].afk:
            await self.move_guild_member(data.guild_id, data.user.id, self.cache[data.guild_id].afk.pop(data.user.id), f"User {data.user.id} is no longer AFK")
    roles = self.cache[data.guild_id].presenceRoles
    if roles == None:
        return
    role = None
    for group in roles:
        for g in roles[group]:
            if data.game.type == 0 and data.game.name in roles[group].keys():
                role = roles[group][data.game.name]
                if role == None or any(i in role for i in data.roles):
                    return
                break
    if role is not None:
        for i in role:
            await self.add_guild_member_role(data.guild_id, data.user.id, i, "Presence Role")

from MFramework.utils.timers import *
@onDispatch(Voice_State)
async def voice_state_update(self, data):
    if data.member.user.bot:
        if data.user_id == self.user_id:
            self.cache[data.guild_id].connection.session_id = data.session_id
        return
    if data.channel_id in self.cache[data.guild_id].disabled_channels and not any(r in data.member.roles for r in self.cache[data.guild_id].disabled_roles):
        if data.channel_id == self.cache[data.guild_id].afk_channel:
            data.channel_id = -1
        else:
            data.channel_id = 0
    #if data.guild_id == 463433273620824104 and data.channel_id == 734523217141563463:
    #    if data.self_stream:
    #        await self.channel_name(734523870647681101, 'Wejście do Zakątka [NA ŻYWO]')
    #    else:
    #        stream = False
    #        v = self.cache[data.guild_id].voice
    #        if data.channel_id in v:
    #            for user in v[data.channel_id]:
    #                if v[data.channel_id][user].self_stream:
    #                    stream = True
    #            if stream:
    #                await self.channel_name(734523870647681101, 'Wejście do Zakątka')
    if self.cache[data.guild_id].dynamic_channels and data.channel_id in self.cache[data.guild_id].dynamic_channels:
        template = self.cache[data.guild_id].dynamic_channels[data.channel_id]
        if 'buffer' in template:
            await self.move_guild_member(data.guild_id, data.user_id, template['buffer'], f"Moved {data.member.user.username} to channel")
    #        if template['buffer'] not in self.cache[data.guild_id].voice:
    #            self.cache[data.guild_id].voice[template['buffer']] = {}
    #            await self.channel_name(data.channel_id, '🔴 Wejście do Zakątka')
    #        elif self.cache[data.guild_id].voice[template['buffer']] == {}:
    #            await self.channel_name(data.channel_id, '🔴 Wejście do Zakątka')
                #count = len(self.cache[data.guild_id].voice[template['buffer']])+1
    #        else:
    #            count = 1
    #        await self.user_limit(data.channel_id, count)
        else:
            count = len(self.cache[data.guild_id].dynamic_channels['channels'])+1
        
            new_channel = await self.create_guild_channel(data.guild_id, template['name']+f' #{count}', 2, None, template['bitrate'], template['user_limit'], None, template['position'], template['permission_overwrites'], template['parent_id'], False, "Generated Channel")
            await self.move_guild_member(data.guild_id, data.user_id, new_channel.id, f"Moved {data.member.user.username} to generated channel")
            data.channel_id = new_channel.id

            self.cache[data.guild_id].dynamic_channels['channels'] += [new_channel.id]

    if self.cache[data.guild_id].VoiceLink:
        r = self.cache[data.guild_id].VoiceLink
        if data.channel_id != 0 and r not in data.member.roles:
            await self.add_guild_member_role(data.guild_id, data.user_id, r, "Voice Role")
        elif data.channel_id == 0 and r in data.member.roles:
            await self.remove_guild_member_role(data.guild_id, data.user_id, r, "Voice Role")

    if self.cache[data.guild_id].trackVoice:
        v = self.cache[data.guild_id].voice
        moved = False
        if data.channel_id > 0: #User is on the Voice Channel
            for channel in v:
                if data.user_id in v[channel]: #User is in cached channel
                    if channel != data.channel_id: #Moved to another channel
                        print('Moved')
                        t = finalize(self, data.guild_id, channel, data.user_id)
                        if t[1][1] != 0:
                            _data = data
                            _data.user_id = t[1][0]
                            await log.UserVoiceChannel(self, _data, channel, int(t[1][1]))
                        t = t[0]
                        await log.UserVoiceChannel(self, data, channel, int(t))
                        moved = True
                        #if v[734523217141563463] == {}:
                        #    await self.channel_name(734523870647681101, 'Wejście do Zakątka')
                        if channel in self.cache[data.guild_id].dynamic_channels['channels'] and v[channel] == {}:
                            print('Removing channel')
                            await self.delete_close_channel(channel, "Deleting Empty Generated Channel")
                            self.cache[data.guild_id].dynamic_channels['channels'].remove(channel)
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
                if not moved:
                   await log.UserVoiceChannel(self, data)

            elif len(v[data.channel_id]) == 0:  #Joined empty channel
                if data.self_deaf:
                    print('Joined Empty Muted')
                    restartTimer(self, data.guild_id, data.channel_id, data.user_id, -1) #Joined Empty Channel Muted
                else:
                    print('Joined Empty')
                    restartTimer(self, data.guild_id, data.channel_id, data.user_id)  #Joined Empty Channel unmuted
                if not moved:
                    await log.UserVoiceChannel(self, data)

            else: #Not a channel switch event
                print('???')

        else:  #User is not on Voice channel anymore
            for channel in v:
                if data.user_id in v[channel]:
                    if data.channel_id == -1:
                        self.cache[data.guild_id].afk[data.user_id] = channel
                    print('Left')
                    t = finalize(self, data.guild_id, channel, data.user_id)
                    if t[1][1] != 0:
                        _data = data
                        _data.user_id = t[1][0]
                        await log.UserVoiceChannel(self, _data, channel, int(t[1][1]))
                    t = t[0]
                    await log.UserVoiceChannel(self, data, channel, int(t))
                    #if v[734523217141563463] == {}:
                    #    await self.channel_name(734523870647681101, 'Wejście do Zakątka')
                    if channel in self.cache[data.guild_id].dynamic_channels['channels'] and v[channel] == {}:
                        print('Removing channel')
                        await self.delete_close_channel(channel, "Deleting Empty Generated Channel")
                        self.cache[data.guild_id].dynamic_channels['channels'].remove(channel)
                        v.pop(channel)
                    return

@onDispatch(Voice_Server_Update)
async def voice_server_update(self, data):
    await self.cache[data.guild_id].connection.connect(data.token, data.guild_id, data.endpoint, self.user_id)


@onDispatch(Guild_Ban_Add)
async def guild_ban_add(self, data):
    reason = await self.get_guild_ban(data.guild_id, data.user.id)
    await log.InfractionEvent(self, data, "banned", reason=reason.reason)

@onDispatch(Guild_Ban_Remove)
async def guild_ban_remove(self, data):
    await log.InfractionEvent(self, data, "unbanned")