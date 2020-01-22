import asyncio
from bot.discord.commands import register

import os, time
def measure_temp():
    temp = os.popen("vcgencmd measure_temp").readline()
    return (temp.replace("temp=",""))
def uptime():
    ut = os.popen("uptime -p").readline()
    return (ut.replace('up ',''))
def ping():
    ping = os.popen("ping -c 4 www.discordapp.com") 
    for line in ping:
        lastline=line
    return lastline
#connection speed: https://www.raspberrypi-spy.co.uk/2015/03/measuring-internet-speed-in-python-using-speedtest-cli/

@register(group="System",help="Shows statistics: Temperature, uptime and ping")
async def status(self, data):
    await self.endpoints.message(data['channel_id'],f'Uptime: {uptime()}\nCurrent Temperature: {measure_temp()}\nPing to Discord: {ping()}')

@register(group="System",help="Reloads commands files.")
async def reloadCommands(self, data):
    '''This probably needs to be placed in another file but well, it's here currently FOR SCIENCE.'''
    import importlib; importlib.reload(__name__)


@register(group="System")
async def getTasks(self, data):
    tasks = [
        t for t in asyncio.all_tasks() 
        if t is not asyncio.current_task()
    ]
    [t.print_stack(limit=5) for t in tasks]

@register(group="System",help="Shuts bot down.")
async def shutdown(self, data):
    await self.close()
    print('Received shutdown command. Shutting down.')

import platform
@register(group="System",help="Shows bot information")
async def version(self, data):
    system = platform.system()
    release = platform.release()
    machine = platform.machine()
    node = platform.node()
    arch = platform.architecture()
    python = platform.python_version()
    try:
        influx = await self.db.influxPing()
    except:
        influx = "ERROR: Database offline."
    try:
        mongo = await self.db.db.mongoPing()
        mongo = ''
    except:
        mongo = 'ERROR: Database offline.'
    await self.endpoints.message(data['channel_id'],f'<@{self.user_id}> @ {node} using Python {python} on {system} {release} {arch[0]} with {machine}\nDatabases used:\nInfluxDB {influx}\nMongoDB {mongo}')


import pickle
from collections import namedtuple
import numpy as np
from bot.utils import timed
_model = None

Scores = namedtuple("Scores", ["toxic", "severe_toxic",
                               "obscence", "insult", "identity_hate"])

@timed
async def warm(model_path):
    global _model
    if _model is None:
        with open("data/pipeline.dat",'rb') as fp:
            pipeline = pickle.load(fp)
            _model = pipeline
    return True
@timed
async def predict(message):
    results = _model.predict_proba([message])
    results = np.array(results).T[1].tolist()[0] #pylint: disable=unsubscriptable-object
    return Scores(*results)
@timed
async def mod(self, data):
    await warm(0)
    scores = await predict(data["content"])
    print(scores)
    if np.average([scores.toxic, scores.insult]) >= 0.4:
        await self.endpoints.message(data['channel_id'], f'Detected averange of Toxicity and Insult above set value: {scores.toxic} and {scores.insult}')
