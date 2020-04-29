import random
class EndpointWrappers:
    async def sendMessage(self, channel, _content, _allowed_mentions={}, _tts=False):
        '''https://discordapp.com/developers/docs/resources/channel#allowed-mentions-object'''
        await self.create_message(channel_id=channel, content=_content, nonce=0, tts=_tts, file=None, embed=None, payload_json=None, allowed_mentions=_allowed_mentions, audit_reason='')
    async def sendEmbed(self, channel, _content, _embed, _allowed_mentions={}, _tts=False):
        await self.create_message(channel_id=channel, content=_content, nonce=0, tts=_tts, file=None, embed=_embed, payload_json=None, allowed_mentions=_allowed_mentions, audit_reason='')
    async def sendFile(self, channel, _content, _embed, attachment, filename='', _allowed_mentions={}, _tts=False):
        await self.create_message(channel_id=channel, content=_content, nonce=0, tts=_tts, file=(filename, attachment), embed=_embed, payload_json=None, allowed_mentions=_allowed_mentions, audit_reason='')
    async def message(self, channel, content):
        return await self.api_call(f"/channels/{channel}/messages", "POST", json={"content": content})
    async def embed(self, channel, content, embed):
        if 'color' not in embed:
            embed['color'] = random.randint(0,16777215)#self.color
        return await self.api_call(f"/channels/{channel}/messages", "POST", json={"content": content, "embed": embed})
    async def webhook(self, embeds, content="", webhook_url="", username="", avatar_url=""):
        return await self.api_call(
            f"/webhooks/{webhook_url}",
            "POST",
            json={"content": content, "embeds": embeds, "username": username, "avatar_url": avatar_url})
    async def withFile(self, channel, attachment, filename="", content="", embed=""):
        return await self.api_call(
            f"/channels/{channel}/messages",
            "POST",
            json={"content": content, "embed": embed},
            file=(filename, attachment))