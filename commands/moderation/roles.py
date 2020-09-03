from MFramework.database import alchemy as db
import re
from MFramework.commands import ctxRegister, BaseCtx
@ctxRegister(group='Admin', help='Manages Reaction Role. Type one of: [create/remove]. Arguments: [role/reaction] (reaction) (group)', alias='rr', category='')
class ReactionRole(BaseCtx):
    def __init__(self, type, channel_slash_message, *args, bot, data, **kwargs):
        self.type = type
        s = self.resolve_location(channel_slash_message, data)
        self.channel_id = s[0]
        self.message = s[1]
        self.args = args
        self.kwargs = kwargs
        self.bot = bot
        self.channel = data.channel_id
        self.user = data.author.id
        self.guild_id  = data.guild_id
    async def execute(self, *args, data, **kwargs):
        try:
            if 'create' == self.type:
                await self.create(self.bot)
            elif 'remove' == self.type:
                await self.remove(self.bot)
            elif 'update' == self.type:
                await self.update(self.bot)
        except Exception as ex:
            pass
        await self.end()
    
    def resolve_location(self, channel_slash_message, data):
        if len(channel_slash_message.split("/")) > 1:
            channel = channel_slash_message.split("/")
            message = channel[1]
            channel = channel[0]
        else:
            channel = data.channel_id
            message = channel_slash_message
        return (int(channel), int(message))

    def isUnicodeReaction(self, reaction):
        reaction = reaction.replace('<:', '').replace('>', '')
        if ':' not in reaction:
            return reaction + ':0'
        else:
            return reaction
    async def create(self, bot):  #, channel_slash_message, role, reaction, roleGroup='None', *args, data, **kwargs):
        role = self.args[0]
        reaction = self.args[1]
        try:
            roleGroup = self.args[2]
        except:
            roleGroup = None
        role = int(re.search('(\d+)', role)[0])
        g = roleGroup
        reaction_ = self.isUnicodeReaction(reaction)
        if g not in bot.cache[self.guild_id].reactionRoles:
            bot.cache[self.guild_id].reactionRoles[g] = {self.message: {reaction_: [role]}}
        else:
            if self.message not in bot.cache[self.guild_id].reactionRoles[g]:
                bot.cache[self.guild_id].reactionRoles[g][self.message] = {reaction_: [role]}
            else:
                bot.cache[self.guild_id].reactionRoles[g][self.message][reaction_] = [role]
        r = db.ReactionRoles(self.guild_id, self.channel_id, self.message, role, reaction_, roleGroup)
        bot.db.sql.add(r)
        await bot.create_reaction(self.channel_id, self.message, reaction)

    async def remove(self, bot):
        reaction = self.args[0]
        reaction_ = self.isUnicodeReaction(reaction)
        session = bot.db.sql.session()
        r = session.query(db.ReactionRoles).filter(db.ReactionRoles.GuildID == self.guild_id).filter(db.ReactionRoles.ChannelID == self.channel_id).filter(db.ReactionRoles.MessageID == self.message).filter(db.ReactionRoles.Reaction == reaction_).first()
        bot.cache[self.guild_id].reactionRoles[r.RoleGroup][self.message].pop(reaction_)
        if bot.cache[self.guild_id].reactionRoles[r.RoleGroup][self.message] == {}:
            bot.cache[self.guild_id].reactionRoles[r.RoleGroup].pop(self.message)
            if bot.cache[self.guild_id].reactionRoles[r.RoleGroup] == {}:
                bot.cache[self.guild_id].reactionRoles.pop(r.RoleGroup)
        session.delete(r)
        await bot.delete_own_reaction(self.channel_id, self.message, reaction_)
        session.commit()


@ctxRegister(group='System', help='Short description to use with help command', alias='', category='')
class crr(BaseCtx):
    '''Extended description to use with detailed help command'''
    def __init__(self, type, channel_slash_message, *args, bot, data, **kwargs):
        self.type = type
        s = self.resolve_location(channel_slash_message, data)
        self.channel_id = s[0]
        self.message = s[1]
        self.args = args
        self.kwargs = kwargs
        self.bot = bot
        self.channel = data.channel_id
        self.user = data.author.id
        self.guild_id  = data.guild_id
    async def execute(self, *args, data, **kwargs):
        if data.content == '--exit':
            await self.end()
        elif 'create' in data.content:
            await self.bot.message(self.channel, 'Ready')
        else:
            d = data.content.replace('\n', ' ').split(' ')
            if len(d) % 2 != 0:
                rg = d[-1]
                d = d[:-1]
            else:
                rg = None
            role = d[0]
            reaction = d[1]
            if len(d) == 3:
                rg = d[2]
            elif len(d) > 3:
                dd = []
                for i in range(0, len(d), 2):
                    dd += [(d[i], d[i+1])]
                for role, reaction in dd:
                    await self.create(reaction, role, self.bot, rg)
                return
            await self.create(role, reaction, self.bot, rg)
    def resolve_location(self, channel_slash_message, data):
        if len(channel_slash_message.split("/")) > 1:
            channel = channel_slash_message.split("/")
            message = channel[1]
            channel = channel[0]
        else:
            channel = data.channel_id
            message = channel_slash_message
        return (int(channel), int(message))

    def isUnicodeReaction(self, reaction):
        reaction = reaction.replace('<:', '').replace('>', '')
        if ':' not in reaction:
            return reaction + ':0'
        else:
            return reaction
    async def create(self, role, reaction, bot, roleGroup=None):  #, channel_slash_message, role, reaction, roleGroup='None', *args, data, **kwargs):
        #role = self.args[0]
        #reaction = self.args[1]
#        try:
#            roleGroup = #self.args[2]
#        except:
#            roleGroup = None
        role = int(re.search('(\d+)', role)[0])
        g = roleGroup
        reaction_ = self.isUnicodeReaction(reaction)
        if g not in bot.cache[self.guild_id].reactionRoles:
            bot.cache[self.guild_id].reactionRoles[g] = {self.message: {reaction_: [role]}}
        else:
            if self.message not in bot.cache[self.guild_id].reactionRoles[g]:
                bot.cache[self.guild_id].reactionRoles[g][self.message] = {reaction_: [role]}
            else:
                bot.cache[self.guild_id].reactionRoles[g][self.message][reaction_] = [role]
        r = db.ReactionRoles(self.guild_id, self.channel_id, self.message, role, reaction_, roleGroup)
        bot.db.sql.add(r)
        await bot.create_reaction(self.channel_id, self.message, reaction)