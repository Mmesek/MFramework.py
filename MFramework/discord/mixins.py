import random
from ..utils.utils import get_main_color
class EndpointWrappers:
    async def sendMessage(self, channel, _content, _allowed_mentions={}, _tts=False):
        '''https://discordapp.com/developers/docs/resources/channel#allowed-mentions-object'''
        await self.create_message(channel_id=channel, content=_content, nonce=0, tts=_tts, file=None, embed=None, payload_json=None, allowed_mentions=_allowed_mentions, audit_reason='')
    async def sendEmbed(self, channel, _content, _embed, _allowed_mentions={}, _tts=False):
        await self.create_message(channel_id=channel, content=_content, nonce=0, tts=_tts, file=None, embed=_embed, payload_json=None, allowed_mentions=_allowed_mentions, audit_reason='')
    async def sendFile(self, channel, _content, _embed, attachment, filename='', _allowed_mentions={}, _tts=False):
        await self.create_message(channel_id=channel, content=_content, nonce=0, tts=_tts, file=(filename, attachment), embed=_embed, payload_json=None, allowed_mentions=_allowed_mentions, audit_reason='')
    async def message(self, channel, content, allowed_mentions={}):
        return await self.api_call(f"/channels/{channel}/messages", "POST", json={"content": content, "allowed_mentions":allowed_mentions})
    async def embed(self, channel, content, embed={}, allowed_mentions={}):
        if embed != {} and 'color' not in embed:
            try:
                if 'image' in embed:
                    img = embed['image']['url']
                elif 'thumbnail' in embed:
                    img = embed['thumbnail']['url']
                embed['color'] = get_main_color(img)
            except Exception as ex:
                embed['color'] = random.SystemRandom().randint(0,16777215)#self.color
        return await self.api_call(f"/channels/{channel}/messages", "POST", json={"content": content, "embed": embed, "allowed_mentions":allowed_mentions})
    async def webhook(self, embeds, content="", webhook_url="", username="", avatar_url="", allowed_mentions={}):
        return await self.api_call(
            f"/webhooks/{webhook_url}",
            "POST",
            json={"content": content, "embeds": embeds, "username": username, "avatar_url": avatar_url, "allowed_mentions":allowed_mentions})
    async def withFile(self, channel, attachment, filename="", content="", embed=""):
        return await self.api_call(
            f"/channels/{channel}/messages",
            "POST",
            json={"content": content, "embed": embed},
            file=(filename, attachment))
    async def move_guild_member(self, guild_id, user_id, channel_id, audit_reason='') -> None:
        return await self.api_call(f'/guilds/{guild_id}/members/{user_id}', 'PATCH', reason=audit_reason, json={'channel_id': channel_id})
