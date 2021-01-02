# -*- coding: utf-8 -*-
'''
API Client
----------

Discord API Client.

:copyright: (c) 2020 Mmesek

'''

import asyncio
import json, zlib
import aiohttp
import platform
from .opcodes import opcodes
from .objects import *
from . import Invalid

class Client:
    def __init__(self, name, cfg, db, cache, shard=0, total_shards=1):
        self.token = cfg['DiscordTokens'][name]
        self.username = '[NOT CONNTECTED] ' + self.token
        self.counters = {"EXECUTED_COMMANDS": 0}
        
        self.db = db
        self.cache = cache
        self.context = {"dm": {}}

        self.alias = cfg[name]['alias']

        self.keepConnection = True
        self.stayConnected = True

        self.connected = True
        self.latency = None
        
        self.sub = True
        self.presence = "How the world burns"
        self.presenceType = Activity_Types.WATCHING.value
        self.status = Status_Types.ONLINE.value
        self.intents = 14271
        
        self.shards = [shard, total_shards]
        self.lock = {"global": False}

        self._api_version = 8

        self._buffer = bytearray()
        self._zlib = zlib.decompressobj()
        
        print("\nInitating Bot with token: ", self.token)

    async def _api_call(self, path, method="GET", reason: str = None, **kwargs):
        if "file" in kwargs:
            data = aiohttp.FormData()
            data.add_field("payload_json", json.dumps(kwargs["json"]))
            data.add_field(
                "file", kwargs["file"], filename=kwargs["filename"], content_type="application/octet-stream"
            )
            return await self.csession.post(
                url=BASE_URL+f"/v{self._api_version}" + path, data=data, headers=[("Authorization", f"Bot {self.token}")]
            )
        defaults = {
            "headers": {
                "Authorization": f"Bot {self.token}",
                "Content-Type": "application/json"
            }
        }
        if reason != None:
            defaults["headers"]["X-Audit-Log-Reason"] = reason
        for kwarg in kwargs:
            if type(kwargs[kwarg]) == dict:
                kwargs[kwarg] = as_dict(kwargs[kwarg])
        if "params" in kwargs:
            for param in kwargs["params"]:
                kwargs["params"][param] = str(kwargs["params"][param])
                #for sub in kwargs[kwarg]:
                    #if is_dataclass(kwargs[kwarg][sub]):
                        #kwargs[kwarg][sub] = asdict(kwargs[kwarg][sub])
            #            kwargs[kwarg][sub] = json.loads(Encoder().encode(kwargs[kwarg][sub]))
        kwargs = dict(defaults, **kwargs)
        return await self.csession.request(method, BASE_URL + path, **kwargs)


    async def api_call(self, path, method='GET', reason=None, **kwargs):
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
                return print('Error sending request: ', res.reason)
            if 'retry_after' in r:
                if r['global'] is True:
                    self.lock['global'] = True
                else:
                    self.lock[bucket] = True
                if r['retry_after'] > 10:
                    await asyncio.sleep(r['retry_after'] / 1000)
                else:
                    await asyncio.sleep(r['retry_after'])
                if r['global'] is True:
                    self.lock['global'] = False
                else:
                    self.lock[bucket] = False
                return await self.api_call(path, method, reason, **kwargs)
            elif 'message' in r:
                print(f"[{res.reason}] [{r['code']}] - {r['message']}: [{method}] {path}")
                print(r.get('errors','')) if 'errors' in r else None
                return {}
            elif res.reason == 'Bad Request':
                print(f"[{res.reason}] {await res.text()}")
                print(f"[{method}] {path}")
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
        self.connected = True
        if 'linux' in platform.system().lower():
            from aiohttp.resolver import AsyncResolver
            resolver = AsyncResolver(nameservers=['8.8.8.8', '8.8.4.4'])
        else:
            resolver = None
        self.csession = aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False, resolver=resolver))#, json_serialize=Encoder().encode)
        gate = await get_gateway_bot(self)
        self.ws = await self.csession.ws_connect(f"{gate['url']}?v={self._api_version}&encoding=json&compress=zlib-stream")

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
                    asyncio.create_task(opcodes.get(data["op"], Invalid)(self, data))#, name="Dispatch")
            except Exception as ex:
                print(f"Exception! {ex}\nType: {msg.type}\nData: {msg.data}\nExtra: {msg.extra}")
        #await self.close()

    async def close(self):
        if self.username:
            print("Closing:", self.username)
        else:
            print("Closing...")
        self.keepConnection = False
        self.heartbeating.cancel()
        await self.ws.close()
        await self.csession.close()
        self.connected = False
        print('Closed')
