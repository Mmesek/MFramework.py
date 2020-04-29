# Generated file from docs at 02:12 2020/04/07.
from .objects import *

class Endpoints:
    async def get_guild_audit_log(self, guild_id, audit_reason='') -> Audit_Log:
        """Returns an [audit log](https://discordapp.com/developers/docs/resources/audit_log#audit-log-object) object for the guild.
        Requires the 'VIEW_AUDIT_LOG' permission."""
        r = await self.api_call(f'/guilds/{guild_id}/audit-logs', 'GET', reason=audit_reason)
        return Audit_Log(r)

    async def get_channel(self, channel_id, audit_reason='') -> Channel:
        """Get a channel by ID.
        Returns a [channel](https://discordapp.com/developers/docs/resources/channel#channel-object) object."""
        r = await self.api_call(f'/channels/{channel_id}', 'GET', reason=audit_reason)
        return Channel(r)

    async def modify_channel(self, channel_id, name, type, position, topic, nsfw, rate_limit_per_user, bitrate, user_limit, permission_overwrites, parent_id, audit_reason='') -> dict:
        """Update a channel's settings.
        Requires the `MANAGE_CHANNELS` permission for the guild.
        Returns a [channel](https://discordapp.com/developers/docs/resources/channel#channel-object) on success, and a 400 BAD REQUEST on invalid parameters.
        Fires a [Channel Update](https://discordapp.com/developers/docs/topics/gateway#channel-update) Gateway event.
        If modifying a category, individual [Channel Update](https://discordapp.com/developers/docs/topics/gateway#channel-update) events will fire for each child channel that also changes.
        All JSON parameters are optional."""
        return await self.api_call(f'/channels/{channel_id}', 'PATCH', reason=audit_reason, json={'name':name,'type':type,'position':position,'topic':topic,'nsfw':nsfw,'rate_limit_per_user':rate_limit_per_user,'bitrate':bitrate,'user_limit':user_limit,'permission_overwrites':permission_overwrites,'parent_id':parent_id,})

    async def delete_close_channel(self, channel_id, audit_reason='') -> Channel:
        """Delete a channel, or close a private message.
        Requires the `MANAGE_CHANNELS` permission for the guild.
        Deleting a category does not delete its child channels; they will have their `parent_id` removed and a [Channel Update](https://discordapp.com/developers/docs/topics/gateway#channel-update) Gateway event will fire for each of them.
        Returns a [channel](https://discordapp.com/developers/docs/resources/channel#channel-object) object on success.
        Fires a [Channel Delete](https://discordapp.com/developers/docs/topics/gateway#channel-delete) Gateway event.
        > warn
        > Deleting a guild channel cannot be undone.
        Use this with caution, as it is impossible to undo this action when performed on a guild channel.
        In contrast, when used with a private message, it is possible to undo the action by opening a private message with the recipient again.
        > info
        > For Public servers, the set Rules or Guidelines channel and the Moderators-only (Public Server Updates) channel cannot be deleted."""
        r = await self.api_call(f'/channels/{channel_id}', 'DELETE', reason=audit_reason)
        return Channel(r)

    async def get_channel_messages(self, channel_id, around, before, after, limit, audit_reason='') -> Message:
        """Returns the messages for a channel.
        If operating on a guild channel, this endpoint requires the `VIEW_CHANNEL` permission to be present on the current user.
        If the current user is missing the 'READ_MESSAGE_HISTORY' permission in the channel then this will return no messages (since they cannot read the message history).
        Returns an array of [message](https://discordapp.com/developers/docs/resources/channel#message-object) objects on success.
        > info
        > The before, after, and around keys are mutually exclusive, only one may be passed at a time."""
        r = await self.api_call(f'/channels/{channel_id}/messages', 'GET', reason=audit_reason, params={'around':around,'before':before,'after':after,'limit':limit,})
        return Message(r)

    async def get_channel_message(self, channel_id, message_id, audit_reason='') -> Message:
        """Returns a specific message in the channel.
        If operating on a guild channel, this endpoint requires the 'READ_MESSAGE_HISTORY' permission to be present on the current user.
        Returns a [message](https://discordapp.com/developers/docs/resources/channel#message-object) object on success."""
        r = await self.api_call(f'/channels/{channel_id}/messages/{message_id}', 'GET', reason=audit_reason)
        return Message(r)

    async def create_message(self, channel_id, content, nonce, tts, file, embed, payload_json, allowed_mentions, audit_reason='') -> Message:
        """
        > warn
        > Before using this endpoint, you must connect to and identify with a [gateway](https://discordapp.com/developers/docs/topics/gateway#gateways) at least once.
        > warn
        > Discord may strip certain characters from message content, like invalid unicode characters or characters which cause unexpected message formatting.
        If you are passing user-generated strings into message content, consider sanitizing the data to prevent unexpected behavior and utilizing `allowed_mentions` to prevent unexpected mentions.Post a message to a guild text or DM channel.
        If operating on a guild channel, this endpoint requires the `SEND_MESSAGES` permission to be present on the current user.
        If the `tts` field is set to `true`, the `SEND_TTS_MESSAGES` permission is required for the message to be spoken.
        Returns a [message](https://discordapp.com/developers/docs/resources/channel#message-object) object.
        Fires a [Message Create](https://discordapp.com/developers/docs/topics/gateway#message-create) Gateway event.
        See [message formatting](https://discordapp.com/developers/docs/reference#message-formatting) for more information on how to properly format messages.The maximum request size when sending a message is 8MB.This endpoint supports requests with `Content-Type`s of both `application/json` and `multipart/form-data`.
        You must however use `multipart/form-data` when uploading files.
        Note that when sending `multipart/form-data` requests the `embed` field cannot be used, however you can pass a JSON encoded body as form value for `payload_json`, where additional request parameters such as `embed` can be set.
        > info
        > Note that when sending `application/json` you must send at least one of `content` or `embed`, and when sending `multipart/form-data`, you must send at least one of `content`, `embed` or `file`.
        For a `file` attachment, the `Content-Disposition` subpart header MUST contain a `filename` parameter."""
        r = await self.api_call(f'/channels/{channel_id}/messages', 'POST', reason=audit_reason, params={'content':content,'nonce':nonce,'tts':tts,'file':file,'embed':embed,'payload_json':payload_json,'allowed_mentions':allowed_mentions,})
        return Message(r)

    async def create_reaction(self, channel_id, message_id, emoji, audit_reason='') -> None:
        """Create a reaction for the message.
        This endpoint requires the 'READ_MESSAGE_HISTORY' permission to be present on the current user.
        Additionally, if nobody else has reacted to the message using this emoji, this endpoint requires the 'ADD_REACTIONS' permission to be present on the current user.
        Returns a 204 empty response on success.The `emoji` must be [URL Encoded](https://en.wikipedia.org/wiki/Percent-encoding) or the request will fail with `10014: Unknown Emoji`."""
        return await self.api_call(f'/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me', 'PUT', reason=audit_reason)

    async def delete_own_reaction(self, channel_id, message_id, emoji, audit_reason='') -> None:
        """Delete a reaction the current user has made for the message.
        Returns a 204 empty response on success.The `emoji` must be [URL Encoded](https://en.wikipedia.org/wiki/Percent-encoding) or the request will fail with `10014: Unknown Emoji`."""
        return await self.api_call(f'/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me', 'DELETE', reason=audit_reason)

    async def delete_user_reaction(self, channel_id, message_id, emoji, user_id, audit_reason='') -> None:
        """Deletes another user's reaction.
        This endpoint requires the 'MANAGE_MESSAGES' permission to be present on the current user.
        Returns a 204 empty response on success.The `emoji` must be [URL Encoded](https://en.wikipedia.org/wiki/Percent-encoding) or the request will fail with `10014: Unknown Emoji`."""
        return await self.api_call(f'/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/{user_id}', 'DELETE', reason=audit_reason)

    async def get_reactions(self, channel_id, message_id, emoji, before, after, limit, audit_reason='') -> User:
        """Get a list of users that reacted with this emoji.
        Returns an array of [user](https://discordapp.com/developers/docs/resources/user#user-object) objects on success.The `emoji` must be [URL Encoded](https://en.wikipedia.org/wiki/Percent-encoding) or the request will fail with `10014: Unknown Emoji`."""
        r = await self.api_call(f'/channels/{channel_id}/messages/{message_id}/reactions/{emoji}', 'GET', reason=audit_reason, params={'before':before,'after':after,'limit':limit,})
        return User(r)

    async def delete_all_reactions(self, channel_id, message_id, audit_reason=''):
        """Deletes all reactions on a message.
        This endpoint requires the 'MANAGE_MESSAGES' permission to be present on the current user.
        Fires a [Message Reaction Remove All](https://discordapp.com/developers/docs/topics/gateway#message-reaction-remove-all) Gateway event."""
        return await self.api_call(f'/channels/{channel_id}/messages/{message_id}/reactions', 'DELETE', reason=audit_reason)

    async def delete_all_reactions_for_emoji(self, channel_id, message_id, emoji, audit_reason=''):
        """Deletes all the reactions for a given emoji on a message.
        This endpoint requires the `MANAGE_MESSAGES` permission to be present on the current user.
        Fires a [Message Reaction Remove Emoji](https://discordapp.com/developers/docs/topics/gateway#message-reaction-remove-emoji) Gateway event.The `emoji` must be [URL Encoded](https://en.wikipedia.org/wiki/Percent-encoding) or the request will fail with `10014: Unknown Emoji`."""
        return await self.api_call(f'/channels/{channel_id}/messages/{message_id}/reactions/{emoji}', 'DELETE', reason=audit_reason)

    async def edit_message(self, channel_id, message_id, content=None, embed=None, flags=None, audit_reason='') -> Message:
        """Edit a previously sent message.
        The fields `content`, `embed`, and `flags` can be edited by the original message author.
        Other users can only edit `flags` and only if they have the `MANAGE_MESSAGES` permission in the corresponding channel.
        When specifying flags, ensure to include all previously set flags/bits in addition to ones that you are modifying.
        Only `flags` documented in the table below may be modified by users (unsupported flag changes are currently ignored without error).Returns a [message](https://discordapp.com/developers/docs/resources/channel#message-object) object.
        Fires a [Message Update](https://discordapp.com/developers/docs/topics/gateway#message-update) Gateway event.
        > info
        > All parameters to this endpoint are optional."""
        r = await self.api_call(f'/channels/{channel_id}/messages/{message_id}', 'PATCH', reason=audit_reason, json={'content':content,'embed':embed,'flags':flags,})
        return Message(r)

    async def delete_message(self, channel_id, message_id, audit_reason='') -> None:
        """Delete a message.
        If operating on a guild channel and trying to delete a message that was not sent by the current user, this endpoint requires the `MANAGE_MESSAGES` permission.
        Returns a 204 empty response on success.
        Fires a [Message Delete](https://discordapp.com/developers/docs/topics/gateway#message-delete) Gateway event."""
        return await self.api_call(f'/channels/{channel_id}/messages/{message_id}', 'DELETE', reason=audit_reason)

    async def bulk_delete_messages(self, channel_id, messages, audit_reason='') -> None:
        """Delete multiple messages in a single request.
        This endpoint can only be used on guild channels and requires the `MANAGE_MESSAGES` permission.
        Returns a 204 empty response on success.
        Fires a [Message Delete Bulk](https://discordapp.com/developers/docs/topics/gateway#message-delete-bulk) Gateway event.Any message IDs given that do not exist or are invalid will count towards the minimum and maximum message count (currently 2 and 100 respectively).
        > warn
        > This endpoint will not delete messages older than 2 weeks, and will fail with a 400 BAD REQUEST if any message provided is older than that or if any duplicate message IDs are provided."""
        return await self.api_call(f'/channels/{channel_id}/messages/bulk-delete', 'POST', reason=audit_reason, json={'messages':messages,})

    async def bulk_delete_messages_deprecated(self, channel_id, audit_reason=''):
        """Same as above, but this endpoint is deprecated."""
        return await self.api_call(f'/channels/{channel_id}/messages/bulk_delete', 'POST', reason=audit_reason)

    async def edit_channel_permissions(self, channel_id, overwrite_id, allow, deny, type, audit_reason='') -> None:
        """Edit the channel permission overwrites for a user or role in a channel.
        Only usable for guild channels.
        Requires the `MANAGE_ROLES` permission.
        Returns a 204 empty response on success.
        For more information about permissions, see [permissions](https://discordapp.com/developers/docs/topics/permissions#permissions)."""
        return await self.api_call(f'/channels/{channel_id}/permissions/{overwrite_id}', 'PUT', reason=audit_reason, json={'allow':allow,'deny':deny,'type':type,})

    async def get_channel_invites(self, channel_id, audit_reason='') -> Invite:
        """Returns a list of [invite](https://discordapp.com/developers/docs/resources/invite#invite-object) objects (with [invite metadata](https://discordapp.com/developers/docs/resources/invite#invite-metadata-object)) for the channel.
        Only usable for guild channels.
        Requires the `MANAGE_CHANNELS` permission."""
        r = await self.api_call(f'/channels/{channel_id}/invites', 'GET', reason=audit_reason)
        return [Invite(i) if type(i) is dict else int(i or 0) if type(i) is int or i.isdigit() else [] for i in r]

    async def create_channel_invite(self, channel_id, max_age, max_uses, temporary, unique, target_user=None, target_user_type=None, audit_reason='') -> Invite:
        """Create a new [invite](https://discordapp.com/developers/docs/resources/invite#invite-object) object for the channel.
        Only usable for guild channels.
        Requires the `CREATE_INSTANT_INVITE` permission.
        All JSON parameters for this route are optional, however the request body is not.
        If you are not sending any fields, you still have to send an empty JSON object (`{}`).
        Returns an [invite](https://discordapp.com/developers/docs/resources/invite#invite-object) object.
        Fires a [Invite Create](https://discordapp.com/developers/docs/topics/gateway#invite-create) Gateway event."""
        r = await self.api_call(f'/channels/{channel_id}/invites', 'POST', reason=audit_reason, json={'max_age':max_age,'max_uses':max_uses,'temporary':temporary,'unique':unique,'target_user':target_user,'target_user_type':target_user_type,})
        return Invite(r)

    async def delete_channel_permission(self, channel_id, overwrite_id, audit_reason='') -> None:
        """Delete a channel permission overwrite for a user or role in a channel.
        Only usable for guild channels.
        Requires the `MANAGE_ROLES` permission.
        Returns a 204 empty response on success.
        For more information about permissions, see [permissions](https://discordapp.com/developers/docs/topics/permissions#permissions)"""
        return await self.api_call(f'/channels/{channel_id}/permissions/{overwrite_id}', 'DELETE', reason=audit_reason)

    async def trigger_typing_indicator(self, channel_id, audit_reason='') -> None:
        """Post a typing indicator for the specified channel.
        Generally bots should **not** implement this route.
        However, if a bot is responding to a command and expects the computation to take a few seconds, this endpoint may be called to let the user know that the bot is processing their message.
        Returns a 204 empty response on success.
        Fires a [Typing Start](https://discordapp.com/developers/docs/topics/gateway#typing-start) Gateway event."""
        return await self.api_call(f'/channels/{channel_id}/typing', 'POST', reason=audit_reason)

    async def get_pinned_messages(self, channel_id, audit_reason='') -> Message:
        """Returns all pinned messages in the channel as an array of [message](https://discordapp.com/developers/docs/resources/channel#message-object) objects."""
        r = await self.api_call(f'/channels/{channel_id}/pins', 'GET', reason=audit_reason)
        return Message(r)

    async def add_pinned_channel_message(self, channel_id, message_id, audit_reason='') -> None:
        """Pin a message in a channel.
        Requires the `MANAGE_MESSAGES` permission.
        Returns a 204 empty response on success.
        > warn
        > The max pinned messages is 50."""
        return await self.api_call(f'/channels/{channel_id}/pins/{message_id}', 'PUT', reason=audit_reason)

    async def delete_pinned_channel_message(self, channel_id, message_id, audit_reason='') -> None:
        """Delete a pinned message in a channel.
        Requires the `MANAGE_MESSAGES` permission.
        Returns a 204 empty response on success."""
        return await self.api_call(f'/channels/{channel_id}/pins/{message_id}', 'DELETE', reason=audit_reason)

    async def group_dm_add_recipient(self, channel_id, user_id, access_token, nick, audit_reason=''):
        """Adds a recipient to a Group DM using their access token"""
        return await self.api_call(f'/channels/{channel_id}/recipients/{user_id}', 'PUT', reason=audit_reason, json={'access_token':access_token,'nick':nick,})

    async def list_guild_emojis(self, guild_id, audit_reason='') -> Emoji:
        """Returns a list of [emoji](https://discordapp.com/developers/docs/resources/emoji#emoji-object) objects for the given guild."""
        r = await self.api_call(f'/guilds/{guild_id}/emojis', 'GET', reason=audit_reason)
        return [Emoji(i) if type(i) is dict else int(i or 0) if type(i) is int or i.isdigit() else [] for i in r]

    async def get_guild_emoji(self, guild_id, emoji_id, audit_reason='') -> Emoji:
        """Returns an [emoji](https://discordapp.com/developers/docs/resources/emoji#emoji-object) object for the given guild and emoji IDs"""
        r = await self.api_call(f'/guilds/{guild_id}/emojis/{emoji_id}', 'GET', reason=audit_reason)
        return Emoji(r)

    async def create_guild_emoji(self, guild_id, name, image, roles, audit_reason='') -> Emoji:
        """Create a new emoji for the guild.
        Requires the `MANAGE_EMOJIS` permission.
        Returns the new [emoji](https://discordapp.com/developers/docs/resources/emoji#emoji-object) object on success.
        Fires a [Guild Emojis Update](https://discordapp.com/developers/docs/topics/gateway#guild-emojis-update) Gateway event.
        > warn
        > Emojis and animated emojis have a maximum file size of 256kb.
        Attempting to upload an emoji larger than this limit will fail and return 400 Bad Request and an error message, but not a [JSON status code](https://discordapp.com/developers/docs/topics/opcodes_and_status_codes#json)."""
        r = await self.api_call(f'/guilds/{guild_id}/emojis', 'POST', reason=audit_reason, json={'name':name,'image':image,'roles':roles,})
        return Emoji(r)

    async def modify_guild_emoji(self, guild_id, emoji_id, name, roles, audit_reason='') -> Emoji:
        """Modify the given emoji.
        Requires the `MANAGE_EMOJIS` permission.
        Returns the updated [emoji](https://discordapp.com/developers/docs/resources/emoji#emoji-object) object on success.
        Fires a [Guild Emojis Update](https://discordapp.com/developers/docs/topics/gateway#guild-emojis-update) Gateway event."""
        r = await self.api_call(f'/guilds/{guild_id}/emojis/{emoji_id}', 'PATCH', reason=audit_reason, json={'name':name,'roles':roles,})
        return Emoji(r)

    async def create_guild(self, name, region=None, icon=None, verification_level=None, default_message_notifications=None, explicit_content_filter=None, roles=None, channels=None, afk_channel_id=None, afk_timeout=None, system_channel_id=None, audit_reason='') -> Guild:
        """Create a new guild.
        Returns a [guild](https://discordapp.com/developers/docs/resources/guild#guild-object) object on success.
        Fires a [Guild Create](https://discordapp.com/developers/docs/topics/gateway#guild-create) Gateway event.
        > warn
        > This endpoint can be used only by bots in less than 10 guilds.
        Assigning a channel to a channel category is not supported by this endpoint, i.e.
        a channel can't have the `parent_id` field."""
        r = await self.api_call(f'/guilds', 'POST', reason=audit_reason, json={'name':name,'region':region,'icon':icon,'verification_level':verification_level,'default_message_notifications':default_message_notifications,'explicit_content_filter':explicit_content_filter,'roles':roles,'channels':channels,'afk_channel_id':afk_channel_id,'afk_timeout':afk_timeout,'system_channel_id':system_channel_id,})
        return Guild(r)

    async def get_guild(self, guild_id, audit_reason='') -> Guild:
        """Returns the [guild](https://discordapp.com/developers/docs/resources/guild#guild-object) object for the given id."""
        r = await self.api_call(f'/guilds/{guild_id}', 'GET', reason=audit_reason)
        return Guild(r)

    async def get_guild_preview(self, guild_id, audit_reason='') -> Guild_Preview:
        """Returns the [guild preview](https://discordapp.com/developers/docs/resources/guild#guild-preview-object) object for the given id, even if the user is not in the guild.
        > info
        > This endpoint is only for Public guilds"""
        r = await self.api_call(f'/guilds/{guild_id}/preview', 'GET', reason=audit_reason)
        return Guild_Preview(r)

    async def modify_guild(self, guild_id, name=None, region=None, verification_level=None, default_message_notifications=None, explicit_content_filter=None, afk_channel_id=None, afk_timeout=None, icon=None, owner_id=None, splash=None, banner=None, system_channel_id=None, rules_channel_id=None, public_updates_channel_id=None, preferred_locale=None, audit_reason='') -> Guild:
        """Modify a guild's settings.
        Requires the `MANAGE_GUILD` permission.
        Returns the updated [guild](https://discordapp.com/developers/docs/resources/guild#guild-object) object on success.
        Fires a [Guild Update](https://discordapp.com/developers/docs/topics/gateway#guild-update) Gateway event.
        > info
        > All parameters to this endpoint are optional"""
        r = await self.api_call(f'/guilds/{guild_id}', 'PATCH', reason=audit_reason, json={'name':name,'region':region,'verification_level':verification_level,'default_message_notifications':default_message_notifications,'explicit_content_filter':explicit_content_filter,'afk_channel_id':afk_channel_id,'afk_timeout':afk_timeout,'icon':icon,'owner_id':owner_id,'splash':splash,'banner':banner,'system_channel_id':system_channel_id,'rules_channel_id':rules_channel_id,'public_updates_channel_id':public_updates_channel_id,'preferred_locale':preferred_locale,})
        return Guild(r)

    async def delete_guild(self, guild_id, audit_reason='') -> None:
        """Delete a guild permanently.
        User must be owner.
        Returns `204 No Content` on success.
        Fires a [Guild Delete](https://discordapp.com/developers/docs/topics/gateway#guild-delete) Gateway event."""
        return await self.api_call(f'/guilds/{guild_id}', 'DELETE', reason=audit_reason)

    async def get_guild_channels(self, guild_id, audit_reason='') -> Channel:
        """Returns a list of guild [channel](https://discordapp.com/developers/docs/resources/channel#channel-object) objects."""
        r = await self.api_call(f'/guilds/{guild_id}/channels', 'GET', reason=audit_reason)
        return [Channel(i) if type(i) is dict else int(i or 0) if type(i) is int or i.isdigit() else [] for i in r]

    async def create_guild_channel(self, guild_id, name, type, topic, bitrate, user_limit, rate_limit_per_user, position, permission_overwrites, parent_id, nsfw, audit_reason='') -> Channel:
        """Create a new [channel](https://discordapp.com/developers/docs/resources/channel#channel-object) object for the guild.
        Requires the `MANAGE_CHANNELS` permission.
        Returns the new [channel](https://discordapp.com/developers/docs/resources/channel#channel-object) object on success.
        Fires a [Channel Create](https://discordapp.com/developers/docs/topics/gateway#channel-create) Gateway event.
        > info
        > All parameters for this endpoint are optional excluding 'name'"""
        r = await self.api_call(f'/guilds/{guild_id}/channels', 'POST', reason=audit_reason, json={'name':name,'type':type,'topic':topic,'bitrate':bitrate,'user_limit':user_limit,'rate_limit_per_user':rate_limit_per_user,'position':position,'permission_overwrites':permission_overwrites,'parent_id':parent_id,'nsfw':nsfw,})
        return Channel(r)

    async def modify_guild_channel_positions(self, guild_id, id, position, audit_reason='') -> None:
        """Modify the positions of a set of [channel](https://discordapp.com/developers/docs/resources/channel#channel-object) objects for the guild.
        Requires `MANAGE_CHANNELS` permission.
        Returns a 204 empty response on success.
        Fires multiple [Channel Update](https://discordapp.com/developers/docs/topics/gateway#channel-update) Gateway events.
        > info
        > Only channels to be modified are required, with the minimum being a swap between at least two channels.This endpoint takes a JSON array of parameters in the following format:"""
        return await self.api_call(f'/guilds/{guild_id}/channels', 'PATCH', reason=audit_reason, json={'id':id,'position':position,})

    async def get_guild_member(self, guild_id, user_id, audit_reason='') -> Guild_Member:
        """Returns a [guild member](https://discordapp.com/developers/docs/resources/guild#guild-member-object) object for the specified user."""
        r = await self.api_call(f'/guilds/{guild_id}/members/{user_id}', 'GET', reason=audit_reason)
        return Guild_Member(r)

    async def list_guild_members(self, guild_id, limit=None, after=None, audit_reason='') -> Guild_Member:
        """Returns a list of [guild member](https://discordapp.com/developers/docs/resources/guild#guild-member-object) objects that are members of the guild.
        > warn
        > In the future, this endpoint will be restricted in line with our [Privileged Intents](https://discordapp.com/developers/docs/topics/gateway#privileged-intents)
        > info
        > All parameters to this endpoint are optional"""
        r = await self.api_call(f'/guilds/{guild_id}/members', 'GET', reason=audit_reason, params={'limit':limit,'after':after,})
        return [Guild_Member(i) if type(i) is dict else int(i or 0) if type(i) is int or i.isdigit() else [] for i in r]

    async def add_guild_member(self, guild_id, user_id, access_token, nick, roles, mute, deaf, audit_reason='') -> dict:
        """Adds a user to the guild, provided you have a valid oauth2 access token for the user with the `guilds.join` scope.
        Returns a 201 Created with the [guild member](https://discordapp.com/developers/docs/resources/guild#guild-member-object) as the body, or 204 No Content if the user is already a member of the guild.
        Fires a [Guild Member Add](https://discordapp.com/developers/docs/topics/gateway#guild-member-add) Gateway event.
        > info
        > All parameters to this endpoint except for `access_token` are optional.
        > info
        > The Authorization header must be a Bot token (belonging to the same application used for authorization), and the bot must be a member of the guild with `CREATE_INSTANT_INVITE` permission."""
        return await self.api_call(f'/guilds/{guild_id}/members/{user_id}', 'PUT', reason=audit_reason, json={'access_token':access_token,'nick':nick,'roles':roles,'mute':mute,'deaf':deaf,})

    async def modify_guild_member(self, guild_id, user_id, nick=None, roles=None, mute=None, deaf=None, channel_id=None, audit_reason='') -> None:
        """Modify attributes of a [guild member](https://discordapp.com/developers/docs/resources/guild#guild-member-object).
        Returns a 204 empty response on success.
        Fires a [Guild Member Update](https://discordapp.com/developers/docs/topics/gateway#guild-member-update) Gateway event.
        If the `channel_id` is set to null, this will force the target user to be disconnected from voice.
        > info
        > All parameters to this endpoint are optional.
        When moving members to channels, the API user _must_ have permissions to both connect to the channel and have the `MOVE_MEMBERS` permission."""
        return await self.api_call(f'/guilds/{guild_id}/members/{user_id}', 'PATCH', reason=audit_reason, json={'nick':nick,'roles':roles,'mute':mute,'deaf':deaf,'channel_id':channel_id,})

    async def modify_current_user_nick(self, guild_id, nick, audit_reason='') -> dict:
        """Modifies the nickname of the current user in a guild.
        Returns a 200 with the nickname on success.
        Fires a [Guild Member Update](https://discordapp.com/developers/docs/topics/gateway#guild-member-update) Gateway event."""
        return await self.api_call(f'/guilds/{guild_id}/members/@me/nick', 'PATCH', reason=audit_reason, json={'nick':nick,})

    async def add_guild_member_role(self, guild_id, user_id, role_id, audit_reason='') -> None:
        """Adds a role to a [guild member](https://discordapp.com/developers/docs/resources/guild#guild-member-object).
        Requires the `MANAGE_ROLES` permission.
        Returns a 204 empty response on success.
        Fires a [Guild Member Update](https://discordapp.com/developers/docs/topics/gateway#guild-member-update) Gateway event."""
        return await self.api_call(f'/guilds/{guild_id}/members/{user_id}/roles/{role_id}', 'PUT', reason=audit_reason)

    async def remove_guild_member_role(self, guild_id, user_id, role_id, audit_reason='') -> None:
        """Removes a role from a [guild member](https://discordapp.com/developers/docs/resources/guild#guild-member-object).
        Requires the `MANAGE_ROLES` permission.
        Returns a 204 empty response on success.
        Fires a [Guild Member Update](https://discordapp.com/developers/docs/topics/gateway#guild-member-update) Gateway event."""
        return await self.api_call(f'/guilds/{guild_id}/members/{user_id}/roles/{role_id}', 'DELETE', reason=audit_reason)

    async def remove_guild_member(self, guild_id, user_id, audit_reason='') -> None:
        """Remove a member from a guild.
        Requires `KICK_MEMBERS` permission.
        Returns a 204 empty response on success.
        Fires a [Guild Member Remove](https://discordapp.com/developers/docs/topics/gateway#guild-member-remove) Gateway event."""
        return await self.api_call(f'/guilds/{guild_id}/members/{user_id}', 'DELETE', reason=audit_reason)

    async def get_guild_bans(self, guild_id, audit_reason='') -> Ban:
        """Returns a list of [ban](https://discordapp.com/developers/docs/resources/guild#ban-object) objects for the users banned from this guild.
        Requires the `BAN_MEMBERS` permission."""
        r = await self.api_call(f'/guilds/{guild_id}/bans', 'GET', reason=audit_reason)
        return [Ban(i) if type(i) is dict else int(i or 0) if type(i) is int or i.isdigit() else [] for i in r]

    async def get_guild_ban(self, guild_id, user_id, audit_reason='') -> Ban:
        """Returns a [ban](https://discordapp.com/developers/docs/resources/guild#ban-object) object for the given user or a 404 not found if the ban cannot be found.
        Requires the `BAN_MEMBERS` permission."""
        r = await self.api_call(f'/guilds/{guild_id}/bans/{user_id}', 'GET', reason=audit_reason)
        return Ban(r)

    async def create_guild_ban(self, guild_id, user_id, deletemessagedays=None, reason=None, audit_reason='') -> None:
        """Create a guild ban, and optionally delete previous messages sent by the banned user.
        Requires the `BAN_MEMBERS` permission.
        Returns a 204 empty response on success.
        Fires a [Guild Ban Add](https://discordapp.com/developers/docs/topics/gateway#guild-ban-add) Gateway event."""
        return await self.api_call(f'/guilds/{guild_id}/bans/{user_id}', 'PUT', reason=audit_reason, params={'deletemessagedays':deletemessagedays,'reason':reason,})

    async def remove_guild_ban(self, guild_id, user_id, audit_reason='') -> None:
        """Remove the ban for a user.
        Requires the `BAN_MEMBERS` permissions.
        Returns a 204 empty response on success.
        Fires a [Guild Ban Remove](https://discordapp.com/developers/docs/topics/gateway#guild-ban-remove) Gateway event."""
        return await self.api_call(f'/guilds/{guild_id}/bans/{user_id}', 'DELETE', reason=audit_reason)

    async def get_guild_roles(self, guild_id, audit_reason='') -> Role:
        """Returns a list of [role](https://discordapp.com/developers/docs/topics/permissions#role-object) objects for the guild."""
        r = await self.api_call(f'/guilds/{guild_id}/roles', 'GET', reason=audit_reason)
        return [Role(i) if type(i) is dict else int(i or 0) if type(i) is int or i.isdigit() else [] for i in r]

    async def create_guild_role(self, guild_id, name, permissions, color, hoist, mentionable, audit_reason='') -> Role:
        """Create a new [role](https://discordapp.com/developers/docs/topics/permissions#role-object) for the guild.
        Requires the `MANAGE_ROLES` permission.
        Returns the new [role](https://discordapp.com/developers/docs/topics/permissions#role-object) object on success.
        Fires a [Guild Role Create](https://discordapp.com/developers/docs/topics/gateway#guild-role-create) Gateway event.
        All JSON params are optional."""
        r = await self.api_call(f'/guilds/{guild_id}/roles', 'POST', reason=audit_reason, json={'name':name,'permissions':permissions,'color':color,'hoist':hoist,'mentionable':mentionable,})
        return Role(r)

    async def modify_guild_role_positions(self, guild_id, id, position, audit_reason='') -> Role:
        """Modify the positions of a set of [role](https://discordapp.com/developers/docs/topics/permissions#role-object) objects for the guild.
        Requires the `MANAGE_ROLES` permission.
        Returns a list of all of the guild's [role](https://discordapp.com/developers/docs/topics/permissions#role-object) objects on success.
        Fires multiple [Guild Role Update](https://discordapp.com/developers/docs/topics/gateway#guild-role-update) Gateway events.This endpoint takes a JSON array of parameters in the following format:"""
        r = await self.api_call(f'/guilds/{guild_id}/roles', 'PATCH', reason=audit_reason, json={'id':id,'position':position,})
        return [Role(i) if type(i) is dict else int(i or 0) if type(i) is int or i.isdigit() else [] for i in r]

    async def modify_guild_role(self, guild_id, role_id, name=None, permissions=None, color=None, hoist=None, mentionable=None, audit_reason='') -> dict:
        """Modify a guild role.
        Requires the `MANAGE_ROLES` permission.
        Returns the updated [role](https://discordapp.com/developers/docs/topics/permissions#role-object) on success.
        Fires a [Guild Role Update](https://discordapp.com/developers/docs/topics/gateway#guild-role-update) Gateway event.
        > info
        > All parameters to this endpoint are optional."""
        return await self.api_call(f'/guilds/{guild_id}/roles/{role_id}', 'PATCH', reason=audit_reason, json={'name':name,'permissions':permissions,'color':color,'hoist':hoist,'mentionable':mentionable,})

    async def delete_guild_role(self, guild_id, role_id, audit_reason='') -> None:
        """Delete a guild role.
        Requires the `MANAGE_ROLES` permission.
        Returns a 204 empty response on success.
        Fires a [Guild Role Delete](https://discordapp.com/developers/docs/topics/gateway#guild-role-delete) Gateway event."""
        return await self.api_call(f'/guilds/{guild_id}/roles/{role_id}', 'DELETE', reason=audit_reason)

    async def get_guild_prune_count(self, guild_id, days, audit_reason='') -> dict:
        """Returns an object with one 'pruned' key indicating the number of members that would be removed in a prune operation.
        Requires the `KICK_MEMBERS` permission."""
        return await self.api_call(f'/guilds/{guild_id}/prune', 'GET', reason=audit_reason, params={'days':days,})

    async def begin_guild_prune(self, guild_id, days, compute_prune_count, audit_reason='') -> dict:
        """Begin a prune operation.
        Requires the `KICK_MEMBERS` permission.
        Returns an object with one 'pruned' key indicating the number of members that were removed in the prune operation.
        For large guilds it's recommended to set the `compute_prune_count` option to `false`, forcing 'pruned' to `null`.
        Fires multiple [Guild Member Remove](https://discordapp.com/developers/docs/topics/gateway#guild-member-remove) Gateway events."""
        return await self.api_call(f'/guilds/{guild_id}/prune', 'POST', reason=audit_reason, params={'days':days,'compute_prune_count':compute_prune_count,})

    async def get_guild_voice_regions(self, guild_id, audit_reason='') -> Voice_Region:
        """Returns a list of [voice region](https://discordapp.com/developers/docs/resources/voice#voice-region-object) objects for the guild.
        Unlike the similar `/voice` route, this returns VIP servers when the guild is VIP-enabled."""
        r = await self.api_call(f'/guilds/{guild_id}/regions', 'GET', reason=audit_reason)
        return [Voice_Region(i) if type(i) is dict else int(i or 0) if type(i) is int or i.isdigit() else [] for i in r]

    async def get_guild_invites(self, guild_id, audit_reason='') -> Invite:
        """Returns a list of [invite](https://discordapp.com/developers/docs/resources/invite#invite-object) objects (with [invite metadata](https://discordapp.com/developers/docs/resources/invite#invite-metadata-object)) for the guild.
        Requires the `MANAGE_GUILD` permission."""
        r = await self.api_call(f'/guilds/{guild_id}/invites', 'GET', reason=audit_reason)
        return [Invite(i) if type(i) is dict else int(i or 0) if type(i) is int or i.isdigit() else [] for i in r]

    async def get_guild_integrations(self, guild_id, audit_reason='') -> Integration:
        """Returns a list of [integration](https://discordapp.com/developers/docs/resources/guild#integration-object) objects for the guild.
        Requires the `MANAGE_GUILD` permission."""
        r = await self.api_call(f'/guilds/{guild_id}/integrations', 'GET', reason=audit_reason)
        return [Integration(i) if type(i) is dict else int(i or 0) if type(i) is int or i.isdigit() else [] for i in r]

    async def create_guild_integration(self, guild_id, type, id, audit_reason='') -> None:
        """Attach an [integration](https://discordapp.com/developers/docs/resources/guild#integration-object) object from the current user to the guild.
        Requires the `MANAGE_GUILD` permission.
        Returns a 204 empty response on success.
        Fires a [Guild Integrations Update](https://discordapp.com/developers/docs/topics/gateway#guild-integrations-update) Gateway event."""
        return await self.api_call(f'/guilds/{guild_id}/integrations', 'POST', reason=audit_reason, json={'type':type,'id':id,})

    async def modify_guild_integration(self, guild_id, integration_id, expire_behavior, expire_grace_period, enable_emoticons, audit_reason='') -> None:
        """Modify the behavior and settings of an [integration](https://discordapp.com/developers/docs/resources/guild#integration-object) object for the guild.
        Requires the `MANAGE_GUILD` permission.
        Returns a 204 empty response on success.
        Fires a [Guild Integrations Update](https://discordapp.com/developers/docs/topics/gateway#guild-integrations-update) Gateway event."""
        return await self.api_call(f'/guilds/{guild_id}/integrations/{integration_id}', 'PATCH', reason=audit_reason, json={'expire_behavior':expire_behavior,'expire_grace_period':expire_grace_period,'enable_emoticons':enable_emoticons,})

    async def delete_guild_integration(self, guild_id, integration_id, audit_reason='') -> None:
        """Delete the attached [integration](https://discordapp.com/developers/docs/resources/guild#integration-object) object for the guild.
        Requires the `MANAGE_GUILD` permission.
        Returns a 204 empty response on success.
        Fires a [Guild Integrations Update](https://discordapp.com/developers/docs/topics/gateway#guild-integrations-update) Gateway event."""
        return await self.api_call(f'/guilds/{guild_id}/integrations/{integration_id}', 'DELETE', reason=audit_reason)

    async def sync_guild_integration(self, guild_id, integration_id, audit_reason='') -> None:
        """Sync an integration.
        Requires the `MANAGE_GUILD` permission.
        Returns a 204 empty response on success."""
        return await self.api_call(f'/guilds/{guild_id}/integrations/{integration_id}/sync', 'POST', reason=audit_reason)

    async def get_guild_embed(self, guild_id, audit_reason='') -> Guild_Embed:
        """Returns the [guild embed](https://discordapp.com/developers/docs/resources/guild#guild-embed-object) object.
        Requires the `MANAGE_GUILD` permission."""
        r = await self.api_call(f'/guilds/{guild_id}/embed', 'GET', reason=audit_reason)
        return Guild_Embed(r)

    async def modify_guild_embed(self, guild_id, audit_reason='') -> Guild_Embed:
        """Modify a [guild embed](https://discordapp.com/developers/docs/resources/guild#guild-embed-object) object for the guild.
        All attributes may be passed in with JSON and modified.
        Requires the `MANAGE_GUILD` permission.
        Returns the updated [guild embed](https://discordapp.com/developers/docs/resources/guild#guild-embed-object) object."""
        r = await self.api_call(f'/guilds/{guild_id}/embed', 'PATCH', reason=audit_reason)
        return Guild_Embed(r)

    async def get_guild_vanity_url(self, guild_id, audit_reason='') -> Invite:
        """Returns a partial [invite](https://discordapp.com/developers/docs/resources/invite#invite-object) object for guilds with that feature enabled.
        Requires the `MANAGE_GUILD` permission.
        `code` will be null if a vanity url for the guild is not set."""
        r = await self.api_call(f'/guilds/{guild_id}/vanity-url', 'GET', reason=audit_reason)
        return Invite(r)

    async def get_guild_widget_image(self, guild_id, style, audit_reason='') -> dict:
        """Returns a PNG image widget for the guild.
        Requires no permissions or authentication.The same documentation also applies to `embed.png`.
        > info
        > All parameters for this endpoint are optional."""
        return await self.api_call(f'/guilds/{guild_id}/widget_png', 'GET', reason=audit_reason, params={'style':style,})

    async def get_invite(self, invite_code, audit_reason='') -> Invite:
        """Returns an [invite](https://discordapp.com/developers/docs/resources/invite#invite-object) object for the given code."""
        r = await self.api_call(f'/invites/{invite_code}', 'GET', reason=audit_reason)
        return Invite(r)

    async def get_current_user(self, audit_reason='') -> User:
        """Returns the [user](https://discordapp.com/developers/docs/resources/user#user-object) object of the requester's account.
        For OAuth2, this requires the `identify` scope, which will return the object _without_ an email, and optionally the `email` scope, which returns the object _with_ an email."""
        r = await self.api_call(f'/users/@me', 'GET', reason=audit_reason)
        return User(r)

    async def get_user(self, user_id, audit_reason='') -> User:
        """Returns a [user](https://discordapp.com/developers/docs/resources/user#user-object) object for a given user ID."""
        r = await self.api_call(f'/users/{user_id}', 'GET', reason=audit_reason)
        return User(r)

    async def modify_current_user(self, username, avatar, audit_reason='') -> User:
        """Modify the requester's user account settings.
        Returns a [user](https://discordapp.com/developers/docs/resources/user#user-object) object on success."""
        r = await self.api_call(f'/users/@me', 'PATCH', reason=audit_reason, json={'username':username,'avatar':avatar,})
        return User(r)

    async def get_current_user_guilds(self, audit_reason='') -> Guild:
        """Returns a list of partial [guild](https://discordapp.com/developers/docs/resources/guild#guild-object) objects the current user is a member of.
        Requires the `guilds` OAuth2 scope."""
        r = await self.api_call(f'/users/@me/guilds', 'GET', reason=audit_reason)
        return [Guild(i) if type(i) is dict else int(i or 0) if type(i) is int or i.isdigit() else [] for i in r]

    async def leave_guild(self, guild_id, audit_reason='') -> None:
        """Leave a guild.
        Returns a 204 empty response on success."""
        return await self.api_call(f'/users/@me/guilds/{guild_id}', 'DELETE', reason=audit_reason)

    async def get_user_dms(self, audit_reason='') -> Channel:
        """Returns a list of [DM channel](https://discordapp.com/developers/docs/resources/channel#channel-object) objects.
        For bots, this is no longer a supported method of getting recent DMs, and will return an empty array."""
        r = await self.api_call(f'/users/@me/channels', 'GET', reason=audit_reason)
        return [Channel(i) if type(i) is dict else int(i or 0) if type(i) is int or i.isdigit() else [] for i in r]

    async def create_dm(self, recipient_id, audit_reason='') -> Channel:
        """Create a new DM channel with a user.
        Returns a [DM channel](https://discordapp.com/developers/docs/resources/channel#channel-object) object."""
        r = await self.api_call(f'/users/@me/channels', 'POST', reason=audit_reason, json={'recipient_id':recipient_id,})
        return Channel(r)

    async def create_group_dm(self, access_tokens, nicks, audit_reason='') -> Channel:
        """Create a new group DM channel with multiple users.
        Returns a [DM channel](https://discordapp.com/developers/docs/resources/channel#channel-object) object.
        This endpoint was intended to be used with the now-deprecated GameBridge SDK.
        DMs created with this endpoint will not be shown in the Discord client
        > warn
        > This endpoint is limited to 10 active group DMs."""
        r = await self.api_call(f'/users/@me/channels', 'POST', reason=audit_reason, json={'access_tokens':access_tokens,'nicks':nicks,})
        return Channel(r)

    async def create_webhook(self, channel_id, name, avatar, audit_reason='') -> Webhook:
        """Create a new webhook.
        Requires the `MANAGE_WEBHOOKS` permission.
        Returns a [webhook](https://discordapp.com/developers/docs/resources/webhook#webhook-object) object on success.
        Webhook names follow our naming restrictions that can be found in our [Usernames and Nicknames](https://discordapp.com/developers/docs/resources/user#usernames-and-nicknames) documentation, with the following additional stipulations:- Webhook names cannot be: 'clyde'"""
        r = await self.api_call(f'/channels/{channel_id}/webhooks', 'POST', reason=audit_reason, json={'name':name,'avatar':avatar,})
        return Webhook(r)

    async def get_channel_webhooks(self, channel_id, audit_reason='') -> Webhook:
        """Returns a list of channel [webhook](https://discordapp.com/developers/docs/resources/webhook#webhook-object) objects.
        Requires the `MANAGE_WEBHOOKS` permission."""
        r = await self.api_call(f'/channels/{channel_id}/webhooks', 'GET', reason=audit_reason)
        return [Webhook(i) if type(i) is dict else int(i or 0) if type(i) is int or i.isdigit() else [] for i in r]

    async def get_guild_webhooks(self, guild_id, audit_reason='') -> Webhook:
        """Returns a list of guild [webhook](https://discordapp.com/developers/docs/resources/webhook#webhook-object) objects.
        Requires the `MANAGE_WEBHOOKS` permission."""
        r = await self.api_call(f'/guilds/{guild_id}/webhooks', 'GET', reason=audit_reason)
        return [Webhook(i) if type(i) is dict else int(i or 0) if type(i) is int or i.isdigit() else [] for i in r]

    async def get_webhook(self, webhook_id, audit_reason='') -> Webhook:
        """Returns the new [webhook](https://discordapp.com/developers/docs/resources/webhook#webhook-object) object for the given id."""
        r = await self.api_call(f'/webhooks/{webhook_id}', 'GET', reason=audit_reason)
        return Webhook(r)

    async def get_webhook_with_token(self, webhook_id, webhook_token, audit_reason=''):
        """Same as above, except this call does not require authentication and returns no user in the webhook object."""
        return await self.api_call(f'/webhooks/{webhook_id}/{webhook_token}', 'GET', reason=audit_reason)

    async def modify_webhook(self, webhook_id, name=None, avatar=None, channel_id=None, audit_reason='') -> Webhook:
        """Modify a webhook.
        Requires the `MANAGE_WEBHOOKS` permission.
        Returns the updated [webhook](https://discordapp.com/developers/docs/resources/webhook#webhook-object) object on success.
        > info
        > All parameters to this endpoint are optional"""
        r = await self.api_call(f'/webhooks/{webhook_id}', 'PATCH', reason=audit_reason, json={'name':name,'avatar':avatar,'channel_id':channel_id,})
        return Webhook(r)

    async def modify_webhook_with_token(self, webhook_id, webhook_token, audit_reason=''):
        """Same as above, except this call does not require authentication, does not accept a `channel_id` parameter in the body, and does not return a user in the webhook object."""
        return await self.api_call(f'/webhooks/{webhook_id}/{webhook_token}', 'PATCH', reason=audit_reason)

    async def delete_webhook(self, webhook_id, audit_reason='') -> None:
        """Delete a webhook permanently.
        Requires the `MANAGE_WEBHOOKS` permission.
        Returns a 204 NO CONTENT response on success."""
        return await self.api_call(f'/webhooks/{webhook_id}', 'DELETE', reason=audit_reason)

    async def delete_webhook_with_token(self, webhook_id, webhook_token, audit_reason=''):
        """Same as above, except this call does not require authentication."""
        return await self.api_call(f'/webhooks/{webhook_id}/{webhook_token}', 'DELETE', reason=audit_reason)

    async def execute_webhook(self, webhook_id, webhook_token, wait, audit_reason=''):
        """
        > warn
        > This endpoint supports both JSON and form data bodies.
        It does require multipart/form-data requests instead of the normal JSON request type when uploading files.
        Make sure you set your `Content-Type` to `multipart/form-data` if you're doing that.
        Note that in that case, the `embeds` field cannot be used, but you can pass an url-encoded JSON body as a form value for `payload_json`."""
        return await self.api_call(f'/webhooks/{webhook_id}/{webhook_token}', 'POST', reason=audit_reason, params={'wait':wait,})

    async def execute_slack_compatible_webhook(self, webhook_id, webhook_token, wait, audit_reason=''):
        return await self.api_call(f'/webhooks/{webhook_id}/{webhook_token}/slack', 'POST', reason=audit_reason, params={'wait':wait,})

    async def get_gateway(self, audit_reason='') -> dict:
        """
        > info
        > This endpoint does not require authentication.Returns an object with a single valid WSS URL, which the client can use for [Connecting](https://discordapp.com/developers/docs/topics/gateway#connecting).
        Clients **should** cache this value and only call this endpoint to retrieve a new URL if they are unable to properly establish a connection using the cached version of the URL."""
        return await self.api_call(f'/gateway', 'GET', reason=audit_reason)

    async def get_gateway_bot(self, audit_reason='') -> dict:
        """
        > warn
        > This endpoint requires authentication using a valid bot token.Returns an object based on the information in [Get Gateway](https://discordapp.com/developers/docs/topics/gateway#get-gateway), plus additional metadata that can help during the operation of large or [sharded](https://discordapp.com/developers/docs/topics/gateway#sharding) bots.
        Unlike the [Get Gateway](https://discordapp.com/developers/docs/topics/gateway#get-gateway), this route should not be cached for extended periods of time as the value is not guaranteed to be the same per-call, and changes as the bot joins/leaves guilds."""
        return await self.api_call(f'/gateway/bot', 'GET', reason=audit_reason)
