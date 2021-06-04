from MFramework import register, Groups, Context, Interaction, Embed
import time

@register(group=Groups.GLOBAL, guild=463433273620824104)
async def bot(ctx: Context, interaction: Interaction, *args, language, **kwargs):
    '''
    Shows Information about bot
    '''
    pass

@register(group=Groups.GLOBAL, main=bot)
async def ping(ctx: Context, interaction: Interaction, detailed: bool=False, *args, language, **kwargs):
    '''
    Shows ping
    Params
    ------
    detailed:
        Whether it should show extended ping information
    '''
    s = time.time()
    await interaction.deferred_message(False)
    end = time.time()
    e = None
    if detailed:
        discord = ping()
        e = Embed().addField("Discord", f"{discord}", True)
        router = ping('192.168.1.254')
        if router[0] != '0':
            e.addField("Router", f"{router}", True)
        if ctx.bot.latency != None:
            e.addField("Heartbeat", "{0:.2f}ms".format(ctx.bot.latency), True)
        e = [e]
    await interaction.edit_response(f"Pong! `{int((end-s)*1000)}ms`", e)

def ping(host='discord.com'):
    import platform, os
    s = platform.system().lower() == 'windows'
    param = '-n' if s else '-c'
    command = ['ping', param, '1', host]
    r = os.popen(' '.join(command))
    for line in r:
        last = line
    try:
        if s:
            ping = last.split('=', 1)[1].split('=', 2)[2]
        else:
            ping = last.split('=', 1)[1].split('/', 2)[1]
    except:
        return ''
    if 'ms' not in ping:
        ping+='ms'
    return ping.lstrip().strip('\n')

@register(group=Groups.GLOBAL, main=bot)
async def status(ctx: Context, interaction: Interaction, show_ping: bool=False, *args, language="en", **kwargs):
    '''
    Shows statistics related to bot and system
    Params
    ------
    show_ping:
        whether it should show ping or not
    '''
    await interaction.deferred_message(False)
    from mlib.sizes import getsize, bytes2human, convert_bytes, file_size
    from mlib.localization import secondsToText
    import psutil, asyncio
    self_size = getsize(ctx.bot)
    embed = Embed()
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    cpu = psutil.cpu_percent()
    proc = psutil.Process()
    ram = proc.memory_info()[0]
    try:
        temp = psutil.sensors_temperatures()["cpu_thermal"][0][1]
    except:
        temp = 0
    sys_uptime = int(time.time() - psutil.boot_time())
    proc_uptime = int(time.time() - proc.create_time())

    embed.addField("Uptime", secondsToText(sys_uptime, language), True)
    embed.addField("Bot Uptime", secondsToText(proc_uptime, language), True)
    embed.addField("Session", secondsToText(int(time.time() - ctx.bot.start_time), language), True)
    if show_ping:
        discord = ping()
        api = 0#ping("")
        cdn = ping("cdn.discordapp.com")
        embed.addField("Ping", f"Discord: {discord}\nAPI: {api}ms\nCDN: {cdn}", True)
    if ctx.bot.latency != None:
        embed.addField("Latency", "{0:.2f}ms".format(ctx.bot.latency), True)
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
    network = psutil.net_io_counters(pernic=True)
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

    cache_size = getsize(ctx.bot.cache)
    if hasattr(ctx, "index"):
        idx = getsize(ctx.index)
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
    embed.addField("Steam Index Size", idx, True)
    r = await ctx.bot.get_gateway_bot()
    embed.addField("Remaining sessions", r.get('session_start_limit', {}).get('remaining', -1))
    embed.setColor(ctx.cache.color)
    await interaction.edit_response(embeds=[embed])

@register(group=Groups.GLOBAL, main=bot)
async def version(ctx: Context, interaction: Interaction, *args, language, **kwargs):
    '''
    Shows bot's version
    '''
    await interaction.deferred_message(False)
    import platform
    system = platform.system()
    release = platform.release()
    machine = platform.machine()
    node = platform.node()
    arch = platform.architecture()
    python = platform.python_version()
    shard = ctx.bot.shards
    servers = len(ctx.bot.cache)
    from MFramework import __version__ as ver, ver_date
    mframework = ver
    seq = ctx.bot.last_sequence
    desc = f"{ctx.bot.username} @ {node}"
    if 'arm' in machine:
        from gpiozero import pi_info
        node = 'Raspberry {0}\n{1}MB'.format(pi_info().model, pi_info().memory)
    try:
        influx = await ctx.db.influx.influxPing()
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
    embed.setTimestamp(ver_date).setFooter("Last Commit")
    embed.setColor(ctx.cache.color).setDescription(desc)
    await interaction.edit_response(embeds=[embed])

@register(group=Groups.GLOBAL, main=bot)
async def stats(ctx: Context, interaction: Interaction, *args, language, **kwargs):
    '''
    Shows received events & registered commands
    '''
    msg = ''
    e = Embed()
    for counter in ctx.bot.counters:
        msg += f"\n`{counter}`: {ctx.bot.counters[counter]}"

    from MFramework.commands._utils import commands
    groups = list(commands)
    groups.reverse()
    cmds = ""
    cmds += f"\n`Total`: {len(set(commands))}"
    #TODO: It doesn't list groups or subcommands yet!
    #TODO: Show executed commands?

    e.addField("Events Received", msg, True)
    e.addField("Registered Commands", cmds, True)
    await interaction.send(embeds=[e])