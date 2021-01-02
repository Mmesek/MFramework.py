# -*- coding: utf-8 -*-
'''
Discord Opcodes
----------

Discord API Opcodes.

:copyright: (c) 2020 Mmesek

'''
import asyncio, time
import sys, traceback, platform

from .objects import *
from . import Dispatch, Invalid, aInvalid

async def dispatch(self, data):
    data['d'] = getattr(Gateway_Events, data['t'].title(), Invalid)(**data['d'])
    if data['t'] not in self.counters:
        self.counters[data['t']] = 0
    self.counters[data['t']] += 1
    try:
        await Dispatch.get(data['t'], aInvalid)(self, data['d'])
    except Insufficient_Permissions as ex:
        print(ex)
    except TypeError as ex:
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
        print(f"Dispatch Error: {type(ex)}: {ex} at {t}")
    return

async def reconnect(self, data):
    print("Reconnect", self.username)
    await resume(self, data)

async def invalid_session(self, data):
    print("Invalid Session")
    print(data)
    if data["d"]:
        print('Resuming')
        await resume(self, data)
    else:
        print('Reidentifying')
        await identify(self)

async def hello(self, data):
    self.heartbeating = asyncio.create_task(heartbeat(self, data["d"]["heartbeat_interval"]))#, name="Heartbeat")
    await identify(self)

async def heartbeat_ack(self, data):
    self.latency = time.perf_counter() - self.heartbeat_sent

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

async def heartbeat(self, interval):
    self.keepConnection = True
    while self.keepConnection:
        await asyncio.sleep(interval / 1000)
        self.heartbeat_sent = time.perf_counter()
        await self.ws.send_json({"op": 1, "d": self.last_sequence})

async def resume(self, data):
    print("Resuming, yes?")
    await self.ws.send_json(as_dict(Gateway_Payload(
        Gateway_Opcodes.RESUME,
        Resume(
            token=self.token,
            session_id=self.session_id,
            seq= self.last_sequence
        )
    )))

async def request_guild_members(self, guild_id, query="", limit=0, presences=False, user_ids=None):
    await self.ws.send_json(as_dict(Gateway_Payload(
        Gateway_Opcodes.REQUEST_GUILD_MEMBERS,
        Guild_Request_Members(
            guild_id=guild_id,
            query=query,
            limit=limit,
            presences=presences,
            user_ids=user_ids,
            nonce=None
        )
    )))

async def voice_state_update(self, guild_id, channel_id, mute=False, deaf=True):
    await self.ws_send_json(as_dict(Gateway_Payload(
        Gateway_Opcodes.VOICE_STATE_UPDATE,
        Gateway_Voice_State_Update(
            guild_id=guild_id,
            channel_id=channel_id,
            self_mute=mute,
            self_deaf=deaf
        )
    )))

async def presence_update(self, status="Online", status_name="How the World Burns", status_type=Activity_Types.WATCHING, afk=False, url=None):
    """Status type: 0 - Playing, 1 - Streaming, 2 - Listening, 3 - Watching"""
    await self.ws.send_json(as_dict(Gateway_Payload(
        Gateway_Opcodes.PRESENCE_UPDATE,
        Gateway_Status_Update(
            time.time() if afk else None,
            [Bot_Activity(
                name=status_name.strip(),
                type=status_type,
                url=url)],
            status.strip().lower(),
            afk
        )
    )))

opcodes = {
    0: dispatch,
    1: heartbeat,
    2: identify,
    3: presence_update,
    4: voice_state_update,
    6: resume,
    7: reconnect,
    8: request_guild_members,
    9: invalid_session,
    10: hello,
    11: heartbeat_ack,
}
