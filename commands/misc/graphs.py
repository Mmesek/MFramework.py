from MFramework.commands import register
from MFramework.utils.utils import tr
import MFramework.database.alchemy as db
@register(group='Admin')
async def graph(self, graph='all', resample='Y', locator='Month', interval=4, *args, data, growth=False, language, **kwargs):
    '''Possible arguments: graph=all/joined/created/boosters\nresample=W-MON/M/Y/dunnowhatelse\nmonth_interval=1+ probably\n-growth'''
    import time, asyncio
    b = time.time()
    from io import BytesIO
    import pandas as pd
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from MFramework.utils.utils import created, truncate
    from datetime import date
    f = time.time()
    await self.trigger_typing_indicator(data.channel_id)

    #Gather data here
    server = self.cache[data.guild_id]
    m_retries = 0
    if len(server.joined) != server.member_count:
        if len(server.joined) >= server.member_count:
            server.joined = []
        await self.request_guild_members(data.guild_id)
    while len(server.joined) != server.member_count and len(server.joined) < server.member_count:
        await asyncio.sleep(0.1)
        m_retries+=1
        if m_retries == 75:
            break
    s = time.time()

    #Create figure and plot data here
    s_member = self.cache[data.guild_id].joined
    total = {'joined':[], 'created':[], 'premium':[]}
    for each in s_member:
        t = pd.to_datetime(each[1]).tz_convert(None) #Joined
        c = pd.to_datetime(created(each[0])).tz_localize(None)  #Created
        try:
            p = pd.to_datetime(each[2]).tz_convert(None)  #Premium
            total['premium'] += [p]
        except:
            pass
        total['joined'] += [t]
        total['created'] += [c]
    sd = time.time()
    total['joined'] = sorted(total['joined'])
    total['created'] = sorted(total['created'])
    total['premium'] = sorted(total['premium'])
    d = time.time()

    fig, ax = plt.subplots()

    if graph == 'all' or graph == 'joined':
        if growth:
            df = pd.Series(total['joined'], index=total['joined'])

            df = df.resample(resample).count()
            idf = pd.to_datetime(df.index)
            ax.plot(idf, df, label=tr('commands.graph.joined', language), linestyle='-')
        else:
            df = pd.Series(total['joined'])
            ax.plot(df, df.index, label=tr('commands.graph.joined', language))
    
    if graph == 'all' or graph=='created':
        cr = pd.Series(total['created'], index=total['created'])
    
        cr = cr.resample(resample).count()
        icr = pd.to_datetime(cr.index)
        ax.plot(icr, cr, label=tr('commands.graph.created', language), marker='o')
    if graph == 'all' or graph == 'boosters':
        if growth:
            pr = pd.Series(total['premium'], index=total['premium'])
            pr = pr.resample(resample).count()
            ipr = pd.to_datetime(pr.index)
            ax.plot(ipr, pr, label=tr('commands.graph.boosters', language), marker='.')
        else:
            pr = pd.Series(total['premium'])
            ax.plot(pr, pr.index, label=tr('commands.graph.boosters', language), marker='.')


    #ax.fmt_xdata = mdates.DateFormatter('%m/%y')
    ax.xaxis.set_major_locator(mdates.YearLocator())
    locator = locator.lower()
    if locator == 'month':
        lctr = mdates.MonthLocator(interval=int(interval))
    elif locator == 'year':
        lctr = mdates.YearLocator()

    ax.xaxis.set_minor_locator(lctr)
    
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%y'))
    ax.xaxis.set_minor_formatter(mdates.DateFormatter('%m'))

    #fig.tight_layout()
    fig.autofmt_xdate()


    #Set Names
    ax.legend()
    ax.set_title(tr('commands.graph.growth', language))#"Growth")
    ax.set_ylabel(tr('commands.graph.memberCount', language))#'Member Count')
    ax.set_xlabel(tr('commands.graph.dates', language))#'Dates (Y/M)')


    buffered = BytesIO()
    fig.savefig(buffered)
    img_str = buffered.getvalue()
    stats = tr('commands.graph.stats', language, total=truncate(time.time()-d, 2), gather=truncate(s-f,2), sort=truncate(d-sd,2), convert=truncate(sd-s,2), imp=truncate(f-b,2))
    await self.withFile(data.channel_id, img_str, f"growth-{date.today()}.png", stats)#f"Took ~{truncate(time.time()-d,2)}s\n{truncate(s-f,2)}s to gather\n{truncate(d-sd,2)}s to sort\n{truncate(sd-s,2)}s to convert\n{truncate(f-b,2)}s to import stuff")

