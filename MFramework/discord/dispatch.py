# Generated file from docs at 17:28 2020/03/20.
message_type = {}
import sys, traceback
class Dispatch:
    async def hello(self, data):
        """Defines the heartbeat interval"""
        mt = message_type.get('hello', None)
        return await mt[0](self, mt[1](data)) if mt is not None else None 

    async def ready(self, data):
        """Contains the initial state information"""
        mt = message_type.get('ready', None)
        return await mt[0](self, mt[1](data)) if mt is not None else None 

    async def resumed(self, data):
        """Response to [resume](https://discordapp.com/developers/docs/topics/gateway#resume)"""
        mt = message_type.get('resumed', None)
        return await mt[0](self, mt[1](data)) if mt is not None else None 

    async def reconnect(self, data):
        """Server is going away, client should reconnect to gateway and resume"""
        mt = message_type.get('reconnect', None)
        return await mt[0](self, mt[1](data)) if mt is not None else None 

    async def invalid_session(self, data):
        """Failure response to [identify](https://discordapp.com/developers/docs/topics/gateway#identify) or [resume](https://discordapp.com/developers/docs/topics/gateway#resume) or invalid active session"""
        mt = message_type.get('invalid_session', None)
        return await mt[0](self, mt[1](data)) if mt is not None else None 

    async def channel_create(self, data):
        """New channel created"""
        mt = message_type.get('channel_create', None)
        return await mt[0](self, mt[1](data)) if mt is not None else None 

    async def channel_update(self, data):
        """Channel was updated"""
        mt = message_type.get('channel_update', None)
        return await mt[0](self, mt[1](data)) if mt is not None else None 

    async def channel_delete(self, data):
        """Channel was deleted"""
        mt = message_type.get('channel_delete', None)
        return await mt[0](self, mt[1](data)) if mt is not None else None 

    async def channel_pins_update(self, data):
        """Message was pinned or unpinned"""
        mt = message_type.get('channel_pins_update', None)
        return await mt[0](self, mt[1](data)) if mt is not None else None 

    async def guild_create(self, data):
        """Lazy-load for unavailable guild, guild became available, or user joined a new guild"""
        mt = message_type.get('guild_create', None)
        return await mt[0](self, mt[1](data)) if mt is not None else None 

    async def guild_update(self, data):
        """Guild was updated"""
        mt = message_type.get('guild_update', None)
        return await mt[0](self, mt[1](data)) if mt is not None else None 

    async def guild_delete(self, data):
        """Guild became unavailable, or user left/was removed from a guild"""
        mt = message_type.get('guild_delete', None)
        return await mt[0](self, mt[1](data)) if mt is not None else None 

    async def guild_ban_add(self, data):
        """User was banned from a guild"""
        mt = message_type.get('guild_ban_add', None)
        return await mt[0](self, mt[1](data)) if mt is not None else None 

    async def guild_ban_remove(self, data):
        """User was unbanned from a guild"""
        mt = message_type.get('guild_ban_remove', None)
        return await mt[0](self, mt[1](data)) if mt is not None else None 

    async def guild_emojis_update(self, data):
        """Guild emojis were updated"""
        mt = message_type.get('guild_emojis_update', None)
        return await mt[0](self, mt[1](data)) if mt is not None else None 

    async def guild_integrations_update(self, data):
        """Guild integration was updated"""
        mt = message_type.get('guild_integrations_update', None)
        return await mt[0](self, mt[1](data)) if mt is not None else None 

    async def guild_member_add(self, data):
        """New user joined a guild"""
        mt = message_type.get('guild_member_add', None)
        return await mt[0](self, mt[1](data)) if mt is not None else None 

    async def guild_member_remove(self, data):
        """User was removed from a guild"""
        mt = message_type.get('guild_member_remove', None)
        return await mt[0](self, mt[1](data)) if mt is not None else None 

    async def guild_member_update(self, data):
        """Guild member was updated"""
        mt = message_type.get('guild_member_update', None)
        return await mt[0](self, mt[1](data)) if mt is not None else None 

    async def guild_members_chunk(self, data):
        """Response to [request guild members](https://discordapp.com/developers/docs/topics/gateway#request-guild-members)"""
        mt = message_type.get('guild_members_chunk', None)
        return await mt[0](self, mt[1](data)) if mt is not None else None 

    async def guild_role_create(self, data):
        """Guild role was created"""
        mt = message_type.get('guild_role_create', None)
        return await mt[0](self, mt[1](data)) if mt is not None else None 

    async def guild_role_update(self, data):
        """Guild role was updated"""
        mt = message_type.get('guild_role_update', None)
        return await mt[0](self, mt[1](data)) if mt is not None else None 

    async def guild_role_delete(self, data):
        """Guild role was deleted"""
        mt = message_type.get('guild_role_delete', None)
        return await mt[0](self, mt[1](data)) if mt is not None else None 

    async def invite_create(self, data):
        """Invite to a channel was created"""
        mt = message_type.get('invite_create', None)
        return await mt[0](self, mt[1](data)) if mt is not None else None 

    async def invite_delete(self, data):
        """Invite to a channel was deleted"""
        mt = message_type.get('invite_delete', None)
        return await mt[0](self, mt[1](data)) if mt is not None else None 

    async def message_create(self, data):
        """Message was created"""
        mt = message_type.get('message_create', None)
        try:
            await mt[0](self, mt[1](data)) if mt is not None else None
        except TypeError as ex:
            error = ''
            t = traceback.extract_tb(sys.exc_info()[2], limit=-1)
            if 'missing' in str(ex):
                error = str(ex).split(' ', 1)[1]
                err = f'{sys.exc_info()}'
                print(error)
                await self.message(data['channel_id'], error.capitalize().replace("'",'`'))
        except Exception as ex:
            print('Exception:',ex)
            print(data)
        return 

    async def message_update(self, data):
        """Message was edited"""
        mt = message_type.get('message_update', None)
        return await mt[0](self, mt[1](data)) if mt is not None else None 

    async def message_delete(self, data):
        """Message was deleted"""
        mt = message_type.get('message_delete', None)
        return await mt[0](self, mt[1](data)) if mt is not None else None 

    async def message_delete_bulk(self, data):
        """Multiple messages were deleted at once"""
        mt = message_type.get('message_delete_bulk', None)
        return await mt[0](self, mt[1](data)) if mt is not None else None 

    async def message_reaction_add(self, data):
        """User reacted to a message"""
        mt = message_type.get('message_reaction_add', None)
        return await mt[0](self, mt[1](data)) if mt is not None else None 

    async def message_reaction_remove(self, data):
        """User removed a reaction from a message"""
        mt = message_type.get('message_reaction_remove', None)
        return await mt[0](self, mt[1](data)) if mt is not None else None 

    async def message_reaction_remove_all(self, data):
        """All reactions were explicitly removed from a message"""
        mt = message_type.get('message_reaction_remove_all', None)
        return await mt[0](self, mt[1](data)) if mt is not None else None 

    async def message_reaction_remove_emoji(self, data):
        """All reactions for a given emoji were explicitly removed from a message"""
        mt = message_type.get('message_reaction_remove_emoji', None)
        return await mt[0](self, mt[1](data)) if mt is not None else None 

    async def presence_update(self, data):
        """User was updated"""
        mt = message_type.get('presence_update', None)
        return await mt[0](self, mt[1](data)) if mt is not None else None 

    async def typing_start(self, data):
        """User started typing in a channel"""
        mt = message_type.get('typing_start', None)
        return await mt[0](self, mt[1](data)) if mt is not None else None 

    async def user_update(self, data):
        """Properties about the user changed"""
        mt = message_type.get('user_update', None)
        return await mt[0](self, mt[1](data)) if mt is not None else None 

    async def voice_state_update(self, data):
        """Someone joined, left, or moved a voice channel"""
        mt = message_type.get('voice_state_update', None)
        return await mt[0](self, mt[1](data)) if mt is not None else None 

    async def voice_server_update(self, data):
        """Guild's voice server was updated"""
        mt = message_type.get('voice_server_update', None)
        return await mt[0](self, mt[1](data)) if mt is not None else None 

    async def webhooks_update(self, data):
        """Guild channel webhook was created, update, or deleted"""
        mt = message_type.get('webhooks_update', None)
        return await mt[0](self, mt[1](data)) if mt is not None else None 

