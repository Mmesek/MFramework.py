from .timers import *
from . import log, levels
def _check_if_current_bot(self, data):
    if data.user_id == self.user_id:
        self.cache[data.guild_id].connection.session_id = data.session_id

def _check_afk_channel(self, data):
    if data.channel_id == self.cache[data.guild_id].afk_channel:
        data.channel_id = -1
    else:
        data.channel_id = 0
    return data

async def _handle_dynamic_channel(self, data):
    template = self.cache[data.guild_id].dynamic_channels[data.channel_id]
    if 'buffer' in template:
        await self.move_guild_member(data.guild_id, data.user_id, template['buffer'], f"Moved {data.member.user.username} to channel")
    else:
        count = len(self.cache[data.guild_id].dynamic_channels['channels'])+1
    
        new_channel = await self.create_guild_channel(data.guild_id, template['name']+f' #{count}', 2, None, template['bitrate'], template['user_limit'], None, template['position'], template['permission_overwrites'], template['parent_id'], False, "Generated Channel")
        await self.move_guild_member(data.guild_id, data.user_id, new_channel.id, f"Moved {data.member.user.username} to generated channel")
        data.channel_id = new_channel.id
        self.cache[data.guild_id].dynamic_channels['channels'] += [new_channel.id]
    return data

async def _handle_voice_link(self, data):
    r = self.cache[data.guild_id].VoiceLink
    if data.channel_id != 0 and r not in data.member.roles:
        await self.add_guild_member_role(data.guild_id, data.user_id, r, "Voice Role")
    elif data.channel_id == 0 and r in data.member.roles:
        await self.remove_guild_member_role(data.guild_id, data.user_id, r, "Voice Role")

def _should_track_voice(self, data):
    if self.cache[data.guild_id].trackVoice:
        return True
    return False

async def user_left_voice_channel(self, data, channel, track_voice=False):
    if track_voice:
        t = finalize(self, data.guild_id, channel, data.user_id)
        await log.UserVoiceChannel(self, data, channel, int(t[0]))
        if t[1][1] != 0:
            _data = data
            _data.user_id = t[1][0]
            await log.UserVoiceChannel(self, _data, channel, int(t[1][1]))
        await levels.handle_exp(self, data)
    else:
        checkLast(self, data.guild_id, channel, data.user_id)
        await log.UserVoiceChannel(self, data, channel)

async def _handle_voice_activity(self, data):
    track_voice= _should_track_voice(self, data)
    v = self.cache[data.guild_id].voice
    moved = False

    if data.channel_id > 0: #User is on the Voice Channel
        for channel in v:
            if data.user_id in v[channel]: #User is in cached channel
                if channel != data.channel_id:  #Moved to another channel    
                    moved = True
                    await user_left_voice_channel(self, data, channel, track_voice)
                    if channel in self.cache[data.guild_id].dynamic_channels['channels'] and v[channel] == {}:
                        await self.delete_close_channel(channel, "Deleting Empty Generated Channel")
                        self.cache[data.guild_id].dynamic_channels['channels'].remove(channel)
                else:  #Channel is same as before    
                    if track_voice:
                        if data.self_deaf or data.self_mute:  #User is now muted
                            restartTimer(self, data.guild_id, data.channel_id, data.user_id, -1)
                        elif (not data.self_deaf and not data.self_mute) and v[data.channel_id][data.user_id] == -1:  #User is not muted anymore
                            if len(v[data.channel_id]) > 1:
                                startTimer(self, data.guild_id, data.channel_id, data.user_id) #Unmuted
                            else:
                                restartTimer(self, data.guild_id, data.channel_id, data.user_id) #Unmuted Alone
                    return

        if data.channel_id not in v: #Init channel
            v[data.channel_id] = {}

        if len(v[data.channel_id]) >= 1 and data.user_id not in v[data.channel_id]:  #New person Joined channel
            if track_voice:
                if data.self_deaf or data.self_mute:
                    restartTimer(self, data.guild_id, data.channel_id, data.user_id, -1) #Muted Joined
                else:
                    startTimer(self, data.guild_id, data.channel_id, data.user_id) #Unmuted Joined
                for u in v[data.channel_id]:
                    if v[data.channel_id][u] == 0:  #There was someone on VC without Timer 
                        startTimer(self, data.guild_id, data.channel_id, u)
            else:
                startTimer(self, data.guild_id, data.channel_id, data.user_id)
            if not moved:
               await log.UserVoiceChannel(self, data)

        elif len(v[data.channel_id]) == 0:  #Joined empty channel
            if track_voice:
                if data.self_deaf or data.self_mute:
                    restartTimer(self, data.guild_id, data.channel_id, data.user_id, -1) #Joined Empty Channel Muted
                else:
                    restartTimer(self, data.guild_id, data.channel_id, data.user_id)  #Joined Empty Channel unmuted
            else:
                startTimer(self, data.guild_id, data.channel_id, data.user_id)
            if not moved:
                await log.UserVoiceChannel(self, data)

        else: #Not a channel switch event
            print('???')

    else:  #User is not on Voice channel anymore
        for channel in v:
            if data.user_id in v[channel]:
                if data.channel_id == -1:
                    self.cache[data.guild_id].afk[data.user_id] = channel

                await user_left_voice_channel(self, data, channel, track_voice)

                if channel in self.cache[data.guild_id].dynamic_channels['channels'] and v[channel] == {}:
                    await self.delete_close_channel(channel, "Deleting Empty Generated Channel")
                    self.cache[data.guild_id].dynamic_channels['channels'].remove(channel)
                    v.pop(channel)
                    return