@register(group='Admin', help='Short description to use with help command', alias='', category='')
async def graph_infractions(self, infraction_type='all', resample='D', locator='Week', interval=1, *args, data, moderator=None, user=None, growth=False, language, **kwargs):
    '''Extended description to use with detailed help command'''
    import time
    b = time.time()
    from io import BytesIO
    import pandas as pd
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from MFramework.utils.utils import truncate
    from datetime import date
    f = time.time()
    await self.trigger_typing_indicator(data.channel_id)
    _s = self.db.sql.session()
    infractions = _s.query(db.Infractions).filter(db.Infractions.GuildID == data.guild_id)
    if infraction_type != 'all':
        infractions = infractions.filter(db.Infractions.InfractionType == infraction_type)
    if moderator != None:
        infractions = infractions.filter(db.Infractions.ModeratorID == moderator)
    if user != None:
        infractions = infractions.filter(db.Infractions.UserID == user)
    infractions = infractions.all()
    s = time.time()
    total = {'Total Infractions': []}
    table = {
        "warn": "Warnings",
        "tempmute": "Temp Mutes",
        "mute": "Mutes",
        "unmute": "Unmutes",
        "kick": "Kicks",
        "tempban":"Temp Bans",
        "ban": "Bans",
        "unban": "Unbans"
    }
    for i in table.values():
        total[i] = []
    total['Others'] = []
    for each in infractions:
        i = pd.to_datetime(each.Timestamp).tz_convert(None)
        total[table.get(each.InfractionType, 'Others')] += [i]
        total['Total Infractions'] += [i]

    sd = time.time()
    
    for i in total:
        total[i] = sorted(total[i])
    
    d = time.time()
    fig, ax = plt.subplots()

    for i in total:
        if total[i] == []:
            continue
        if not growth:
            df = pd.Series(total[i], index=total[i])
    
            df = df.resample(resample).count()
            idf = pd.to_datetime(df.index)
            ax.plot(idf, df, label=i)#tr('commands.graph.infractions', language), marker='o')
        else:
            df = pd.Series(total[i])
            ax.plot(df, df.index, label=i)#tr('commands.graph.infractions', language))


    ax.xaxis.set_major_locator(mdates.MonthLocator())
    locator = locator.lower()
    if locator == 'day':
        lctr = mdates.DayLocator(interval=int(interval))
    elif locator == 'week':
        lctr = mdates.WeekdayLocator(interval=int(interval))
    elif locator == 'month':
        lctr = mdates.MonthLocator(interval=int(interval))
    elif locator == 'year':
        lctr = mdates.YearLocator()

    ax.xaxis.set_minor_locator(lctr)
    
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%y'))
    ax.xaxis.set_minor_formatter(mdates.DateFormatter('%d/%m'))

    #fig.tight_layout()
    fig.autofmt_xdate()


    #Set Names
    ax.legend()
    ax.set_title(tr('commands.graph.infractions', language))
    ax.set_ylabel(tr('commands.graph.infractionCount', language))
    ax.set_xlabel('Dates (D/M)')

    buffered = BytesIO()
    fig.savefig(buffered)
    img_str = buffered.getvalue()
    stats = tr('commands.graph.stats', language, total=truncate(time.time()-d, 2), gather=truncate(s-f,2), sort=truncate(d-sd,2), convert=truncate(sd-s,2), imp=truncate(f-b,2))
    await self.withFile(data.channel_id, img_str, f"growth-{date.today()}.png", stats)
