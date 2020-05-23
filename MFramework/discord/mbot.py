import asyncio, time
import json, zlib
import aiohttp
import sys, traceback, platform
from .endpoints import Endpoints
from .mixins import EndpointWrappers
from ..database import database as db

from ..commands import Invalid
from ..utils.config import cfg as config
from .dispatch import message_type, Dispatch

def onDispatch(obj):
    def inner(f, *arg, **kwarg):
        message_type[f"{f.__name__}"] = (f, obj)

        def inn(*ar, **kwar):
            r = f(*ar, **kwar)
            return r

        return inn

    return inner

class Opcodes:
    async def dispatch(self, data):
        try:
            await getattr(Dispatch, data["t"].lower(), Invalid)(self, data['d'])
        except TypeError as ex:
            error = ''
            t = traceback.extract_tb(sys.exc_info()[2], limit=-1)
            if 'missing' in str(ex):
                error = str(ex).split(' ', 1)[1]
                err = f'{sys.exc_info()}'
                print(error)
                #await self.message(data['d']['channel_id'], error.capitalize())
            else:
                print('Error occured:', ex)
                print(sys.exc_info())
                print(t)
        except Exception as ex:
            t = traceback.extract_tb(sys.exc_info()[2], limit=-1)
            print(f"Message Create Error: {type(ex)}: {ex} at {t}")
        return

    async def reconnect(self, data):
        print("Reconnect", self.username)
        await self.resume(data)

    async def invalid_session(self, data):
        print("Invalid Session")
        print(data)
        if data["d"]:
            print('Resuming')
            await self.resume(data)
        else:
            print('Reidentifying')
            await self.identify()

    async def hello(self, data):
        self.heartbeating = asyncio.create_task(self.heartbeat(data["d"]["heartbeat_interval"]))#, name="Heartbeat")
        await self.identify()

    async def heartbeat_ack(self, data):
        self.latency = time.perf_counter() - self.heartbeat_sent


