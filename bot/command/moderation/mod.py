from bot.discord.commands import register

import bot.utils as utils
import asyncio

from bot.utils import Embed, created, parseMention, datetime, time


@register(group='Mod',category='Moderation',help='[user] [reason] - Warns user.')
async def warn(self, data):
    uid = data['mentions'][0]['id']
    reason = data['content'].split(' ',1)
    guild = await self.endpoints.get_guild(data['guild_id'])['name']
    cid = await self.endpoints.make_dm(uid)
    result = await self.endpoints.message(cid['id'], f"You've been warned in {guild} server for {reason[1]}")
    if 'code' in result:
        return await self.endpoints.message(data['channel_id'],f"Couldn't deliver Warning to user <@{uid}> due to: {result['message']}")
    return await self.endpoints.message(data['channel_id'],f"Delivered Warning to user <@{uid}> for: {reason[1]}")

@register(group='Mod',category='Moderation',help='[user] (time) [reason] - Mutes user.')
async def mute(self, data):
    uid = data['mentions'][0]['id']
    reason = data['content'].split(' ',1)
    guild = await self.endpoints.get_guild(data['guild_id'])['name']
    cid = await self.endpoints.make_dm(uid)
    result = await self.endpoints.message(cid['id'], f"You've been muted in {guild} for {reason[1]}")
    if 'code' in result:
        return await self.endpoints.message(data['channel_id'],f"Couldn't deliver mute reason to user <@{uid}> due to: {result['message']}")
    return await self.endpoints.message(data['channel_id'],f"Delivered mute reason to user <@{uid}> for: {reason[1]}")

@register(group='Mod',category='Moderation',help='[user] (time) [reason] - Bans user.')
async def ban(self, data):
    uid = utils.param(data['content'])[0]
    if data['mentions'] != []:
        uid=f"<@{uid}>"
    await self.endpoints.message(data['channel_id'],f"<:pege:644033864704196649> 🔨 {uid}")

@register(group='Mod',category='Moderation',help='[user] - Shows information about user.',)
async def userInfo(self, data):
    uid = parseMention(data['content'])
    member = await self.endpoints.get_member(data['guild_id'], uid)
    print(member)
    embed = Embed().setTitle(f"{member['user']['username']}#{member['user']['discriminator']}")
    embed.setFooter('',f"User ID: {member['user']['id']}")
    jdiscord = str(await created(member['user']['id']))
    embed.setTimestamp(jdiscord)
    avatar = member['user']['avatar']
    if avatar[0:2] == 'a_':
        avatar+='.gif'
    embed.setThumbnail(f"https://cdn.discordapp.com/avatars/{member['user']['id']}/{avatar}")
    roles=""
    for role in member['roles']:
        if roles != '':
            roles+=', '
        if (len(roles) + len(role)) <=1023:
            roles +=f"<@&{role}>"
    joined = str(time.strftime("%Y-%m-%d %H:%M:%S",datetime.datetime.fromisoformat(member['joined_at']).timetuple()))
    if member['premium_since'] != None:
        nitro = str(time.strftime("%Y-%m-%d %H:%M:%S",datetime.datetime.fromisoformat(member['premium_since']).timetuple()))
    else:
        nitro = member['premium_since']
    discord = str(time.strftime("%Y-%m-%d %H:%M:%S",datetime.datetime.fromisoformat(jdiscord).timetuple()))
    names = {
        "nick":("Nick",f"{member['nick']}",False),
        "roles":('Roles',f"{roles}",False),
        "premium_since":('Nitro',f"{nitro}",True),
        "joined_at":('Joined',f"**Discord:**\n{discord}\n**Server:**\n{joined}",True),
        "mute":('Voice',f"Guild Deaf: {member['deaf']}\nGuild Mute: {member['mute']}",True),
    }
    order = ['nick','joined_at','premium_since','deaf','roles']
    for key in order:
        if member[key] != None and member[key] != [] and member[key] != False and member[key] != 0 and key not in ['user']:
            res = names.get(key)
            if res != None:
                embed.addField(f"{res[0]}",f"{res[1]}", res[2])
    try:
        infractions = db.getInfractions(data['guild_id'],member['user']['id'])[0][0]
    except:
        infractions = None
    if infractions != None:
        embed.addField('Infractions',f"{infractions}",True)
    embed.setDescription(f"Requested by <@{data['author']['id']}> for user <@{member['user']['id']}>")
    await self.endpoints.embed(data['channel_id'],"",embed.embed)