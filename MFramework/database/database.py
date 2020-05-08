from influxdb import InfluxDBClient
import datetime

class Influx:
    __slots__ = ('influx')
    def __init__(self, host, name):
        self.influx = InfluxDBClient(host=host, database=name)

    async def influxMember(self, serverID, userID, joined_or_left, timestamp=datetime.datetime.now()):
        self.influx.write_points(
            [
                {
                    "measurement": "MemberChange",
                    "tags": {"server": serverID, "user": userID},
                    "time": timestamp,
                    "fields": {"change": joined_or_left},
                }
            ]
        )

    async def influxMembers(self, serverID, users: tuple):
        """Users = [(UserID, timestamp)]"""
        jsons = []
        for user in users:
            jsons += [
                {
                    "measurement": "MemberChange",
                    "tags": {"server": serverID, "user": user[0]},
                    "time": user[1],
                    "fields": {"change": True},
                }
            ]
        self.influx.write_points(jsons)

    async def influxGetMember(self, server):
        return self.influx.query(
            "select change from MemberChange where server=$server;", bind_params={"server": server}
        )

    def commitVoiceSession(self, server, channel, user, delta, timestamp=datetime.datetime.now()):
        self.influx.write_points([{"measurement": "VoiceSession","tags":{"server": server, "channel": channel, "user": user},"time":timestamp, "fields": {"session":delta}}])

    async def influxPing(self):
        return self.influx.ping()

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .alchemy import Base

class SQL:
    __slots__ = ('engine', 'Session')
    def __init__(self, db, user, password, location, port, name, echo):
        #self.engine = create_engine("sqlite:///mbot.db", echo=False)#f'{db}://{user}:{password}@{location}:{port}/{name}', echo={echo})
        self.engine = create_engine("postgresql://postgres:postgres@raspberry:5432/mbot")
        self.Session = sessionmaker(bind=self.engine)
    def create_tables(self):
        Base.metadata.create_all(self.engine)
    def session(self):
        session = self.Session()
        return session
    def add(self, mapping):
        s = self.session()
        s.add(mapping)
        return s.commit()


class Database:
    def __init__(self, config):
        sql = config['Database']
        influx = config['Influx']
        self.sql = SQL(sql['db'], sql['user'], sql['password'], sql['location'], sql['port'], sql['name'], sql['echo'])
        self.influx = Influx(influx['host'],influx['db'])