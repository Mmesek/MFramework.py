from MFramework.commands import register
from MFramework.utils.utils import tr
@register(help='Decodes or Encodes message in Morse')
async def morse(self, *message, data, decode=False, **kwargs):
    morse_dict = {
        'A':'.-', 'B':'-...', 'C':'-.-.', 'D':'-..', 'E':'.', 
        'F':'..-.', 'G':'--.', 'H':'....', 'I':'..', 'J':'.---', 
        'K':'-.-', 'L':'.-..', 'M':'--', 'N':'-.', 'O':'---', 
        'P':'.--.', 'Q':'--.-', 'R':'.-.', 'S':'...', 'T':'-', 
        'U':'..-', 'V':'...-', 'W':'.--', 'X':'-..-', 'Y':'-.--', 
        'Z':'--..', '1':'.----', '2':'..---', '3':'...--', '4':'....-', 
        '5':'.....', '6':'-....', '7':'--...', '8':'---..', '9':'----.', 
        '0':'-----', ', ':'--..--', '.':'.-.-.-', '?':'..--..', '/':'-..-.', 
        '-':'-....-', '(':'-.--.', ')':'-.--.-', '`':'.----.', '!':'-.-.--',
        '&':'.-...',':':'---...',';':'-.-.-.','=':'-...-','+':'.-.-.',
        '_':'..--.-','"':'.-..-.','$':'...-..-','@':'.--.-.',
        'Ĝ':'--.-.','Ĵ':'.---.','Ś':'...-...','Þ':'.--..','Ź':'--..-.','Ż':'--..-','Ð':'..-..',
        'Error':'........','End of Work':'...-.-','Starting Signal':'-.-.-',
        'Understood':'...-.'
    }
    morse_sequences = {
        ". .-. .-. --- .-.":"........",
        ". -. -.. -....- --- ..-. -....- .-- --- .-. -.-":"...-.-",
        "..- -. -.. . .-. ... - --- --- -..":"...-."
    }
    inverted = {v: k for k, v in morse_dict.items()}
    def encrypt(message):
        cipher=''
        for letter in message.upper():
            if letter == ' ':
                cipher+='/'
                #cipher+=morse_dict['-']+' '
                continue
            elif letter not in morse_dict:
                cipher+=letter+' '
            else:
                cipher+=morse_dict[letter]+' '#morse_dict.get(letter,'') + ' '
        for sequence in morse_sequences:
            if sequence in cipher:
                cipher = cipher.replace(sequence, morse_sequences[sequence])
        return cipher
    def decrypt(message):
        message += ' '
        decipher = ''
        morse = ''
        for letter in message:
            if letter == '/':
                decipher +=' '
            elif letter not in '.-' and letter != ' ':
                decipher += letter
            elif letter != ' ':
                morse += letter
            elif letter == ' ' and morse != '':
                try:
                    decipher += inverted[morse]#inverted.get(morse,'')
                except:
                    decipher += '\nNo match for: "'+morse+'"\n'
                morse = ''
        return decipher
    org = data.content
    if decode:
        reward = decrypt(data.content)
        t = "Morse -> Normal"
    else:
        reward = encrypt(data.content)
        t = "Normal -> Morse"
    if len(org) > 2000:
        org = org[:100] + f"\n(+{len(org)-100} more characters)\nCharacter limit exceeded."
    if len(reward) > 2048:
        t=t+f" | Not sent {len(reward)-2048} characters due to limit of 2048"
        reward = reward[:2048]
    await self.embed(data.channel_id, 'Orginal: '+org, {"title":t,"description":reward})


#from io import BytesIO
#import pandas as pd
#import matplotlib.pyplot as plt
#import matplotlib.dates as mdates
#import numpy as np
#from MFramework.utils.utils import created, truncate
#from datetime import date
#import dateutil, time, asyncio

'''@register(group='Admin', help='Shows graph of member count change and years of account creations.')
async def graph(self, *args, data, **kwargs):
    """Before you say something about it being slow, ~~obtainting~~ harvesting data of users from Discord takes quite a bit on bigger servers"""
    await self.trigger_typing_indicator(data.channel_id)
    f = time.time()
    members = await self.db.influx.influxGetMember(data.guild_id)
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
    s_member = self.cache[data.guild_id].joined
    s_member = sorted(s_member)
    total = []
    for each in s_member:
        t = pd.to_datetime(each[1])
        total += [{'time':t, 'change': True, 'created':created(each[0])}]
    for each in members:
        for i in each:
            if i['change'] == False:
                t = pd.to_datetime(i['time'])
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
    ts = ts.set_index('date')

    fig, (ax, ax2) = plt.subplots(1,2,figsize=(15,7))
    ts.plot(kind='line',ax=ax,y='count', legend=False)
    ax.set_title('Member Increase')
    ax.set_xlabel('Dates')
    ax.set_ylabel('Member Count')
    ax.fmt_xdata = mdates.DateFormatter('%m/%y')
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%y'))
    ts['created'].apply(lambda x: dateutil.parser.parse(str(x)).strftime('%Y')).value_counts().sort_index().plot(kind='bar',ax=ax2)
    ax2.set_title('Member Accounts Creation years')
    ax2.set_xlabel('Years')
    ax2.set_ylabel('Amount')

    fig.autofmt_xdate()

    buffered = BytesIO()
    fig.savefig(buffered)
    img_str = buffered.getvalue()
    
    await self.withFile(data.channel_id, img_str, f"growth-{date.today()}.png", f"Took ~{truncate(time.time()-s,2)}s (And {truncate(s-f,2)}s to gather data)")'''

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
