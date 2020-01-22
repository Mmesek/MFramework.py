import pymongo
from influxdb import InfluxDBClient
import sqlite3 as sql3

class Database:
    def __init__(self, databaseLocation, databaseName):
        self.client = pymongo.MongoClient(databaseLocation)
        self.db = self.client[databaseName]
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
    async def mongoPing(self):
        return self.db.command('ping')
    #SQL
    async def access(self, query, params):
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
