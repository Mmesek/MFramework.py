import asyncio, json, aiohttp
import discord.endpoints as endpoints
import discord.db as db
async def Invalid(*args):
    #print(f"Invalid Package: {args[0]}")
    pass

mtypes={}

def onDispatch():
    def inner(f, *arg, **kwarg):
        global mtypes
        mtypes[f"{f.__name__.upper()}"] = f
        def inn(*ar, **kwar):
            r = f(*ar, **kwar)
            return r
        return inn
    return inner

import config

class Bot:
    def __init__(self):
        self.token = config.tokens['discord']
        self.session_id = 0
        self.user_id    = 0
        self.sequence   = 0
        self.keepConnection = True
        self.state = True
        self.stayConnected = True
        self.presence = "How the world burns."
        self.sub    = False
        self.presenceType = 3
        self.shards = None #[shard,total]
        self.db = db.Database('Mbot')
        self.cache = db.Cache(self.db)
        self.endpoints = endpoints.Endpoints(self.api_call)
        self.op = {
            0:self.dispatch,
            7:self.reconnect,
            9:self.invalid_session,
            10:self.hello,
            11:self.heartbeat_ack}
        self.message_type = mtypes
        print('Initating Bot with token: ',self.token)
    async def api_call(self, path, method="GET", **kwargs):
        if 'file' in kwargs:
            data = aiohttp.FormData()
            data.add_field('payload_json',json.dumps(kwargs['json']))
            data.add_field('file',kwargs['file'][1], filename=kwargs['file'][0],content_type='application/octet-stream')
            return await self.csession.post(url='https://discordapp.com/api'+path,data=data,headers=[('Authorization',f'Bot {self.token}')])
        defaults = {"headers":{"Authorization": f"Bot {self.token}", "Content-Type": "application/json"}}
        kwargs = dict(defaults, **kwargs)
        res = await self.csession.request(method, "https://discordapp.com/api"+path, **kwargs)
        try:
            return await res.json()
        except:
            return res.reason
    async def connection(self):
        self.state = True
        try:
            self.csession = aiohttp.ClientSession()
        except:
            print('Session Closed, Discord?')
            await self.close()
        gate = await self.api_call("/gateway")
        self.ws = await self.csession.ws_connect(f"{gate['url']}?v=6&encoding=json")
    async def msg(self):
#        msg = await self.ws.receive()
#        print('Type:',msg.type,'\nExtra: ',msg.extra)
#        data = json.loads(msg.data)
        try:
            data = await self.ws.receive_json()
        except:
            data = None
        return data
    async def heartbeat(self, interval):
        while self.keepConnection:
            await asyncio.sleep(interval/1000)
            await self.ws.send_json({"op":1, "d":self.sequence})
    async def close(self):
        print('Closing')
        self.heartbeating.cancel() #pylint: disable=no-member
        await self.ws.close()
        await self.csession.close()
        self.state = False
    async def opcode(self, data):
        if data == None:
            return
        if data['op'] != 11:
            self.last_sequence = data['s']
        return await self.op.get(data['op'], Invalid)(data)
    async def dispatch(self, data):
        if data['t'] == 'MESSAGE_CREATE':
            await self.message_type[data['t']](self, data['d'])
        elif data['t'] != 'PRESENCE_UPDATE':
            try:
                asyncio.create_task(self.message_type.get(data['t'], Invalid)(self, data['d']))
            except Exception as ex:
                print('Dispatch Error:', ex)
        elif data['t'] == 'PRESENCE_UPDATE':
            pass
            await self.message_type[data['t']](self, data['d'])
        return
    ###User
    async def identify(self):
        print('Identifing')
        await self.ws.send_json({
            "op": 2,
            "d":{
            "token": self.token,
            "properties":{},
            "compress":False,
            "large_threshold":250,
            "presence":{
                "game":{
                    "name":self.presence,
                    "type":self.presenceType},
            "guild_subscriptions":self.sub,
            "shard":self.shards,
            }}})
        
    async def resume(self, data):
        print ("Resuming, yes?")
        await self.ws.send_json({
            "op":6,
            "d":{
            "token":self.token,
            "session_id":self.session_id,
            "seq":self.last_sequence}
        })
    async def request_guild_members(self, data):
        await self.ws.send_json({
            "op":8,
            "d":{
                "guild_id":data['d']['guild_id'],
            "query":"",
            "limit":0}
    })
    async def voice_state_update(self, data, channel_id, mute=False, deaf=True):
        print('Updating Voice State',data, channel_id, mute, deaf)
        await self.ws.send_json({
            "op":4,
            "d":{
                "guild_id":data['d']['guild_id'],
                "channel_id":channel_id,
                "selt_mute":mute,
                "self_deaf":deaf}
        })
    async def status_update(self, data, status="Online", status_name="How the World Burns", status_type=3):
        '''Status type: 0 - Playing, 1 - Streaming, 2 - Listening, 3 - Watching'''
        await self.ws.send_json({
            "op":3,
            "d":{
                "game":{
                    "name":status_name,
                    "type":status_type
                },
                "status":status,
                "afk":False
        }})
    ############

    async def reconnect(self, data):
        print('Reconnect')
        self.resume(data)
    async def invalid_session(self, data):
        print('Invalid Session')
        if data['d']:
            self.resume(data)
        else:
            self.identify()
    async def hello(self, data):
        self.heartbeating = asyncio.create_task(self.heartbeat(data['d']['heartbeat_interval']))
        await self.identify()
    async def heartbeat_ack(self, data):
        pass


def run():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.run_until_complete(asyncio.sleep(0))
    loop.close()


async def main():
    b = Bot()
    while b.stayConnected:
        await b.connection()
        while b.state:
            data = await b.msg()
            await b.opcode(data)
        print('SHEEP IS ON FIRE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        break
#run()