from MFramework.commands import register
from MFramework.utils.utils import Embed, convert_bytes, getsize, file_size, secondsToText, bytes2human
import asyncio, time


def ping(endpoint=''):
    return 0


@register(group="System", help="Shows statistics related to bot and system")
async def status(self, *args, data, no_ping=False, language, **kwargs):
    import psutil
    self_size = getsize(self)
    embed = Embed()
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    cpu = psutil.cpu_percent()
    proc = psutil.Process()
    ram = proc.memory_info()[0]
    try:
        temp = psutil.sensors_temperatures()["cpu-thermal"][0][1]
    except:
        temp = 0
    sys_uptime = int(time.time() - psutil.boot_time())
    proc_uptime = int(time.time() - proc.create_time())

    embed.addField("Uptime", secondsToText(sys_uptime, language), True)
    embed.addField("Bot Uptime", secondsToText(proc_uptime, language), True)
    embed.addField("Session", secondsToText(int(time.time() - self.startTime), language), True)
    if not no_ping:
        discord = ping()
        api = ping("")
        cdn = ping("cdn")
        embed.addField("Ping", f"Discord: {discord}ms\nAPI: {api}ms\nCDN: {cdn}ms", True)
    if self.latency != None:
        embed.addField("Latency", "{0:.2f}ms".format(self.latency), True)
    else:
        embed.addField("\u200b", "\u200b", True)
    embed.addField("Current Temperature", "{0:.2f}'C".format(temp), True)
    embed.addField("CPU", f"{cpu}%", True)
    embed.addField("Tasks", str(len(tasks)), True)
    try:
        import resource
        child_usage = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
        self_usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    except:
        child_usage = 0
        self_usage = 0
    #    print(resource.getrusage(resource.RUSAGE_CHILDREN))
    #    print(resource.getrusage(resource.RUSAGE_SELF))
    network = psutil.net_io_counters(pernic=True)
    eth = 0
    wlan = 0
    net = ''
    if 'eth0' in network:
        ethdl = bytes2human(network['eth0'].bytes_recv)
        ethup = bytes2human(network['eth0'].bytes_sent)
        net += 'Ethernet: '+ethdl+' ↓↑ '+ ethup+'\n'
    if 'wlan0' in network:
        wlandl = bytes2human(network['wlan0'].bytes_recv)
        wlanup = bytes2human(network['wlan0'].bytes_sent)
        net += 'Wireless: '+wlandl + ' ↓↑ '+ wlanup+'\n'
    if 'wlan0' not in network and 'eth0' not in network:
        network = psutil.net_io_counters()
        netdl = bytes2human(network.bytes_recv)
        netup = bytes2human(network.bytes_sent)
        net += 'Total: '+netdl + ' ↓↑ '+ netup
    
    embed.addField("Network Usage",net, True)
    embed.addField("RAM Usage", convert_bytes(self_usage + child_usage), True)

    cache_size = getsize(self.cache)
    if hasattr(self, "index"):
        idx = getsize(self.index)
        bot_size = convert_bytes(self_size - cache_size - idx)
        idx = "File: " + file_size("data/steamstoreindex.json") + "\nLoaded: " + convert_bytes(idx)
    else:
        try:
            idx = file_size("data/steamstoreindex.json")
        except:
            idx = 0
        bot_size = convert_bytes(self_size - cache_size)

    embed.addField("Bot Usage", bot_size, True)
    embed.addField("RAM", f"{convert_bytes(ram)}", True)
    try:
        import gpiozero
        embed.addField("Disk Usage", f"{int(gpiozero.DiskUsage().usage)}%", True)
    except:
        embed.addField("\u200b", "\u200b", True)
    embed.addField("Cache Size", convert_bytes(cache_size), True)
    #embed.addField("\u200b", "\u200b", True)
    embed.addField("Steam Index Size", idx, True)
    embed.setColor(self.cache[data.guild_id].color)
    await self.embed(data.channel_id, "", embed.embed)


@register(group="System", help="Shows bot information")
async def version(self, *args, data, **kwargs):
    import platform
    system = platform.system()
    release = platform.release()
    machine = platform.machine()
    node = platform.node()
    arch = platform.architecture()
    python = platform.python_version()
    shard = self.shards
    servers = len(self.cache)
    mframework = 3#self.version
    seq = self.last_sequence
    desc = f"{self.username} @ {node}"
    if 'arm' in machine:
        import gpiozero
        node = 'Raspberry {0:board}\n{0:memory}MB'.format(gpiozero.pi_info())
    try:
        influx = await self.db.influx.influxPing()
    except:
        influx = "ERROR: Database offline."
    try:
        postgres = "Online"
    except:
        postgres = "Offline"
    embed = (Embed() 
    .addField("Python", python, True)
    .addField("MFramework", mframework, True)
    .addField("OS", f"{system} {release}", True)
    .addField("Architecture", f"{machine} {arch[0]}", True)
    .addField("\u200b", "\u200b", True)
    .addField("System", node, True)

    .addField("Servers", servers-1, True)
    .addField("Sequence", seq, True)
    .addField("Shard", f"{shard[0]}/{shard[1]}", True)

    .addField("InfluxDB", influx, True)
    .addField("\u200b", "\u200b", True)
    .addField("PostgreSQL", postgres, True)
    )
    
    embed.setColor(self.cache[data.guild_id].color).setDescription(desc)
    await self.embed(data.channel_id, "", embed.embed)

@register(group='System', help='Short description to use with help command', notImpl=True)
async def remaining(self, *args, data, **kwargs):
    '''Extended description to use with detailed help command'''
    print(await self.get_gateway_bot())