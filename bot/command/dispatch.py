import asyncio, json, datetime, time

from bot.utils import timed, quote
from bot.discord.mbot import onDispatch
from bot.discord.commands import execute

@onDispatch()
async def ready(self, data):
    self.session_id = data['session_id']
    self.user_id    = data['user']['id']
    print('Conntected as:', data['user']['username'])
@onDispatch()
async def resumed(self, data):
    pass

@onDispatch()
async def message_create(self, data):
    try:
#        print(data)
        if 'webhook_id' not in data and 'bot' not in data['author'] and 'guild_id' in data:
            if ('!' in data['content'] or self.user_id in data['content']) and await execute(self, data) != 0:
                return
            elif 'discordapp.com/channels/' in data['content']:
                pass
                return await quote(self, data)
            return
        #    await cache(data)
        #    database.AddExp(data['guild_id'],data['author']['id'],int(datetime.datetime.fromisoformat(data['timestamp']).timestamp()))
        elif 'bot' not in data['author'] and 'guild_id' not in data:
            embed = {'description':data['content'],'author':{"name":f"{data['author']['username']}#{data['author']['discriminator']}","icon_url":f"https://cdn.discordapp.com/avatars/{data['author']['id']}/{data['author']['avatar']}.png"},
            'footer':{f"{data['author']['id']} - {data['author']['username']}#{data['author']['discriminator']}"},'image':{},'attachments':[], "timestamp":data['timestamp'].split('+',1)[0]}
            try:
                embed['image']['url'] = f"{data['attachments'][0]['url']}"
                filename = data['attachments'][0]['filename']
            except:
                filename = ''
            #Change below embed with webhook from database
            webhook = ''
            return await self.endpoints.webhook(embed,f"<@{data['author']['id']}> {filename}", webhook)
        return
    except Exception as ex:
        print('Message Create Error: ', ex)
        print(data)
    return

@onDispatch()
async def presence_update(self, data):
    pass

@onDispatch()
async def message_update(self, data):
    if 'guild_id' not in data or 'webhook_id' in data or 'content' not in data:
        return
    c = self.cache.cachedMessage(data)
    embed = {"title":f"Message edited in <#{data['channel_id']}>\nBefore:","footer":{},"author":{},"fields":[]}
    if c != None:
        embed["description"]       =f"{c['content']}"
        embed['fields']           +=[{"name":"After:","value":f"{data['content'][:1023]}"}]
        if len(data['content']) > 1023:
            embed['fields']       +=[{"name":"\u200b","value":f"{data['content'][1023:]}"}]
        embed["timestamp"]         =c['timestamp']
        embed["footer"]["text"]    =f"ID: {c['author']['id']}"
        embed["author"]["icon_url"]=f"https://cdn.discordapp.com/avatars/{c['author']['id']}/{c['author']['avatar']}.png"
        embed["author"]["name"]    =f"{c['author']['username']}#{c['author']['discriminator']}"
        try:
            embed["fields"]    +=[{"name":"Attachments:","value":c['attachments'][0]['filename']}]
        except:
            pass
    self.cache.message(data)
    if 'description' in embed and (embed['description'] == "" or embed['description'] == data['content']):
        return
    webhook = self.cache.cache[data['guild_id']]['logging']['message_update']
    if webhook[0][0] == '':
        return
    return await self.endpoints.webhook(embed,'', webhook[0][0])

@onDispatch()
async def voice_server_update(self, data):
    pass
#        Voice = voice.VoiceConnection(data['token'], data['endpoint'], data['guild_id'])
#        await Voice.connection_manager()

@onDispatch()
async def voice_state_update(self, data):
    if data['channel_id'] != None:
        await self.cache.voice(data)
    else:
        t = int(await self.cache.cachedVoice(data)/60/10)
        print(t)
        #database.AddExp(data['guild_id'],data['user_id'],'','vexp',t,"joinedVC")

@onDispatch()
async def channel_create(self, data):
    pass

@onDispatch()
async def channel_update(self, data):
    pass

@onDispatch()
async def channel_delete(self, data):
    pass

@onDispatch()
async def channel_pins_update(self, data):
    pass

@onDispatch()
async def guild_create(self, data):
    print(data['id'],data['name'],data['owner_id'],data['joined_at'],data['large'],data['unavailable'],data['member_count'],data['voice_states'])
    print(data['members'][0],data['channels'][0],data['presences'][0])
#    self.db[data['id']].insert_one({})
    self.cache.server_data(data)
#    if database.checkGuild(data['id']) == []:
#        database.initGuild(data['id'])

@onDispatch()
async def guild_update(self, data):
    pass

@onDispatch()
async def guild_delete(self, data):
    pass

@onDispatch()
async def guild_ban_add(self, data):
    pass

@onDispatch()
async def guild_ban_remove(self, data):
    pass

@onDispatch()
async def guild_emojis_update(self, data):
    pass

@onDispatch()
async def guild_integrations_update(self, data):
    pass

@onDispatch()
async def guild_member_add(self, data):
    print(data)

@onDispatch()
async def guild_member_remove(self, data):
    print(data)

@onDispatch()
async def guild_member_update(self, data):
    pass

@onDispatch()
async def guild_member_chunk(self, data):
    pass

@onDispatch()
async def guild_role_create(self, data):
    pass

@onDispatch()
async def guild_role_update(self, data):
    pass

@onDispatch()
async def guild_role_delete(self, data):
    pass

@onDispatch()
async def message_delete(self, data):
    if 'guild_id' not in data or 'webhook_id' in data:
        return
    c = self.cache.cachedMessage(data)
    embed = {"title":f"Message deleted in <#{data['channel_id']}>","footer":{},"author":{},"fields":[]}
    if c != None:
        embed["description"]       =c['content']
        embed["timestamp"]         =c['timestamp']
        embed["footer"]["text"]    =f"ID: {c['author']['id']}"
        embed["author"]["icon_url"]=f"https://cdn.discordapp.com/avatars/{c['author']['id']}/{c['author']['avatar']}.png"
        embed["author"]["name"]    =f"{c['author']['username']}#{c['author']['discriminator']}"
        try:
            embed["fields"]    +=[{"name":"Attachments:","value":c['attachments'][0]['filename']}]
        except:
            pass
    webhook = self.cache.cache[data['guild_id']]['logging']['message_delete']
    if webhook[0][0] == '':
        return
    return await self.endpoints.webhook(embed,'', webhook[0][0])

@onDispatch()
async def message_delete_bulk(self, data):
    pass

@onDispatch()
async def message_reaction_add(self, data):
    role = self.cache.cache[data['guild_id']]['reactions'][data['message_id']][f"{data['emoji']['name']}:{data['emoji']['id']}"]
    if role == None:
        return
    return await self.endpoints.role_add(data['guild_id'],data['user_id'],role)

@onDispatch()
async def message_reaction_remove(self, data):
    role = self.cache.cache[data['guild_id']]['reactions'][data['message_id']][f"{data['emoji']['name']}:{data['emoji']['id']}"]
    if role == None:
        return
    return await self.endpoints.role_remove(data['guild_id'],data['user_id'],role)

@onDispatch()
async def message_reaction_remove_all(self, data):
    pass

@onDispatch()
async def presences_replace(self, data):
    pass

@onDispatch()
async def typing_start(self, data):
    pass

@onDispatch()
async def user_update(self, data):
    pass

@onDispatch()
async def webhooks_update(self, data):
    pass