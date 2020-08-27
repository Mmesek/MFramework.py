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

@register(group='Admin', help='Short description to use with help command', alias='', category='')
async def graph_words(self, channel_id, *word_or_phrase, data, limit_messages=10000, resample='W-MON', locator='Week', interval=1, growth=False, language, **kwargs):
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

    word_or_phrase = ''.join(word_or_phrase)
    limit_messages = int(limit_messages)
    if limit_messages < 100:
        limit = limit_messages
    else:
        limit = 100
    total_messages = await self.get_messages(channel_id, limit=limit)
    previous_id = 0
    previous_first_id = 0
    cache = self.cache[data.guild_id].messages
    channel_id = int(channel_id)
    if channel_id in cache:
        cached_messages = list(i[1] for i in sorted(cache[channel_id].items()))
        #print("Last Message:", total_messages[0].content)
        #print("First Cached Messaged:", cached_messages[0].content)
        #print("Last Cached Messaged:", cached_messages[-1].content)
        if total_messages[0].id > cached_messages[-1].id:
            print("old cache?")
            last_id = cached_messages[-1]
            old = True
        else:
            print("Cache up to date")
            old = False
            total_messages = cached_messages
    if limit_messages > 100:
        for i in range(int((int(limit_messages)) / 100)):
            last_id = total_messages[-1].id
            first_id = total_messages[0].id
            print(previous_id, last_id, previous_id > last_id, len(total_messages))
            if previous_id > last_id or previous_id == 0: #and previous_first_id < first_id:
                new_messages = await self.get_messages(channel_id, snowflake=last_id)
                #if new_messages[0] != total_messages[0] and new_messages[-1] != total_messages[-1]:
                total_messages += new_messages
                previous_id = last_id
                previous_first_id = first_id
            else:
                break
    for msg in reversed(total_messages):
        if msg.id not in self.cache[data.guild_id].messages[channel_id]:
            self.cache[data.guild_id].message(msg.id, msg)
    total_messages = list(i[1] for i in sorted(self.cache[data.guild_id].messages[channel_id].items()))

    s = time.time()

    total = {word_or_phrase: []}
    sorted_total = {word_or_phrase: []}
    for message in total_messages:
        if word_or_phrase in message.content:
            message_timestamp = pd.to_datetime(message.timestamp).tz_convert(None)
            total[word_or_phrase] += [message_timestamp]
    sd = time.time()

    if total[word_or_phrase] == []:
        return await self.message(data.channel_id, f"Couldn't find specified word or phrase ({word_or_phrase}) within last fetchable {len(total_messages)} in <#{channel_id}>")
    #for i in total:
    #    sorted_total[i] = sorted(total[i])

    d = time.time()
    fig, ax = plt.subplots()

    for i in total:
        if total[i] == []:
            continue
        if not growth:
            df = pd.Series(total[i], index=total[i])
    
            df = df.resample(resample).count()
            idf = pd.to_datetime(df.index)
            ax.plot(idf, df, label=i, marker='o')#tr('commands.graph.infractions', language), marker='o')
        else:
            df = pd.Series(total[i])
            ax.plot(df, df.index, label=i)#tr('commands.graph.infractions', language))


    locator = locator.lower()
    major = '%d/%m'
    minor = '%H/%d'
    if locator == 'minute':
        ax.xaxis.set_major_locator(mdates.HourLocator())
        lctr = mdates.MinuteLocator(interval=int(interval))
        major = '%H/%d'
        minor = '%M:%H'
    elif locator == 'hour':
        ax.xaxis.set_major_locator(mdates.DayLocator())
        lctr = mdates.HourLocator(interval=int(interval))
        major = '%d/%m'
        minor = '%H'
    elif locator == 'day':
        ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=7))
        lctr = mdates.DayLocator(interval=int(interval))
        major = '%d/%m'
        minor = '%H/%d'
    elif locator == 'week':
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        lctr = mdates.WeekdayLocator(interval=int(interval))
        major = '%m/%y'
        minor = '%d'
    elif locator == 'month':
        ax.xaxis.set_major_locator(mdates.YearLocator())
        lctr = mdates.MonthLocator(interval=int(interval))
        major = '%y'
        minor = '%m'
    elif locator == 'year':
        lctr = mdates.YearLocator()

    ax.xaxis.set_minor_locator(lctr)
    
    ax.xaxis.set_major_formatter(mdates.DateFormatter(major))
    ax.xaxis.set_minor_formatter(mdates.DateFormatter(minor))

    #fig.tight_layout()
    fig.autofmt_xdate()


    #Set Names
    ax.legend()
    ax.set_title(tr('commands.graph.words', language))
    ax.set_ylabel(tr('commands.graph.wordCount', language))
    ax.set_xlabel('Dates (D/M)')

    buffered = BytesIO()
    fig.savefig(buffered)
    img_str = buffered.getvalue()
    stats = tr('commands.graph.stats', language, total=truncate(time.time()-d, 2), gather=truncate(s-f,2), sort=truncate(d-sd,2), convert=truncate(sd-s,2), imp=truncate(f-b,2))
    await self.withFile(data.channel_id, img_str, f"growth-{date.today()}.png", f"Found {len(total[word_or_phrase])} messages containing `{word_or_phrase}` within {len(total_messages)} of total fetched messages. (Took {truncate(s-f,2)}s to fetch them)")