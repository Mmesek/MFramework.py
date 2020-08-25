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

