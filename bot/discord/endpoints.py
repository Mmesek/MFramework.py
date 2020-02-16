class Endpoints:
    def __init__(self, api_call):
        self.api_call = api_call

    async def message(self, channel, content):
        return await self.api_call(f"/channels/{channel}/messages", "POST", json={"content": content})

    async def edit(self, channel, message, content):
        return await self.api_call(f"/channels/{channel}/messages/{message}", "PATCH", json={"content": content})

    async def react(self, channel, message, emoji):
        return await self.api_call(f"/channels/{channel}/messages/{message}/reactions/{emoji}/@me", "PUT")

    # https://leovoel.github.io/embed-visualizer/
    async def embed(self, channel, content, embed):
        return await self.api_call(f"/channels/{channel}/messages", "POST", json={"content": content, "embed": embed})

    async def delete(self, channel, message, audit_reason=""):
        return await self.api_call(f"/channels/{channel}/messages/{message}", "DELETE", reason=audit_reason)

    async def trigger_typing(self, channel):
        return await self.api_call(f"/channels/{channel}/typing", "POST")

    async def role_add(self, guild, user, role, audit_reason=""):
        return await self.api_call(f"/guilds/{guild}/members/{user}/roles/{role}", "PUT", reason=audit_reason)

    async def role_remove(self, guild, user, role, audit_reason=""):
        return await self.api_call(f"/guilds/{guild}/members/{user}/roles/{role}", "DELETE", reason=audit_reason)

    async def role_update(self, guild, role, content, audit_reason=""):
        return await self.api_call(
            f"/guilds/{guild}/roles/{role}", "PATCH", json={"mentionable": content}, reason=audit_reason
        )

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

    async def kick_member(self, guild, user, audit_reason=""):
        return await self.api_call(f"/guilds/{guild}/members/{user}", "DELETE", reason=audit_reason)

    async def make_dm(self, user):
        return await self.api_call(f"/users/@me/channels", "POST", json={"recipient_id": user})

    async def modify_emoji(self, guild, emoji, name, roles, audit_reason=""):
        return await self.api_call(
            f"/guilds/{guild}/emojis/{emoji}", "PATCH", json={"name": name, "roles": roles}, reason=audit_reason,
        )

    async def get_messages(self, channel, message, limit=2, when="before"):
        """when = [before|around|after]"""
        return await self.api_call(f"/channels/{channel}/messages", "GET", params={"limit": limit, when: message})

    async def get_message(self, channel, message):
        return await self.api_call(f"/channels/{channel}/messages/{message}", "GET")

    async def modifychanneltopic(self, channel, topic, audit_reason=""):
        return await self.api_call(f"/channels/{channel}", "PATCH", json={"topic": topic}, reason=audit_reason)

    async def modifychannelname(self, channel, name, audit_reason=""):
        return await self.api_call(f"/channels/{channel}", "PATCH", json={"name": name}, reason=audit_reason)

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
        return await self.api_call(f"/channels/{channel}/messages/{message}/reactions/{emoji}/@me", "DELETE")

    async def delete_user_reaction(self, channel, message, emoji, user):
        return await self.api_call(f"/channels/{channel}/messages/{message}/reactions/{emoji}/{user}", "DELETE")

    async def changeNick(self, guild, nick):
        return await self.api_call(f"/guilds/{guild}/members/@me/nick", "PATCH", json={"nick": nick})

    async def create_webhook(self, channel, name, audit_reason=""):
        return await self.api_call(f"/channels/{channel}/webhooks", "POST", json={"name": name}, reason=audit_reason)

    async def webhook(self, embeds, content="", webhook_url="", username="", avatar_url=""):
        return await self.api_call(
            f"/webhooks/{webhook_url}",
            "POST",
            json={"content": content, "embeds": embeds, "username": username, "avatar_url": avatar_url},
        )

    async def withFile(self, channel, attachment, filename="", content="", embed=""):
        return await self.api_call(
            f"/channels/{channel}/messages",
            "POST",
            json={"content": content, "embed": embed},
            file=(filename, attachment),
        )

    async def ban_user(self, guild, user, reason="", delete_messages=0, audit_reason=""):
        return await self.api_call(
            f"/guilds/{guild}/bans/{user}",
            "PUT",
            params={"reason": reason, "delete-message-days": delete_messages},
            reason=audit_reason,
        )

    async def get_webhooks(self, channel):
        return await self.api_call(f"/channels/{channel}/webhooks", "GET")
