import asyncio, json, aiohttp
import bot.discord.endpoints as endpoints
import bot.discord.database as db
import bot.discord.cache as cache

from bot.discord.commands import Invalid
from bot.config import cfg as config
from bot.utils import log

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

class Bot:
    def __init__(self):
        self.token = config['Tokens']['discord']
        self.session_id = 0
        self.user_id    = 0
        self.sequence   = 0
        self.keepConnection = True
        self.state = True
        self.stayConnected = True
        self.presence = config['Discord']['presence']
        self.sub    = config['Discord']['subscription']
        self.presenceType = config['Discord']['presence_type']
        self.shards = None #[shard,total]
        self.db = db.Database(config['Database']['location'],config['Database']['name'])
        asyncio.create_task(self.db.createTables())
        self.cache = cache.Cache(self.db)
        self.endpoints = endpoints.Endpoints(self.api_call)
        self.op = {
            0:self.dispatch,
            7:self.reconnect,
            9:self.invalid_session,
            10:self.hello,
            11:self.heartbeat_ack}
        self.message_type = mtypes
        print('Initating Bot with token: ',self.token)
    async def api_call(self, path, method="GET", reason='', **kwargs):
        if 'file' in kwargs:
            data = aiohttp.FormData()
            data.add_field('payload_json',json.dumps(kwargs['json']))
            data.add_field('file',kwargs['file'][1], filename=kwargs['file'][0],content_type='application/octet-stream')
            return await self.csession.post(url='https://discordapp.com/api'+path,data=data,headers=[('Authorization',f'Bot {self.token}')])
        defaults = {"headers":{"Authorization": f"Bot {self.token}", "Content-Type": "application/json", "X-Audit-Log-Reason":f"{reason}"}}
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
#       async for msg in self.ws:
#           await self.opcode(json.loads(msg.data))
    async def msg(self):
#        msg = await self.ws.receive()
#        print('Type:',msg.type,'\nExtra: ',msg.extra)
#        data = json.loads(msg.data)
        async for msg in self.ws:
            try:
                data = json.loads(msg.data)
                if data != None:
                    asyncio.create_task(self.opcode(data))
            except Exception as ex:
                print('Error:', ex)
#        while self.keepConnection:
#            try:
#                data = await self.ws.receive_json()
#            except Exception:
#                data = await self.ws.receive()
#                print('Msg Error: ', data.type, data.extra, data.data)
#                self.keepConnection = False
#                data = None
#            if data != None:
#                asyncio.create_task(self.opcode(data))
        await self.close()
    async def heartbeat(self, interval):
        while self.keepConnection:
            await asyncio.sleep(interval/1000)
            await self.ws.send_json({"op":1, "d":self.sequence})
    async def close(self):
        self.keepConnection = False
        print('Closing')
#        self.db.client.close()
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

async def cancelTasks():
    tasks = [t for t in asyncio.all_tasks() if t is not
             asyncio.current_task()]
    [print(task.get_stack()) for task in tasks]
    [task.cancel() for task in tasks]
    print(f"Cancelling {len(tasks)} tasks")
    await asyncio.gather(*tasks, return_exceptions=True)

async def shutdown(loop, bot=None):
    if bot:
        bot.keepConnection = False
        await bot.close()
        await asyncio.sleep(0)
    tasks = [t for t in asyncio.all_tasks() if t is not
             asyncio.current_task()]
    [print(task.get_stack()) for task in tasks]
    [task.cancel() for task in tasks]
    print(f"Cancelling {len(tasks)} tasks")
    await asyncio.gather(*tasks, return_exceptions=True)
    loop.stop()

async def handle_exception(loop, context):
    msg = context.get("exception", context["message"])
    print(f"Handling exception: {msg}")
    log(f"Caught exception: {msg}")
    asyncio.create_task(shutdown(loop))



def run():
    #/Not tested
    from sys import platform
    if platform != "win32":
        import signal
        loop = asyncio.get_event_loop()
        loop.add_signal_handler(signal.SIGINT,asyncio.create_task(shutdown(loop)))
        loop.set_exception_handler(handle_exception)
        #loop.run_until_complete(main())
        #loop.close()
    #Not tested/
    asyncio.run(main())

async def main():
    b = Bot()
    await b.connection()
    try:
        await b.msg()
    except Exception as ex:
        log(f"Main exception: {ex}")
    finally:
        try:
            await asyncio.sleep(1)
            if b.state:
                await b.close()
        except Exception as ex: 
            log(f"Clean up exception: {ex}")