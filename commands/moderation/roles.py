from MFramework.commands import register
from MFramework.database import alchemy as db
import re
@register(group="Admin", help="Create reaction role")
async def create_rr(self, channel_slash_message, role, reaction, roleGroup='None', *args, data, **kwargs):
    if len(channel_slash_message.split("/")) > 1:
        channel = channel_slash_message.split("/")
        message = channel[1]
        channel = channel[0]
    else:
        channel = data.channel_id
        message = channel_slash_message
    reaction = reaction.replace('<:', '').replace('>', '')
    role = int(re.search('(\d+)', role)[0])
    g = roleGroup
    message = int(message)
    channel = int(channel)

    if ':' not in reaction:
        reaction_ = reaction + ':0'
    else:
        reaction_ = reaction
    if g not in self.cache[data.guild_id].reactionRoles:
        self.cache[data.guild_id].reactionRoles[g] = {message: {reaction_: [role]}}
    else:
        if message not in self.cache[data.guild_id].reactionRoles[g]:
            self.cache[data.guild_id].reactionRoles[g][message] = {reaction_: [role]}
        else:
            self.cache[data.guild_id].reactionRoles[g][message][reaction_] = [role]
    #session = self.db.sql.session()
    r = db.ReactionRoles(data.guild_id, channel, message, role, reaction_, roleGroup)
    #session.add(r)
    #session.commit()
    self.db.sql.add(r)
    await self.create_reaction(channel, message, reaction)


@register(group="Admin", help="Remove reaction role")
async def remove_rr(self, channel, message, reaction, *args, data, **kwargs):
    params = data.content.split(" ")
    if len(params[0].split("/")) > 1:
        channel = params[0].split("/")
        message = channel[1]
        channel = channel[0]
    else:
        channel = data.channel_id
        message = params[0]
    reaction = params[1]
    await self.db.delete(
        "ReactionRoles",
        "GuildID=? AND ChannelID=? AND MessageID=? AND Reaction=?",
        [data.guild_id, channel, message, reaction],
    )
    await self.delete_own_reaction(channel, message, reaction)


@register(group="Admin", help="Update reaction role")
async def update_rr(self, *args, data, **kwargs):
    await self.message(
        data.channel_id,
        "Look, remove it and then create again or make me sql query\
 for update cause, honestly: what exactly do you want to update? Add a group? Change Role? Reaction? Bro, come\
 on, be serious. !remove_rr and then !add_rr, you can do it",
    )


@register(group="Admin", help="Creates custom command/reaction", category="")
async def add_cc(self, name, trigger, response, group, *args, data, **kwargs):
    """$execute$command\n$$"""
    params = data.content.split(";")
    name = params[0]
    trigger = params[1]
    response = params[2]
    req = params[3]
    await self.db.insert(
        "Regex",
        "GuildID, UserID, Name, Trigger, Response, ReqRole",
        [data.guild_id, data.author.id, name, trigger, response, req],
    )
    await self.cache.recompileTriggers(data)

@register(group='Admin', help='Removes custom command/reaction', category='')
async def remove_cc(self, name, trigger, *args, data, **kwargs):
    params = data.content.split(';')
    name = params[0]
    trigger = params[1]
    await self.db.delete('Regex','GuildID=? AND Name=? AND Trigger=?',[data['guild_id'],name, trigger])
    await self.cache.recompileTriggers(data)


def getfromdb(name):
    pass
from MFramework.utils.utils import Embed

@register(group='Mod', help='Creates message with custom embed', alias='', category='')
async def customEmbed(self, embedName, *args, data, **kwargs):
    e = getfromdb(embedName)
    embed = Embed()
    for val in e:
        if val is not None:
            continue
    embed.setTitle(e[1])
    embed.setDescription(e[2])
    embed.setUrl(e)
    if e.timestamp is not None:
        if e.timestamp == 'message_trigger':
            embed.setTimestamp(data['timestamp'])
    embed.setThumbnail()
    embed.setImage()
    embed.setFooter()
    embed.setColor()
    embed.setAuthor()
    for field in e.fields:
        embed.addField(field[0], field[1], field[2])