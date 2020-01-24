#Servers: 
# GuildID | AdminID | ModID | VipID | NitroID | MutedID | LogFlags? | LogWebhook? | NoExpRoles | NoExpChannels
#ServersRegex:
# GuildID | Trigger | Response | Group
#ReactionRoles:
# GuildID | ChannelID | MessageID | RoleID | Reaction | RoleGroup
#LevelRoles:
# GuildID | Level | Role | Stacked
#UserLevels:
# GuildID | UserID | EXP | vEXP | LastMessage
#Infractions:
# GuildID | UserID | Timestamp | Reason | ModeratorID | Duration | InfractionType
#Webhooks:
# GuildID | Webhook | Source | Content | AddedBy
#RSS:
# Source | Last | URL | Color
#Spotify:
# Artist | AddedBy
#Giveaways:
# GuildID | ChannelID | MessageID | UserID | Timestamp | Duration | WinnerCount
#EmbedTemplates:
# GuildID | UserID | Name | Message | Title | Description | URL | Footer | Color | Image | Timestamp | Trigger
#Games:
# UserID | Title | LastPlayed
#PickUps:
# GuildID | ChannelID | Name | RequiredPlayers | Maps | Playcount

#GuildID {
#   Roles{
#       group:[roles]},
#   Log{
#       settings:{
#           action:bool},
#       webhooks:{
#           action:webhook}},
#   Responses{
#       group:{
#           trigger:response}},
#   Users{
#       UserID:{
#           exp:int,
#           vexp:int}},
#   Infractions{
#       UserID:{
#           Timestamp:{
#               Reason:'',
#               From:uid,
#               Duration:int,
#               infractiontype:''
#}}}}


#import pymongo
from influxdb import InfluxDBClient
import sqlite3 as sql3

class Database:
    def __init__(self, databaseLocation, databaseName):
#        self.client = pymongo.MongoClient(databaseLocation)
#        self.db = self.client[databaseName]
        self.influx = InfluxDBClient(host='rpi4',database='MFrameworkMemberChanges')
        self.sql = sql3.connect('bot/data/Mbot.db')
    #Influx
    async def influxMember(self, serverID, userID, joined_or_left, timestamp=''):
        self.influx.write_points([{
            "measurement":"MemberChange",
            "tags":{
                "server":serverID,
                "user":userID
            },
            "time":timestamp,
            "fields":{
                "change":joined_or_left
        }}])
    async def influxMembers(self, serverID, users: tuple):
        '''Users = [(UserID, timestamp)]'''
        jsons = []
        for user in users:
            jsons+=[{
                "measurement":"MemberChange",
                "tags":{
                    "server":serverID,
                    "user":user[0]
                },
                "time":user[1],
                "fields":{
                    "change":True}}]
        self.influx.write_points(jsons)
    async def influxGetMember(self, server):
        return self.influx.query('select change from MemberChange where server=$server;',bind_params={'server':server})
    async def influxPing(self):
        return self.influx.ping()
    #Mongo
#    async def mongoPing(self):
#        return self.db.command('ping')
    #SQL
    async def access(self, query, params=[]):
        print(query, params)
        with self.sql:
            self.a = self.sql.cursor()
            self.a.execute(query, params)
    async def single(self):
        return self.a.fetchone()
    async def all(self):
        return self.a.fetchall()
    async def selectOne(self, table: str, column: str, query: str='', params: list=[]):
        '''TableName\nselectColumn\nWHERE whereColumn=? AND.. {ORDER BY columnName}\n(isVariable)'''
        await self.access(f'SELECT {column} FROM {table} {query}',params)
        return await self.single()
    async def selectMultiple(self, table: str, column: str, query: str='', params: list=[]):
        '''TableName\nselectColumn\nWHERE whereColumn=? AND.. {ORDER BY columnName}\n(isVariable)'''
        await self.access(f'SELECT {column} FROM {table} {query}',params)
        return await self.all()
    async def insert(self, table: str, columns: str, params: list=[], query: str='',):
        '''TableName\nto,Columns..\n(Variable,s..)'''
        v = ','.join(['?' for i in columns.split(',')])
        return await self.access(f'INSERT INTO {table}({columns}) VALUES ({v}) {query}',params)
    async def update(self, table: str, query: str, params: list=[]):
        '''TableName\ncolumn=? AND.. WHERE whereColumn=? AND..\n(columnValues)'''
        return await self.access(f'UPDATE {table} SET {query}',params)
    async def delete(self, table: str, column: str, params: list=[], query: str=''):
        '''TableName\nwhereColumn\n(isVariable)\nAND..'''
        return await self.access(f'DELETE FROM {table} WHERE {column}=? {query}',params)
    async def createTables(self):
        await self.access('SELECT EXISTS(SELECT name FROM sqlite_master WHERE type="table")')
        if await self.single() == (1,):
            return
        await self.access('CREATE TABLE `Servers`(GuildID INT, AdminIDs BLOB, ModIDs BLOB, VipIDs BLOB, NitroIDs BLOB, MutedIDs BLOB, NoExpRoles BLOB, NoExpChannels BLOB)')
        await self.access('CREATE TABLE `Regex`(GuildID INT, Trigger TEXT, Response TEXT, ReqRole TEXT)')
        await self.access('CREATE TABLE `ReactionRoles`(GuildID INT, ChannelID INT, MessageID INT, RoleID INT, Reaction TEXT, RoleGroup TEXT)')
        await self.access('CREATE TABLE `LevelRoles`(GuildID INT, Level INT, Role INT, Stacked BOOL)')
        await self.access('CREATE TABLE `UserLevels`(GuildID INT, UserID INT, EXP INT, vEXP INT, LastMessage INT)')
        await self.access('CREATE TABLE `Infractions`(GuildID INT, UserID INT, Timestamp INT, Reason TEXT, ModeratorID INT, Duration INT, InfractionType TEXT)')
        await self.access('CREATE TABLE `Webhooks`(GuildID INT, Webhook TEXT, Source TEXT, Content TEXT, AddedBy INT)')
        await self.access('CREATE TABLE `RSS`(Source TEXT, Last INT, URL TEXT, Color INT)')
        await self.access('CREATE TABLE `Spotify`(Artist TEXT, AddedBy INT)')
        await self.access('CREATE TABLE `Giveaways`(GuildID INT, ChannelID INT, MessageID INT, UserID INT, Timestamp INT, Duration INT, WinnerCount INT)')
        await self.access('CREATE TABLE `EmbedTemplates`(GuildID INT, UserID INT, Name TEXT, Message TEXT, Embed BLOB, Trigger TEXT)')
        await self.access('CREATE TABLE `Games`(UserID INT, Title TEXT, LastPlayed INT)')

    async def checkExistence(self, table: str, column: str, params: list=[]):
        await self.access(f'SELECT EXISTS(SELECT ? FROM {table} WHERE {column}=?)',params)
        return await self.single()
    async def checkExistenceAndReturn(self, table: str, column: str, params: list=[]):
        await self.access(f'SELECT ? FROM {table} WHERE {column}=?',params)
        return await self.all()
