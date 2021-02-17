# -*- coding: utf-8 -*-
'''
API Client
----------

Discord API Client.

:copyright: (c) 2021 Mmesek

'''

import asyncio, aiohttp
import ujson as json
from . import objects as discord
from . import Deserializer
from .exceptions import *
class Client(discord.Endpoints):
    def __init__(self, name: str, cfg: dict, db: object, cache: object, shard: int = 0, total_shards: int = 1):
        self.token = cfg['DiscordTokens'][name]
        self.username = '[NOT CONNTECTED] ' + self.token
        self.counters = {"EXECUTED_COMMANDS": 0}
        
        self.db = db
        self.cache = cache
        self.context = {"dm": {}}

        self.latency = None
        
        self.cfg = cfg

        self.alias = cfg[name]['alias']
        self.sub = cfg[name].get('subscription', False) #True
        self.presence = cfg[name]['presence'] #"How the world burns"
        self.presenceType = cfg[name]['presence_type'] #Activity_Types.WATCHING.value
        self.status = cfg[name]['status'] #Status_Types.ONLINE.value
        self.intents = cfg[name]['intents'] #14271 # https://ziad87.net/intents/
        self.url = None
        
        self.shards = [shard, total_shards]
        self.lock = {"global": False}

        self.decompress = Deserializer()
        
        print("\nInitating Bot with token: ", self.token)

    async def _api_call(self, path: str, method: str = "GET", reason: str = None, **kwargs):
        headers = [("Authorization", f"Bot {self.token}")]
        if reason:
            headers.append(("X-Audit-Log-Reason", reason))
        if kwargs.get('json'):
            kwargs['json'] = discord.as_dict(kwargs['json'])
        if kwargs.get('params'):
            for param in kwargs["params"]:
                kwargs["params"][param] = str(kwargs["params"][param])
        #TODO: kwargs to json #I think it's handled now?
        if not kwargs.get('filename'):
            headers.append(("Content-Type", "application/json"))
            data = None
        else:
            data = aiohttp.FormData()
            data.add_field("payload_json", json.dumps(kwargs["json"]))
            data.add_field("file", kwargs["file"],
                filename=kwargs["filename"],
                content_type="application/octet-stream"
            )
            kwargs.pop('json')
        kwargs.pop('filename', None)
        kwargs.pop('file', None)
        return await self._client_session.request(
            method, discord.BASE_URL + path,
            data=data, headers=headers, 
            **kwargs)

    async def api_call(self, path: str, method: str = "GET", reason: str = None, **kwargs):
        try:
            bucket = path.split('/', 3)[2]
        except:
            bucket = None

        if self.lock.get(bucket, False) is False and self.lock.get('global') is False:
            res = await self._api_call(path, method, reason, **kwargs)
            try:
                r = await res.json()
            except:
                if res.reason == 'No Content':
                    return None
                raise RequestError(f"Error sending request: {res.reason}")

            if 'retry_after' in r:

                #FIXME: Old version below
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
                #TODO: Handle ratelimits!

                return

            elif 'message' in r:
                if res.status >= 500:
                    await asyncio.sleep(1)
                    return await self.api_call(path, method, reason, **kwargs)
                raise JsonBadRequest(f"[{res.reason}] [{r['code']}] - {r['message']}: [{method}] {path}", r.get('errors','') if 'errors' in r else None)
            elif res.reason == 'Bad Request':
                raise BadRequest(f"[{res.reason}] {await res.text()}", f"[{method}] {path}")
            else:
                if type(r) is dict:
                    return dict({"_Client": self}, **r)
                return list(dict({"_Client":self}, **i) for i in r)

        elif 'reaction' in path:
            # Ratelimit information for them is longer/inconsitent
            # Still hits 429 hence additional sleep
            await asyncio.sleep(0.5)
        await asyncio.sleep(0.75)
        return await self.api_call(path, method, reason, **kwargs)

    async def __aenter__(self):
        self.decompress = Deserializer()

        import platform
        if 'linux' in platform.system().lower():
            from aiohttp.resolver import AsyncResolver
            resolver = AsyncResolver(nameservers=['8.8.8.8', '8.8.4.4'])
        else:
            resolver = None
        
        self._client_session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False, resolver=resolver))#, json_serialize=Encoder().encode)
        gate = await self.get_gateway_bot()
        self._ws = await self._client_session.ws_connect(f"{gate['url']}?v={self.cfg['Discord']['api_version']}&encoding=json&compress=zlib-stream",)
        return self

    async def receive(self):
        async for msg in self._ws:
            try:
                data = self.decompress(msg.data)
                if data is not None:
                    if data.op != 11 and data.s is not None:
                        self.last_sequence = data.s
                    from .opcodes import opcodes
                    from . import Invalid
                    asyncio.create_task(opcodes.get(data.op, Invalid)(self, data))#, name="Dispatch")
            except Exception as ex:
                print(f"Exception! {ex}\nType: {msg.type}\nData: {msg.data}\nExtra: {msg.extra}")

    async def send(self, _json: object):
        _json = discord.as_dict(_json)
        #TODO: json (object) to json (dict) #done?
        return await self._ws.send_json(_json)

    async def __aexit__(self, *args, **kwargs):
        await asyncio.sleep(1)
        if hasattr(self, 'heartbeating'):
            self.heartbeating.cancel()
        await self._ws.close()
        await self._client_session.close()
