import asyncio
class Endpoints:
    def __init__(self, api_call):
        self.api_call = api_call
    async def message(self, channel, content):
        return await self.api_call(f"/channels/{channel}/messages","POST",json={"content": content})
    async def edit(self, channel, message,content, sequence):
        return await self.api_call(f"/channels/{channel}/messages/{message}","PATCH",json={"content": content})
    async def react(self, channel, message, emoji):
        return await self.api_call(f"/channels/{channel}/messages/{message}/reactions/{emoji}/@me","PUT")
    async def embed(self, channel, content, embed): #https://leovoel.github.io/embed-visualizer/
        return await self.api_call(f"/channels/{channel}/messages","POST",json={"content": content, "embed": embed})
    async def delete(self, channel, message):
        return await self.api_call(f"/channels/{channel}/messages/{message}","DELETE")
    async def trigger_typing(self, channel):
        return await self.api_call(f"/channels/{channel}/typing","POST")
    async def role_add(self, guild, user, role):
        return await self.api_call(f"/guilds/{guild}/members/{user}/roles/{role}","PUT")
    async def role_remove(self, guild, user, role):
        return await self.api_call(f"/guilds/{guild}/members/{user}/roles/{role}","DELETE")
    async def role_update(self, guild,role,content):
        return await self.api_call(f"/guilds/{guild}/roles/{role}","PATCH",json={"mentionable": content})
    async def list_members(self, guild, after=0):
        return await self.api_call(f"/guilds/{guild}/members?limit=1000&after={after}")
    async def get_emoji(self, guild):
        return await self.api_call(f"/guilds/{guild}/emojis")
    async def get_invite(self, guild):
        return await self.api_call(f"/guilds/{guild}/invites")
    async def get_embed(self, guild):
        return await self.api_call(f"/guilds/{guild}/embed")
    async def get_prune(self, guild):
        return await self.api_call(f"/guilds/{guild}/prune")
    async def kick_member(self, guild,user):
        return await self.api_call(f"/guilds/{guild}/members/{user}","DELETE",json={"reason":"Protokół Czystka."})
    async def make_dm(self,user):
        return await self.api_call(f"/users/@me/channels","POST",json={"recipient_id": user})
    async def modify_emoji(self, guild,emoji,name,roles):
        return await self.api_call(f"/guilds/{guild}/emojis/{emoji}","PATCH",json={"name":name,"roles":roles})
    async def get_messages(self, channel,after, limit=50):
        return await self.api_call(f"/channels/{channel}/messages","GET",params={'limit':2,'before':after})
    async def get_message(self, channel, message):
        return await self.api_call(f"/channels/{channel}/messages/{message}","GET")
    async def modifychanneltopic(self, channel, topic):
        return await self.api_call(f"/channels/{channel}","PATCH",json={"topic":topic})
    async def modifychannelname(self, channel, name):
        return await self.api_call(f"/channels/{channel}","PATCH",json={"name":name})
    async def get_guild(self, guild):
        return await self.api_call(f"/guilds/{guild}")
    async def get_guild_integrations(self, guild):
        return await self.api_call(f"/guilds/{guild}/integrations")
    async def get_user(self, user):
        return await self.api_call(f"/users/{user}")
    async def get_member(self, guild, user):
        return await self.api_call(f"/guilds/{guild}/members/{user}")
    async def get_roles(self, guild):
        return await self.api_call(f"/guilds/{guild}/roles")
    async def delete_own_reaction(self, channel, message, emoji):
        return await self.api_call(f"/channels/{channel}/messages/{message}/reactions/{emoji}/@me","DELETE")
    async def changeNick(self, guild, nick):
        return await self.api_call(f"/guilds/{guild}/members/@me/nick","PATCH",json={"nick": nick})
    async def create_webhook(self, channel, name):
        return await self.api_call(f"/channels/{channel}/webhooks","POST",json={"name":name})
    async def webhook(self, embeds, content='', webhook_url='641434571384160278/9W5TsFUrLRi0ULfvgkoviWl5t3SWtqZQO7R4fC5FVsERYj0msopjTELOsFmk1-F8Bg3z', username='', avatar_url=''):
        return await self.api_call(f"/webhooks/{webhook_url}","POST",json={"content":content,"embeds":embeds,"username":username,"avatar_url":avatar_url})
    async def withFile(self, channel, attachment, filename='', content='', embed=''):
        return await self.api_call(f"/channels/{channel}/messages","POST",json={"content":content,"embed":embed},file=(filename,attachment))
