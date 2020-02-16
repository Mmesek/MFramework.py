import asyncio, platform
from bot.discord.commands import register

import os, time

import pickle
from collections import namedtuple
import numpy as np
from bot.utils.utils import timed

_model = None

Scores = namedtuple("Scores", ["toxic", "severe_toxic", "obscence", "insult", "identity_hate"])

def measure_temp():
    temp = os.popen("vcgencmd measure_temp").readline()
    return temp.replace("temp=", "")


def uptime():
    ut = os.popen("uptime -p").readline()
    return ut.replace("up ", "")


def ping():
    ping = os.popen("ping -c 4 www.discordapp.com")
    for line in ping:
        lastline = line
    return lastline


# connection speed: https://www.raspberrypi-spy.co.uk/2015/03/measuring-internet-speed-in-python-using-speedtest-cli/


@register(group="System", help="Shows statistics: Temperature, uptime and ping")
async def status(self, *args, data, **kwargs):
    await self.endpoints.message(data["channel_id"], f"{platform.node()} Uptime: {uptime()}Current Temperature: {measure_temp()}Ping to Discord: {ping().split('=',1)[1].split('/',2)[1]}ms")


@register(group="System", help="Reloads commands files.")
async def reloadCommands(self, *args, data, **kwargs):
    """This probably needs to be placed in another file but well, it's here currently FOR SCIENCE."""
    import importlib

    importlib.reload(__name__)


@register(group="System")
async def getTasks(self, *args, data, **kwargs):
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    [t.print_stack(limit=5) for t in tasks]


@register(group="System", help="Shuts bot down.")
async def shutdown(self, *args, data, **kwargs):
    await self.close()
    print("Received shutdown command. Shutting down.")

@register(group="System", help="Shows bot information")
async def version(self, *args, data, **kwargs):
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
        mongo = ""
    except:
        mongo = "ERROR: Database offline."
    try:
        postgres = 'Not yet implemented.'
    except:
        postgres = 'ERROR: Database offline.'
    await self.endpoints.message(
        data["channel_id"],
        f"{self.username} @ {node} using Python {python} on {system} {release} {arch[0]} with {machine}\nDatabases used:\nInfluxDB {influx}\nMongoDB {mongo}\nPostgreSQL {postgres}",
    )

@timed
async def warm(model_path):
    global _model
    if _model is None:
        with open("data/pipeline.dat", "rb") as fp:
            pipeline = pickle.load(fp)
            _model = pipeline
    return True


@timed
async def predict(message):
    results = _model.predict_proba([message])
    results = np.array(results).T[1].tolist()[0]  # pylint: disable=unsubscriptable-object
    return Scores(*results)


@timed
async def mod(self, data):
    await warm(0)
    scores = await predict(data["content"])
    print(scores)
    if np.average([scores.toxic, scores.insult]) >= 0.4:
        await self.endpoints.message(
            data["channel_id"],
            f"Detected averange of Toxicity and Insult above set value: {scores.toxic} and {scores.insult}",
        )

from io import BytesIO
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from bot.utils.utils import created, truncate
from datetime import date
import dateutil

@register(group='Admin', help='Shows graph of member count change and years of account creations. Before you say something about it being slow, ~~obtainting~~ harvesting data of users from Discord takes quite a bit on bigger servers')
async def graph(self, *args, data, **kwargs):
    await self.endpoints.trigger_typing(data['channel_id'])
    f = time.time()
    members = await self.db.influxGetMember(data['guild_id'])
    server = self.cache.cache[data['guild_id']]
    m_retries = 0
    if len(server['joined']) != server['member_count']:
        if len(server['joined']) >= server['member_count']:
            server['joined'] = []
        await self.request_guild_members(data['guild_id'])
    while len(server['joined']) != server['member_count'] and len(server['joined']) < server['member_count']:
        await asyncio.sleep(0.1)
        m_retries+=1
        if m_retries == 75:
            break
    s = time.time()
    s_member = self.cache.cache[data['guild_id']]['joined']
    s_member = sorted(s_member)
    total = []
    for each in s_member:
        t = pd.to_datetime(each[1])
        total += [{'time':t, 'change': True, 'created':await created(each[0])}]
    for each in members:
        for i in each:
            if i['change'] == False:
                t = pd.to_datetime(i['time'])
                #total += [{'time':t, 'change': i['change'], 'created':datetime.datetime.today()}]
    total = sorted(total, key=lambda k: k['time'])
    c = {'date':[],'count':[],'created':[]}
    for one in total:
        try:
            if one['change'] == True:
                c['count'] += [c['count'][-1]+1]
                c['date'] += [one['time']]
                c['created'] += [one['created']]
            else:
                c['count'] += [c['count'][-1]-1]
                c['date'] += [one['time']]
                c['created'] += [one['created']]
        except:
            c['count'] += [1]
            c['date'] += [one['time']]
            c['created'] += [one['created']]

    ts = pd.DataFrame.from_dict(c)
    #ts['date'] = ts['date'].astype('datetime64[D]')
    #ts = pd.Series(ch)
    #ts = pd.Series(list(ch.values()),index=pd.MultiIndex.from_tuples(ch.keys()))
    #ts = ts.cumsum()
    ts = ts.set_index('date')

    fig, (ax, ax2) = plt.subplots(1,2,figsize=(15,7))
    #fig, ax = plt.subplots(figsize=(15,7))
    ts.plot(kind='line',ax=ax,y='count', legend=False)
    ax.set_title('Member Increase')
    ax.set_xlabel('Dates')
    ax.set_ylabel('Member Count')
    ax.fmt_xdata = mdates.DateFormatter('%m/%y')
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    #ax.xaxis.set_major_formatter(ticker.FixedFormatter(ticks))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%y'))
    #ax.xaxis.set_minor_locator(mdates.WeekdayLocator())
    #ts['date'].apply(lambda x: dateutil.parser.parse(str(x)).strftime('%Y')).value_counts().sort_index().plot(kind='bar',ax=ax, stacked=True)
    ts['created'].apply(lambda x: dateutil.parser.parse(str(x)).strftime('%Y')).value_counts().sort_index().plot(kind='bar',ax=ax2)
    ax2.set_title('Member Accounts Creation years')
    ax2.set_xlabel('Years')
    ax2.set_ylabel('Amount')

    fig.autofmt_xdate()

    buffered = BytesIO()
    fig.savefig(buffered)
    img_str = buffered.getvalue()
    
    await self.endpoints.withFile(data["channel_id"], img_str, f"growth-{date.today()}.png", f"Took ~{truncate(time.time()-s,2)}s (And {truncate(s-f,2)}s to gather data)")


@register(group='System')
async def updateStatus(self, *args, data, **kwargs):
    '''Extended description to use with detailed help command'''
    s = data['content'].split(',',2)
    print(s)
    await self.status_update(data, s[0],s[2],int(s[1]))


from bot.utils.scheduler import rssTask
@register(group='System')
async def startTasks(self, *args, data, **kwargs):
    '''Extended description to use with detailed help command'''
    rssTask.delay(self)
