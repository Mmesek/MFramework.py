#cache = { 
# "server": {
#   "message":{
#       "id":{}},
#   "reactions":{
#       "message_id":{
#           "name:id":["role","group"]}}, 
#   "roles":{
#       "123":2, #mod
#       "234":1, #admin
#       "345":4, #vip
#       "456":3  #nitro
#       }, 
#   "muted":"567"
#   "groups":["1","2","3"],
#   "responses":{
#       "trigger":"response"},
#   "logging":{
#       "dm":"webhook",
#       "modActions":"webhook",
#       "botActions":"webhook",
#       "logChannel":"webhook"}
#   }
# }
import time
class Cache:
    def __init__(self, db):
        self.cache = {}
        self.db = db
    def message(self, data):
        if len(self.cache[data['guild_id']]['msgs']) == 256:
            self.cache[data['guild_id']]['msgs'].pop(list(self.cache[data['guild_id']]['msgs'].keys())[0],None)
        self.cache[data['guild_id']]['msgs'][data['id']] = data
    def cachedMessage(self, data):
        return self.cache[data['guild_id']]['msgs'].pop(data['id'],None)
    def server_data(self, data):
        if data['id'] not in self.db.list_collection_names():
            #init guild
            return
        self.cache[data['id']] = {
            "msgs":{},
            "member_count": data['member_count'],
            "since": data['joined_at'],
            "voice": {},
            "channels":[],
            "reactions": self.db[data['id']]['reactions'],
            "roles": self.db[data['id']]['roles'],
            "disabled_channels": self.db[data['id']]['disabled']['channels'],
            "disabled_roles": self.db[data['id']]['disabled']['roles'],
            "muted": self.db[data['id']]['muted'],
            "groups":self.db[data['id']]['groups'],
            "responses":self.db[data['id']]['CustomResponses'],
            "logging":self.db[data['id']]['logging']
        }
    def voice(self, data):
        if data['user_id'] not in self.cache[data['id']]['voice']:
            self.cache[data['id']]['voice'][data['user_id']] = time.time()
        return
    def cachedVoice(self, data):
        join = self.cache[data['id']]['voice'].pop(data['user_id'],None)
        now = time.time()
        if join != None:
            return now-join
        return 0
    def cachedRoles(self, guild, roles):
        return 5

import pymongo

class Database:
    def __init__(self, database):
        self.client = pymongo.MongoClient("raspberry")
        self.db = self.client[database]
