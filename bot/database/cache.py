import time
import json
import re
from bot.utils.utils import replaceMultiple


class Cache:
    def __init__(self, db):
        self.cache = {}
        self.db = db

    def message(self, data):
        if len(self.cache[data["guild_id"]]["msgs"]) == 256:
            self.cache[data["guild_id"]]["msgs"].pop(list(self.cache[data["guild_id"]]["msgs"].keys())[0], None)
        self.cache[data["guild_id"]]["msgs"][data["id"]] = data

    def cachedMessage(self, data):
        return self.cache[data["guild_id"]]["msgs"].pop(data["id"], None)

    async def server_data(self, data):
        db = await self.db.selectOne(
            "Servers",
            "AdminIDs, ModIDs, VipIDs, NitroIDs, MutedIDs, NoExpRoles, NoExpChannels",
            "WHERE GuildID=?",
            [data["id"]],
        )
        if db is None:
            admin, mod, vip, nitro, muted, rnoexp, cnoexp = [], [], [], [], [], [], []
            for role in data["roles"]:
                if role["name"] == "Admin" or role["name"] == "Administrator":
                    admin += [role["id"]]
                elif role["name"] == "Moderator":
                    mod += [role["id"]]
                elif role["name"] == "Nitro Booster" and role["managed"] is True:
                    nitro += [role["id"]]
                elif role["name"] == "Muted":
                    muted += [role["id"]]
                elif role["name"].lower() in {"VIP", "Contributor"}:
                    vip += [role["id"]]
                elif role["name"] == "No Exp":
                    rnoexp += [role["id"]]
            for channel in data["channels"]:
                if "bot" in channel["name"]:
                    cnoexp += [channel["id"]]
            await self.db.insert(
                "Servers",
                "GuildID, AdminIDs, ModIDs, VipIDs, NitroIDs, MutedIDs, NoExpRoles, NoExpChannels",
                [
                    data["id"],
                    json.dumps(admin),
                    json.dumps(mod),
                    json.dumps(vip),
                    json.dumps(nitro),
                    json.dumps(muted),
                    json.dumps(rnoexp),
                    json.dumps(cnoexp),
                ],
            )
            db = await self.db.selectOne(
                "Servers",
                "AdminIDs, ModIDs, VipIDs, NitroIDs, MutedIDs, NoExpRoles, NoExpChannels",
                "WHERE GuildID=?",
                [data["id"]],
            )
        logging = await self.db.selectMultiple(
            "Webhooks", "Webhook", "WHERE GuildID=? AND Source=?", [data["id"], "Log"]
        )
        rroles = await self.db.selectMultiple(
            "ReactionRoles", "MessageID, RoleID, Reaction, RoleGroup", "WHERE GuildID=?", [data["id"]]
        )
        rr, responses, triggers = {}, {}, {}
        
        if logging != []:
            logging = logging[0]
        
        for r in rroles:
            if r[3] == "":
                gr = "None"
            else:
                gr = r[3]
            if gr not in rr:
                rr[gr] = {}
            if str(r[0]) not in rr[gr]:
                rr[gr][str(r[0])] = {}
            rr[gr][str(r[0])][r[2]] = str(r[1])
        
        users = {}
        for presence in data["presences"]:
            if "nickname" in presence:
                users[presence["nickname"]] = presence["user"]["id"]
        self.cache[data["id"]] = {
            "msgs": {},
            "joined":[],
            "name": data["name"],
            "member_count": data["member_count"],
            "since": data["joined_at"],
            "voice": data["voice_states"],
            "channels": data["channels"],
            "members": data["presences"],
            "roles": data["roles"],
            "reactions": data["emojis"],
            "disabled_channels": replaceMultiple(db[6], ["[", "]", '"'], "").split(", "),
            "disabled_roles": replaceMultiple(db[5], ["[", "]", '"'], "").split(", "),
            "groups": {
                "Admin": replaceMultiple(db[0], ["[", "]", '"'], "").split(", "),
                "Mod": replaceMultiple(db[1], ["[", "]", '"'], "").split(", "),
                "Vip": replaceMultiple(db[2], ["[", "]", '"'], "").split(", "),
                "Nitro": replaceMultiple(db[3], ["[", "]", '"'], "").split(", "),
                "Muted": replaceMultiple(db[4], ["[", "]", '"'], "").split(", "),
            },
            "reactionRoles": rr,
            "responses": triggers,
            "logging": {"all": logging},
        }
        await self.recompileTriggers(data['id'])

    def update_server_data(self, data):
        self.cache[data["id"]]["name"] = data["name"]
        self.cache[data["id"]]["member_count"] = data["member_count"]
        self.cache[data["id"]]["roles"] = data["roles"]
        self.cache[data["id"]]["reactions"] = data["emojis"]

    def voice(self, data):
        if data["user_id"] not in self.cache[data["id"]]["voice"]:
            self.cache[data["id"]]["voice"][data["user_id"]] = time.time()
        return

    def cachedVoice(self, data):
        join = self.cache[data["id"]]["voice"].pop(data["user_id"], None)
        now = time.time()
        if join is not None:
            return now - join
        return 0

    def cachedRoles(self, guild, roles):
        groups = self.cache[guild]["groups"]
        for role in roles:
            for group in groups:
                if role in groups[group]:
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
            for response in responses[r]:
                if response[0] == 'r':
                    responses[r][response[0]] = re.escape(response[1])
            p = re.compile(r"(?:{})".format("|".join("(?P<{}>{})".format(k, f) for k, f in responses[r].items())))
            # p = re.compile(r'(?:{})'.format('|'.join(map(re.escape, longest_first))))
            triggers[r] = p
        self.cache[server]["responses"] = triggers
