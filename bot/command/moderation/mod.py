from bot.discord.commands import register

import bot.utils as utils
import asyncio

from bot.utils import Embed, created, parseMention, datetime, time

from PIL import Image
from io import BytesIO

async def handleInfraction(self,data,infraction):
    params = data['content'].split(' ',1)
    uid = params[0]
    reason = params[1]
    if infraction[0] == 'Warn':
        duration = 0
    else:
        duration = 0 #There is some need of handling it tho.
    await self.db.insert('Infractions','GuildID,UserID,Timestamp,Reason,ModeratorID,Duration,InfractionType',[data['guild_id'],uid,data['timestamp'],reason,data['author']['id'],duration,infraction[0]])
    guild = await self.endpoints.get_guild(data['guild_id'])
    guild= guild['name']
    cid = await self.endpoints.make_dm(uid)
    result = await self.endpoints.message(cid['id'], f"You've been {infraction[1]} in {guild} server for {reason}")
    if 'code' in result:
        await self.endpoints.message(data['channel_id'],f"Couldn't deliver {infraction[2]} to user <@{uid}> due to: {result['message']}")
    else:
        await self.endpoints.message(data['channel_id'],f"Delivered {infraction[2]} to user <@{uid}> for: {reason}")
    if uid == '273499695186444289':
        await self.endpoints.message(data['channel_id'],'No.')
        return
    if infraction[0] in {'Mute','Kick','Ban'}:
        delete = 0
        g = self.cache.cachedRoles(data['guild_id'],data['mentions'][0]['member']['roles'])
        if g not in {'Global','Vip','Nitro'}:
            await self.endpoints.message(data['channel_id'],f"{infraction[1].capitalize()} 🔨... Can not ban <@{uid}> because CAN NOT BAN MODERATOR OR ADMINISTRATOR REEEEEEE")
        else:
            if infraction[0] == 'Mute':
                try:
                    role = self.cache.cache[data['guild_id']]['groups']['Muted'][0]
                    r = await self.endpoints.role_add(data['guild_id'],uid, role, f"Requested by {data['author']['username']}")
                except:
                    await self.endpoints.message(data['channel_id'],f"Couldn't perform operation. Muted role or permission is missing.")
            elif infraction[0] == 'Kick':
                r = await self.endpoints.kick_user(data['guild_id'],uid,reason,f"Requested by {data['author']['username']}")
            elif infraction[0] == 'Ban':
                r = await self.endpoints.ban_user(data['guild_id'],uid,reason,delete,f"Requested by {data['author']['username']}")
            if 'code' in r:
                await self.endpoints.message(data['channel_id'],f"Couldn't perform operation. Missing Permission. (Attempted action: {infraction[0]})")
            else:
                await self.endpoints.message(data['channel_id'],f"{infraction[1].capitalize()} 🔨 <@{uid}> for {reason}")

@register(group='Mod',category='Moderation',help='[user] [reason] - Warns user.')
async def warn(self, data):
    await handleInfraction(self, data, ["Warn","warned","Warning"])

@register(group='Mod',category='Moderation',help='[user] (time) [reason] - Mutes user.')
async def mute(self, data):
    await handleInfraction(self, data, ["Mute","muted","mute reason"])

@register(group='Mod',category='Moderation',help='[user] [reason] - Kicks user.')
async def kick(self, data):
    await handleInfraction(self, data, ["Kick","kicked","kick reason"])

@register(group='Mod',category='Moderation',help='[user] (time) [reason] - Bans user.')
async def ban(self, data):
    await handleInfraction(self, data, ["Ban","banned","ban reason"])



@register(group='Mod',category='Moderation',help='[user] - Shows Infractions of user.')
async def infractions(self, data):
    uids = data['content'].split('!',1)[0].split(' ')
    if uids == ['']:
        uids = [data['author']['id']]
    for uid in uids:
        member = await self.endpoints.get_member(data['guild_id'], uid)
        avatar = member['user']['avatar']        
        embed=Embed().setAuthor(f"{member['user']['username']}#{member['user']['discriminator']}",'',f"https://cdn.discordapp.com/avatars/{member['user']['id']}/{avatar}")
        joined = str(time.strftime("%Y-%m-%d %H:%M:%S",datetime.datetime.fromisoformat(member['joined_at']).timetuple()))
        embed.setTimestamp(joined).setTitle("Infractions")
        embed.setFooter('',f"User ID: {member['user']['id']}. Joined Server ")
        infractions = await self.db.selectMultiple('Infractions','Timestamp,Reason,ModeratorID,Duration,InfractionType','WHERE GuildID=? AND UserID=?',[data['guild_id'],member['user']['id']])
        infractions = reversed(infractions)
        if infractions != []:
            w,m,b = 0,0,0
            inf_total = ''
            for i in infractions:
                if i[4] == 'Warn':
                    w+=1
                elif i[4] == 'Mute':
                    m+=1
                elif i[4] == 'Ban':
                    b+=1                    
                f = f"[{i[0][0:16].replace('T',' ')}] [{i[4]}] **{i[1]}** by <@{i[2]}>\n"
                if len(inf_total+f) < 2048:
                    inf_total += f
            infractions = inf_total
            total = f'Warns: [{w}]\nMutes: [{m}]\nBans: [{b}]'
            embed.setDescription(f"{infractions}").addField('Total Infractions',total,True)    
    await self.endpoints.embed(data['channel_id'],"",embed.embed)

