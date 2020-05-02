from . import alchemy as db
import datetime, time, re
from ..discord.objects import *

class Cache:
    __slots__ = ('groups', 'disabled_channels', 'disabled_roles', 'logging', 'language',
    'alias', 'reactionRoles', 'levels', 'webhooks', 'responses',
    'name', 'color', 'joined', 'member_count',
    'messages', 'voice', 'channels', 'members', 'roles', 'reactions', 'bot', 'trackPresence', 'presenceRoles', 'canned')
    groups: dict
    disabled_channels: tuple
    disabled_roles: tuple
    logging: dict

    alias: str
    reactionRoles: dict
    levels: dict
    webhooks: dict
    responses: list

    name: str
    color: int
    joined: datetime
    member_count: int

    messages: dict
    voice: list
    channels: list
    members: list
    roles: list
    reactions: list

    bot: dict
    def __init__(self, data, datab, user_id, alias):
        guildID = data.id
        session = datab.sql.session()
        g = session.query(db.Servers).filter(db.Servers.GuildID == guildID).first()
        if g == None:
            self.initGuild(data, datab, user_id, alias)
            g = session.query(db.Servers).filter(db.Servers.GuildID == guildID).first()
        else:
            self.setBot(data, user_id)

        self.groups = {}

        self.groups['Admin'] = g.AdminIDs
        self.groups['Mod'] = g.ModIDs
        self.groups['Vip'] = g.VipIDs
        self.groups['Nitro'] = g.NitroIDs
        self.groups['Muted'] = g.MutedIDs
        self.disabled_channels = g.NoExpChannels
        self.disabled_roles = g.NoExpRoles
        self.logging = {}  #g.Logging
        self.trackPresence = g.TrackPresence
        self.language = g.Language
        self.canned = {}
        self.recompileCanned(datab, guildID)

        self.alias = g.Alias
        #self.reactionRoles = {i.RoleGroup:{i.MessageID:{i.Reaction:i.RoleID}} for i in session.query(db.ReactionRoles).filter(db.Servers.GuildID == guildID).all()}
        self.reactionRoles = {}
        for i in session.query(db.ReactionRoles).filter(db.ReactionRoles.GuildID == guildID).all():
            rr = self.reactionRoles
            if rr == {}:
                rr[i.RoleGroup] = {}
            if i.MessageID not in rr[i.RoleGroup]:
                rr[i.RoleGroup][i.MessageID] = {}
            if i.RoleID not in rr[i.RoleGroup][i.MessageID]:
                rr[i.RoleGroup][i.MessageID][i.Reaction] = []
            rr[i.RoleGroup][i.MessageID][i.Reaction] += [i.RoleID]
            self.reactionRoles = rr
        self.presenceRoles = session.query(db.PresenceRoles).filter(db.Servers.GuildID == guildID).all()
        self.levels = session.query(db.LevelRoles).filter(db.Servers.GuildID == guildID).all()
        self.webhooks = session.query(db.Webhooks).filter(db.Servers.GuildID == guildID).all()
        self.responses = session.query(db.Regex).filter(db.Servers.GuildID == guildID).all()

        self.color = g.Color
        self.fillCache(data)
        self.messages = {}
    def setBot(self, data, user_id):
        for member in data.members:
            if member.user.id == user_id:
                self.bot = member
                break
    def initGuild(self, data, datab, user_id, alias):
        self.setBot(data, user_id)
        admin, mod, vip, nitro, muted, rnoexp, cnoexp = [], [], [], [], [], [], []
        self.color = None
        for role in data.roles:
            #if (self.color is None and self.bot is not None) and
            if (role.id in self.bot.roles):
                #self.color = role['color']
                if role.managed is True:
                    self.color = (role.position, role.color, True)
                elif self.color == None:
                    self.color = (role.position, role.color, False)
                elif role.position > self.color[0] and self.color[2] != True:
                    self.color = (role.position, role.color, False)
            
            if role.name == "Admin" or role.name == "Administrator":
                admin += [role.id]
            elif role.name == "Moderator":
                mod += [role.id]
            elif role.name == "Nitro Booster" and role.managed is True:
                nitro += [role.id]
            elif role.name == "Muted":
                muted += [role.id]
            elif role.name.lower() in {"VIP", "Contributor"}:
                vip += [role.id]
            elif role.name == "No Exp":
                rnoexp += [role.id]
        if self.color != None:
            self.color = self.color[1]
        for channel in data.channels:
            if "bot" in channel.name:
                cnoexp += [channel.id]
        guildID = data.id
        session = datab.sql.session()
        g = db.Servers(guildID, admin, mod, vip, nitro, muted, rnoexp, cnoexp, alias, self.color, False)
        session.add(g)
        session.commit()

        
    def fillCache(self, data: Guild):
        self.name = data.name#['name']
        self.joined = data.joined_at#['joined_at']
        self.member_count = data.member_count#['member_count']
        self.voice = []
        for vc in data.voice_states:
            self.voice += [vc]
        #self.voice = data.voice_states
        self.channels = []
        for channel in data.channels:
            self.channels += [channel]
        #self.channels = data.channels
        self.members = []
        for member in data.presences:
            self.members += [member]
        #self.members = data.presences
        self.roles = []
        for role in data.roles:
            self.roles += [role]
        #self.roles = data.roles
        self.reactions = []
        for reaction in data.emojis:
            self.reactions += [reaction]
        #self.reactions = data.emojis
    
    def message(self, message_id, data):
        self.messages[message_id] = data
    def getMessage(self, message_id):
        return self.messages.pop(message_id, None)
    
    def update_server_data(self, data):
        self.name = data.name
        self.member_count = data.member_count
        self.roles = data.roles
        self.reactions = data.emojis

    def voice_(self, data):
        if data.user_id not in self.voice:
            self.voice[data.user_id] = time.time()
        return

    def cachedVoice(self, data):
        join = self.voice.pop(data.user_id, None)
        now = time.time()
        if join is not None:
            return now - join
        return 0

    def cachedRoles(self, roles):
        groups = self.groups
        for group in groups:
            if any(i in roles for i in groups[group]):
                return group
        return "Global"

    async def recompileTriggers(self, server):
        reg = await self.db.selectMultiple("Regex", "ReqRole, Name, Trigger", "WHERE GuildID=?", [server])
        responses, triggers = {}, {}
        for trig in reg:
            if trig[0] not in responses:
                responses[trig[0]] = {}
            if trig[1] not in responses[trig[0]]:
                responses[trig[0]][trig[1]] = trig[2]
            else:
                responses[trig[0]] = {trig[1]: trig[2]}
        for r in responses:
            #for response in responses[r]:
#                if response[0] == 'r':
#                    responses[r][response[0]] = re.escape(response[1])
            p = re.compile(r"(?:{})".format("|".join("(?P<{}>{})".format(k, f) for k, f in responses[r].items())))
            # p = re.compile(r'(?:{})'.format('|'.join(map(re.escape, longest_first))))
            triggers[r] = p
        self.cache[server].responses = triggers
    def recompileCanned(self, datab, guildID):
        session = datab.sql.session()
        s = session.query(db.Snippets).filter(db.Snippets.GuildID == guildID).filter(db.Snippets.Type == 'cannedresponse')
        self.canned['patterns'] = re.compile('|'.join([f'(?P<{re.escape(i.Name)}>{i.Trigger})' for i in s]))
        self.canned['responses'] = {re.escape(i.Name):i.Response for i in s}


class CacheDM:
    __slots__ = ("messages")
    def __init__(self):
        self.messages = {}
    def message(self, data):
        message_id = data.id
        self.messages[message_id] = data
    def getMessage(self, message_id):
        return self.messages.pop(message_id, None)