class Bot(EndpointWrappers, Endpoints):
    __slots__ = ('token', 'startTime', 'patterns', 'session_id', 'user_id', 'keepConnection', 'state', 'stayConnected', 'alias', 'presence', 'sub', 'presenceType', 'shards', 'db', 'cache', 'csession', 'ws',
    'last_sequence', 'heartbeating', 'username', 'lock', 'latency', 'heartbeat_sent', 'servers', '_zlib', '_buffer', 'chords', 'primary_guild', 'url', 'intents', 'errorchannel')
    opcodes = {
        0: Opcodes.dispatch,
        7: Opcodes.reconnect,
        9: Opcodes.invalid_session,
        10: Opcodes.hello,
        11: Opcodes.heartbeat_ack,
    }
    def __init__(self, token=config["Tokens"]["discord"], shard=0, total_shards=1, servers={}):
        self.token = config['DiscordTokens'][token]
        self.username = '[NOT CONNTECTED] '+ token
        self.keepConnection = True
        self.state = True
        self.stayConnected = True
        self.latency = None
        self.url = config['Discord']['url']
        self.alias = config['Discord']['alias']
        self.presence = config["Discord"]["presence"]
        self.sub = config["Discord"]["subscription"]
        self.presenceType = config["Discord"]["presence_type"]
        self.status = config["Discord"]["status"]
        if token in config:
            c = config[token]
            if 'status' in c:
                self.status = c['status']
            if 'presence' in c:
                self.presence = c['presence']
            if 'presence_type' in c:
                self.presenceType = c['presence_type']
            if 'alias' in c:
                self.alias = c['alias']
            if 'primary_guild' in c:
                self.primary_guild = c['primary_guild']
            if 'intents' in c:
                self.intents = c['intents']
            if 'log_dm' in c:
                self.errorchannel = c['log_dm']
        self.shards = [shard, total_shards]
        self.db = db.Database(config)
        self.db.sql.create_tables()
        self.cache = {"dm": {}}
        self.servers = servers
        self.emoji = config['Emoji']
        self.lock = {"global": False}
        self._buffer = bytearray()
        self._zlib = zlib.decompressobj()
        print("\nInitating Bot with token: ", self.token)

    async def _api_call(self, path, method="GET", reason="", **kwargs):
        if "file" in kwargs:
            data = aiohttp.FormData()
            data.add_field("payload_json", json.dumps(kwargs["json"]))
            data.add_field(
                "file", kwargs["file"][1], filename=kwargs["file"][0], content_type="application/octet-stream"
            )
            return await self.csession.post(
                url="https://discordapp.com/api" + path, data=data, headers=[("Authorization", f"Bot {self.token}")]
            )
        defaults = {
            "headers": {
                "Authorization": f"Bot {self.token}",
                "Content-Type": "application/json",
                "X-Audit-Log-Reason": f"{reason}",
            }
        }
        kwargs = dict(defaults, **kwargs)
        return await self.csession.request(method, "https://discordapp.com/api" + path, **kwargs)


    async def api_call(self, path, method='GET', reason='', **kwargs):
        try:
            bucket = path.split('/', 3)[2]
        except:
            bucket = None
        if bucket not in self.lock or self.lock[bucket] is not True and self.lock['global'] is False:
            res = await self._api_call(path, method, reason, **kwargs)
            try:
                r = await res.json()
            except:
                if res.reason == 'No Content':
                    return None
                print('Error sending request: ', res.reason)
            if 'retry_after' in r:
                if r['global'] is True:
                    self.lock['global'] = True
                else:
                    self.lock[bucket] = True
                await asyncio.sleep(r['retry_after'] / 1000)
                if r['global'] is True:
                    self.lock['global'] = False
                else:
                    self.lock[bucket] = False
                return await self.api_call(path, method, reason, **kwargs)
            elif 'message' in r:
                print(f"[{res.reason}] [{r['code']}] - {r['message']}: [{method}] {path}")
                return []
            else:
                return r
        else:
            if 'reaction' in path: #Ratelimit information for them is longer/inconsitent; Still hits 429 hence additional sleep
                await asyncio.sleep(0.5)
            await asyncio.sleep(0.75)
            return await self.api_call(path, method, reason, **kwargs)

    async def connection(self):
        self._buffer = bytearray()
        self._zlib = zlib.decompressobj()
        self.state = True
        self.csession = aiohttp.ClientSession()
        gate = await self.get_gateway_bot()
        self.ws = await self.csession.ws_connect(f"{gate['url']}?v=6&encoding=json&compress=zlib-stream")

    async def decompress(self, msg):
        if type(msg) is bytes:
            #print('Decompressing!')
            self._buffer.extend(msg)
            if len(msg) >= 4:
                if msg[-4:] == b'\x00\x00\xff\xff':
                    #print('Seems legit!')
                    msg = self._zlib.decompress(self._buffer).decode('utf-8')
                    self._buffer = bytearray()
                else:
                    return
            else:
                return
        #print('Hey! We are past decompressing!')
        msg = json.loads(msg)
        return msg

    async def msg(self):
        async for msg in self.ws:
            try:
                data = await self.decompress(msg.data)
                #data = json.loads(msg.data)
                if data is not None:
                    if data["op"] != 11 and data["s"] is not None:
                        self.last_sequence = data["s"]
                    asyncio.create_task(self.opcodes.get(data["op"], Invalid)(self, data))#, name="Dispatch")
            except Exception as ex:
                print(f"Exception! {ex}\nType: {msg.type}\nData: {msg.data}\nExtra: {msg.extra}")
        #await self.close()

    async def heartbeat(self, interval):
        self.keepConnection = True
        while self.keepConnection:
            await asyncio.sleep(interval / 1000)
            self.heartbeat_sent = time.perf_counter()
            await self.ws.send_json({"op": 1, "d": self.last_sequence})

    async def close(self):
        if self.username:
            print("Closing:", self.username)
        else:
            print("Closing...")
        self.keepConnection = False
        self.heartbeating.cancel()
        await self.ws.close()
        await self.csession.close()
        self.state = False
        print('Closed')

    # User
    async def identify(self):
        # https://ziad87.net/intents/
        print("Identifing")
        await self.ws.send_json(
            {
                "op": 2,
                "d": {
                    "token": self.token,
                    "properties": {
                        "$os": platform.system(),
                        "$browser": "MFramework",
                        "$device": "MFramework"
                    },
                    "compress": True,
                    "large_threshold": 250,
                    "guild_subscriptions": self.sub,
                    "shard": self.shards,
                    "presence": {
                        "game": {
                            "name": self.presence,
                            "type": self.presenceType,
                            #"url": self.url
                        },
                        "status": self.status,
                        "since": time.time(),
                        "afk": False
                    },
                    "intents": self.intents
                },
            }
        )

    async def resume(self, data):
        print("Resuming, yes?")
        await self.ws.send_json(
            {"op": 6, "d": {"token": self.token, "session_id": self.session_id, "seq": self.last_sequence}}
        )

    async def request_guild_members(self, guild_id, query="", limit=0, presences=False, user_ids=None):
        await self.ws.send_json({"op": 8, "d": {"guild_id": guild_id, "query": query, "limit": limit, "presences":presences}})

    async def voice_state_update(self, guild_id, channel_id, mute=False, deaf=True):
        print("Updating Voice State", guild_id, channel_id, mute, deaf)
        await self.ws.send_json(
            {
                "op": 4,
                "d": {
                    "guild_id": guild_id,
                    "channel_id": channel_id,
                    "selt_mute": mute,
                    "self_deaf": deaf,
                },
            }
        )

    async def status_update(self, status="Online", status_name="How the World Burns", status_type=3, afk=False, url=""):
        """Status type: 0 - Playing, 1 - Streaming, 2 - Listening, 3 - Watching"""
        print(status, status_name, status_type)
        await self.ws.send_json(
            {
                "op": 3, 
                "d": {
                    "since": time.time(),
                    "game": {
                        "name": status_name.strip(), 
                        "type": int(status_type),
                        "url": url
                    }, 
                    "status": status.strip().lower(), 
                    "afk": afk
                }
            }
        )
    