from mlib.utils import replaceMultiple
def parseMention(message: str) -> str:
    return replaceMultiple(message, ['<:', '@!', '#', '&', '<', ':>', '>', '@'], '')

def param(message: str) -> list:
    return replaceMultiple(message, ['<:', '@!', '#', '&', '<', ':>', '>', '@'], '').split(' ')[1:]

async def get_usernames(self, guild_id: int, user_id: int) -> str:
    try:
        u = self.cache[guild_id].members[user_id].user.username
    except:
        try:
            u = await self.get_guild_member(guild_id, user_id)
        except:
            return None
        self.cache[guild_id].members[user_id] = u
        u = u.user.username
    return u
