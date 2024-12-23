import datetime

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from mlib.database import AsyncSQL
from mlib.rest_client import Client

from MFramework import log


class InfluxBase:
    def __init__(self, cfg: dict = None) -> None:
        pass

    def point(self, measurement_name, *args, **kwargs):
        pass

    async def influxMember(self, *args, **kwargs):
        pass

    async def influxMembers(self, serverID, users: tuple, *args, **kwargs):
        pass

    def getMembersChange(self, server_id, period: str, state: str = "joined", *args, **kwargs):
        pass

    async def influxGetMember(self, server, *args, **kwargs):
        pass

    def commitVoiceSession(
        self, server, channel, user, delta, timestamp=datetime.datetime.now().isoformat(), *args, **kwargs
    ):
        pass

    def commitPresence(self, server, user, game, delta, timestamp=datetime.datetime.now().isoformat(), *args, **kwargs):
        pass

    def commitMessage(self, server, channel, user, words, *args, **kwargs):
        pass

    def commitCommandUsage(self, server_id, command_name, bot_name, success=True, user_id=0, *args, **kwargs):
        pass

    def getSession(self, user, interval, *args, **kwargs):
        pass

    def getMessages(self, user, *args, **kwargs):
        pass

    def get(self, query, *args, **kwargs):
        pass

    def get_server(self, limit, interval, guild_id, measurement, fn="count", additional="", *args, **kwargs):
        pass

    def get_command_usage(self, guild_id, interval="30d", *args, **kwargs):
        pass

    async def influxPing(self, *args, **kwargs):
        return False


class Influx(InfluxBase):
    __slots__ = ("influx", "write_api", "query_api")

    def __init__(self, cfg: dict):
        self.influx = InfluxDBClient(cfg.get("url", None), cfg.get("token", None), org=cfg.get("org", None))
        self.write_api = self.influx.write_api(write_options=SYNCHRONOUS)
        self.query_api = self.influx.query_api()

    def point(self, measurement_name):
        return Point(measurement_name)

    async def influxMember(self, serverID, userID, joined_or_left, timestamp=datetime.datetime.now()):
        self.write_api.write(
            bucket="MFramework",
            record=(
                Point("MemberChange").tag("server", serverID).field("user", userID).field("change", joined_or_left)
            ),
        )

    async def influxMembers(self, serverID, users: tuple):
        """Users = [(UserID, timestamp)]"""
        for user in users:
            await self.influxMember(serverID, user[0], True)

    def getMembersChange(self, server_id, period: str, state: str = "joined"):
        return self.get(
            f"""
  |> range(start: -{period})
  |> filter(fn: (r) => r["_measurement"] == "MemberChange")
  |> filter(fn: (r) => r["server"] == "{server_id}")
  |> filter(fn: (r) => r["_value"] == {"true" if state == "joined" else "false"})
  |> aggregateWindow(every: 90d, fn: count)
  |> last()
  |> yield(name: "{state}")"""
        )

    async def influxGetMember(self, server):
        return self.query_api.query_data_frame(f'from(bucket:"MemberChange") |> filter(server={server})')

    def commitVoiceSession(
        self,
        server,
        channel,
        user,
        delta,
        timestamp=datetime.datetime.now().isoformat(),
    ):
        self.write_api.write(
            bucket="MFramework",
            record=(
                Point("VoiceSession")
                .tag("server", server)
                .tag("channel", channel)
                .tag("user", user)
                .field("session", delta)
            ),
        )

    def commitPresence(self, server, user, game, delta, timestamp=datetime.datetime.now().isoformat()):
        self.write_api.write(
            bucket="MFramework",
            record=(
                Point("GamePresence").tag("server", server).tag("game", game).tag("user", user).field("session", delta)
            ),
        )

    def commitMessage(self, server, channel, user, words):
        self.write_api.write(
            bucket="MFramework",
            record=(
                Point("MessageActivity")
                .tag("server", server)
                .tag("channel", channel)
                .tag("user", user)
                .field("words", words)
            ),
        )

    def commitCommandUsage(self, server_id, command_name, bot_name, success=True, user_id=0, locale=None):
        self.write_api.write(
            bucket="MFramework",
            record=(
                Point("Commands")
                .tag("server", server_id)
                .tag("command", command_name)
                .tag("bot", bot_name)
                .tag("locale", locale)
                .field("success", success)
                .field("user", user_id)
            ),
        )

    def getSession(self, user, interval):
        return self.query_api.query_data_frame(f'from(bucket:"Sessions/VoiceSession") |> filter(user={user})')

    def getMessages(self, user):
        return self.query_api.query_data_frame(f'from(bucket:"Sessions/MessageActivity") |> filter(user={user})')

    def get(self, query):
        return self.query_api.query('from(bucket:"MFramework")' + query)

    def get_server(self, limit, interval, guild_id, measurement, fn="count", additional=""):
        return self.get(
            f'|> range(start: -{interval})\
|> filter(fn: (r) => r["_measurement"] == "{measurement}")\
|> filter(fn: (r) => r["server"] == "{guild_id}")\
|> group(columns: ["user"], mode:"by")\
|> aggregateWindow(every: {interval}, fn: {fn})\
|> sum()\
|> group()\
|> top(columns: ["_value"], n: {limit})'
            + additional
        )

    def get_command_usage(self, guild_id, interval="30d"):
        return self.get(
            f"""
  |> range(start: -32d)
  |> filter(fn: (r) => r["_measurement"] == "Commands")
  |> filter(fn: (r) => r["server"] == "{guild_id}")
  |> filter(fn: (r) => r["_field"] == "user")
  |> map(fn: (r)=> ({'{r with user: r["_value"]}'}))
  |> group(columns: ["user"])
  |> aggregateWindow(every: {interval}, fn: count, createEmpty: false, column: "_value")
  |> yield(name: "count")"""
        )

    async def influxPing(self):
        return self.influx.health()


class Supabase(Client):
    async def rpc(self, func: str, method: str = "POST", **kwargs):
        return await self.api_call(path="rest/v1/rpc/" + func, method=method, **kwargs)

    async def increase_exp(self, server_id: int, user_id: int, value: float = 1) -> float:
        return await self.rpc(func="incrExp", server_id=server_id, user_id=user_id, value=value)


class Database:
    def __init__(self, config: dict):
        self.sql = AsyncSQL(**config.get("Database", {}))
        if "influx2" in config:
            self.influx = Influx(config["influx2"])
        else:
            self.influx = InfluxBase()
            log.info("Influx config not specified, skipping")
        if "Supabase" in config:
            self.supabase = Supabase(config["Supabase"])
        else:
            log.info("Supabase config not specified, skipping")
