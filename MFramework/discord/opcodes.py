# -*- coding: utf-8 -*-
'''
Discord Opcodes
----------

Discord API Opcodes.

:copyright: (c) 2020 Mmesek

'''
import asyncio, time
import sys, traceback, platform
from typing import List, Optional

from .objects import (
    Gateway_Events, 
    Gateway_Payload, 
    Gateway_Opcodes,
    Gateway_Status_Update,
    Gateway_Voice_State_Update,
    Identify, Resume,
    Guild_Request_Members,
    Snowflake,
    Status_Types, Activity_Types,
    Bot_Activity,
    Insufficient_Permissions
)
from .client import Client
from . import Dispatch, Invalid, aInvalid
from .exceptions import *
async def dispatch(self: Client, data: Gateway_Payload):
    data.d = getattr(Gateway_Events, data.t.title(), Invalid)(_Client=self, **data.d)
    if data.t not in self.counters:
        self.counters[data.t] = 0
    self.counters[data.t] += 1
    try:
        for function in Dispatch.get(data.t, [aInvalid]):
            await function(self, data.d)
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
    except JsonBadRequest as ex:
        print(ex)
    except Exception as ex:
        t = traceback.extract_tb(sys.exc_info()[2], limit=-1)
        print(f"Dispatch Error: {type(ex)}: {ex} at {t}")
    return

async def reconnect(self: Client, data: dict):
    print("Reconnect", self.username)
    await resume(self, data)

async def invalid_session(self: Client, data: dict):
    print("Invalid Session")
    print(data)
    if data.d:
        print('Resuming')
        await resume(self, data)
    else:
        print('Reidentifying')
        await identify(self)

async def hello(self: Client, data: dict):
    self.heartbeating = asyncio.create_task(heartbeat(self, data.d["heartbeat_interval"]))#, name="Heartbeat")
    await identify(self)

async def heartbeat_ack(self: Client, data: dict):
    self.latency = time.perf_counter() - self.heartbeat_sent

# User
async def identify(self: Client):
    print("Identifing")
    await self.send(Gateway_Payload(
        op= Gateway_Opcodes.IDENTIFY,
        d= Identify(
            token=self.token,
            properties={
                "$os": platform.system(),
                "$browser": "MFramework",
                "$device": "MFramework"},
            compress=True,
            large_threshold=250,
            guild_subscriptions=self.sub,
            shard=self.shards,
            presence= Gateway_Status_Update(
                since= time.time(),
                activities=[Bot_Activity(
                    name=self.presence,
                    type=self.presenceType,
                    url=self.url
                    )],
                status= self.status,
                afk= False),
            intents= self.intents
            )
        )
    )
    return

async def heartbeat(self: Client, interval: int):
    self.keepConnection = True
    while self.keepConnection:
        await asyncio.sleep(interval / 1000)
        self.heartbeat_sent = time.perf_counter()
        await self._ws.send_json({"op": 1, "d": self.last_sequence})

async def resume(self: Client, data: dict):
    print("Resuming, yes?")
    await self.send(Gateway_Payload(
        Gateway_Opcodes.RESUME,
        Resume(
            token=self.token,
            session_id=self.session_id,
            seq= self.last_sequence
        )
    ))

async def request_guild_members(self: Client, guild_id: Snowflake, query: str = "", limit: int = 0, presences: bool = False, user_ids: List[Snowflake] = None):
    await self.send(Gateway_Payload(
        Gateway_Opcodes.REQUEST_GUILD_MEMBERS,
        Guild_Request_Members(
            guild_id=guild_id,
            query=query,
            limit=limit,
            presences=presences,
            user_ids=user_ids,
            nonce=None
        )
    ))

async def voice_state_update(self: Client, guild_id: Snowflake, channel_id: Snowflake, mute: bool = False, deaf: bool = True):
    await self.send(Gateway_Payload(
        Gateway_Opcodes.VOICE_STATE_UPDATE,
        Gateway_Voice_State_Update(
            guild_id=guild_id,
            channel_id=channel_id,
            self_mute=mute,
            self_deaf=deaf
        )
    ))

async def presence_update(self: Client, status: Status_Types = "Online", status_name: str = "How the World Burns", status_type: Activity_Types = Activity_Types.WATCHING, afk: bool = False, url: Optional[str] = None):
    """Status type: 0 - Playing, 1 - Streaming, 2 - Listening, 3 - Watching"""
    await self.send(Gateway_Payload(
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
    ))

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