@register(group='Mod',category='Moderation',help='[user] - Shows information about user.')
async def userInfo(self, data):
    uids = data['content'].split('!',1)[0].split(' ')
    if uids == ['']:
        uids = [data['author']['id']]
    for uid in uids:
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
        infractions = await self.db.selectMultiple('Infractions','Timestamp,Reason,ModeratorID,Duration,InfractionType','WHERE GuildID=? AND UserID=?',[data['guild_id'],member['user']['id']])
        if infractions != []:
            infractions = reversed(infractions)
            w,m,b = 0,0,0
            inf_total = ''
            for i in infractions:
                if i[4] == 'Warn':
                    w+=1
                elif i[4] == 'Mute':
                    m+=1
                elif i[4] == 'Ban':
                    b+=1                    
                f = f"[{i[0][0:16].replace('T',' ')}] [{i[4]}] **{i[1]}** by <@{i[2]}>\n"
                if len(inf_total+f) < 1024:
                    inf_total += f
            infractions = inf_total
            total = f'Warns: [{w}]\nMutes: [{m}]\nBans: [{b}]'
            embed.addField('Infractions',f"{infractions}").addField('Total Infractions',total,True)
        embed.setDescription(f"Requested by <@{data['author']['id']}> for user <@{member['user']['id']}>")
        await self.endpoints.embed(data['channel_id'],"",embed.embed)

@register(group='Mod',category='Moderation',help='- Shows information about server.')
async def serverInfo(self, data):
    server = await self.endpoints.get_guild(data['guild_id'])
    icon = server['icon']
    if icon[0:2] == 'a_':
       icon+=".gif"
    else:
       icon+=".png"
    features = ''
    for feature in server['features']:
       if features != '':
           features+=", "
       features += feature.lower().capitalize().replace('_',' ')
    names = {
        "owner_id":("Owner",f"<@{server['owner_id']}>",False),
        "features":("VIP Perks",f"{features}",False),
        "region":("Region",f"Voice: {server['region']}\nLanguage: {server['preferred_locale']}",True),
        "afk_channel_id":("AFK",f"Timeout: {server['afk_timeout']/60}minutes\nChannel: <#{server['afk_channel_id']}>",True),
        "default_message_notifications":("Message Notifications",f"{server['default_message_notifications']}",True),
        "roles":("Roles",f"{len(server['roles'])}",True),
        "emojis":("Emojis",f"{len(server['emojis'])}",True),
        "premium_subscription_count":("Boost",f"Tier: {server['premium_tier']}\nBoosters: {server['premium_subscription_count']}",True),
        "verification_level":("Verification Level",f"{server['verification_level']}",True),
        "vanity_url_code":("Vanity URL",f"gg/[{server['vanity_url_code']}](http://discord.gg/{server['vanity_url_code']})",True),
        "mfa_level":("MFA Level",f"{server['mfa_level']}",True),
        "explicit_content_filter":("Content Filter",f"{server['explicit_content_filter']}",True),
        "embed_enabled":("Embed",f"Enabled: {server['embed_enabled']}\nChannel: <#{server['embed_channel_id']}>",True),
        "widget_enabled":("Widget",f"Enabled: {server['widget_enabled']}\nChannel: <#{server['widget_channel_id']}>",True),
        "system_channel_id":("System",f"Channel: <#{server['system_channel_id']}>\nFlags: {server['system_channel_flags']}",True),
        "application_id":("Application ID",f"{server['application_id']}")
    }
    order = ['owner_id','features','region','afk_channel_id','premium_subscription_count','embed_enabled','widget_enabled','system_channel_id','vanity_url_code','roles','emojis','verification_level','mfa_level','explicit_content_filter','default_message_notifications']
    embed = Embed().setTitle(server['name']).setTimestamp(str(await created(server['id']))).setFooter('',f"Server ID: {server['id']}").setThumbnail(f"https://cdn.discordapp.com/icons/{server['id']}/{icon}").setImage(f"https://cdn.discordapp.com/splashes/{server['id']}/{server['splash']}")
    if server['description'] != None:
        embed.setDescription(server['description'])
    for key in order:
        if server[key] != None and server[key] != [] and server[key] != False and server[key] != 0 and key not in ['icon', 'name','id', 'splash','banner','max_members']:
            res = names.get(key)
            if res != None:
                embed.addField(f"{res[0]}",f"{res[1]}", res[2])
    await self.endpoints.embed(data['channel_id'],'',embed.embed)

@register(group='Mod',category='Moderation',help='[role] - Shows information about role.')
async def roleInfo(self, data):
    rid = data['content'].split('!',1)[0].split(' ')
    if rid == ['']:
        rid = [data['member']['roles'][0]]
    roles = await self.endpoints.get_roles(data['guild_id'])
    for r in rid:        
        for role in roles:
            if role['id'] == r:
                color = str(hex(role['color'])).replace('0x','#')
                img = Image.new('RGB',(100,100),color)
                embed = Embed()
                embed.setColor(role['color']).setTitle(role['name']).setFooter('',f"Role ID: {role['id']}")
                embed.setTimestamp(str(await created(role['id'])))
                embed.addField('Position', role['position'],True).addField("Displayed separately",role['hoist'],True)
                embed.addField("Color",color,True).addField("Mentionable",role['mentionable'],True)
                embed.addField("Integration",role['managed'],True).addField("Permissions",role['permissions'],True)
                embed.addField("Created",str(time.strftime("%Y-%m-%d %H:%M:%S",datetime.datetime.fromisoformat(str(await created(role['id']))).timetuple())),True)
                embed.setThumbnail('attachment://color.png')
                buffered = BytesIO()
                img.save(buffered, format="PNG")
                img_str = buffered.getvalue()
                await self.endpoints.withFile(data['channel_id'],img_str,'color.png','',embed.embed)