from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS 
import datetime

class Influx:
    __slots__ = ('influx', 'write_api', 'query_api')
    def __init__(self):
        self.influx = InfluxDBClient.from_config_file("data/secrets.ini")
        self.write_api = self.influx.write_api(write_options=SYNCHRONOUS)
        self.query_api = self.influx.query_api()

    async def influxMember(self, serverID, userID, joined_or_left, timestamp=datetime.datetime.now()):
        self.write_api.write(bucket="Members", record=(
            Point("MemberChange")
            .tag("server", serverID)
            .tag("user", userID)
            .field("change", joined_or_left))
        )

    async def influxMembers(self, serverID, users: tuple):
        """Users = [(UserID, timestamp)]"""
        for user in users:
            await self.influxMember(serverID, user[0], True)

    async def influxGetMember(self, server):
        return self.query_api.query_data_frame(f'from(bucket:"MemberChange") |> filter(server={server})')

    def commitVoiceSession(self, server, channel, user, delta, timestamp=datetime.datetime.now().isoformat()):
        self.write_api.write(bucket="Sessions", record=(
            Point("VoiceSession")
            .tag("server", server)
            .tag("channel", channel)
            .tag("user", user)
            .field("session", delta)
        ))
    def commitPresence(self, server, user, game, delta, timestamp=datetime.datetime.now().isoformat()):
        self.write_api.write(bucket="Sessions", record=(
            Point("GamePresence")
            .tag("server", server)
            .tag("game", game)
            .tag("user", user)
            .field("session", delta)
        ))
    def getSession(self, user, interval):
        return self.query_api.query_data_frame(f'from(bucket:"Sessions/VoiceSession") |> filter(user={user}')

    async def influxPing(self):
        return self.influx.health()

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .alchemy import Base

class SQL:
    __slots__ = ('engine', 'Session')
    def __init__(self, db, user, password, location, port, name, echo):
        #self.engine = create_engine("sqlite:///mbot.db", echo=False)#f'{db}://{user}:{password}@{location}:{port}/{name}', echo={echo})
        #self.engine = create_engine("postgresql://postgres:postgres@r4:5432/mbot")
        self.engine = create_engine(f'{db}://{user}:{password}@{location}:{port}/{name}', echo=echo)
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
    def delete(self, mapping):
        s = self.session()
        s.delete(mapping)
        return s.commit()


class Database:
    def __init__(self, config):
        sql = config['Database']
        self.sql = SQL(sql['db'], sql['user'], sql['password'], sql['location'], sql['port'], sql['name'], sql['echo'])
        self.influx = Influx()


'''
Author | Title | Year | Lyrics | Notes
Author | Title | Year | Type   | Read Date | Notes
Title | Year | Watched | Notes
Title | Years | Seasons | Last Episode | Watched Date | Next Episode | Notes
Developer | Title | Year | Achievements | Played Date | Notes
Author | Quote | Notes

Author | Title | Year | Type | Notes | Data | Date
'''