from MFramework.commands import register

import requests, datetime
from MFramework.utils.utils import Embed, tr

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

@register(group='Global', help='Converts Roman to Int, or vice versa', alias='', category='')
async def roman(self, *value, data, language, **kwargs):
    '''Very simple and does not really work (Well, it works but if you mess up digit it does not really check that)'''
    #Sources:
    # https://www.w3resource.com/python-exercises/class-exercises/python-class-exercise-1.php 
    # https://www.w3resource.com/python-exercises/class-exercises/python-class-exercise-2.php
    # https://www.oreilly.com/library/view/python-cookbook/0596001673/ch03s24.html
    def int_to_Roman(num):
        val = [
            1000, 900, 500, 400,
            100, 90, 50, 40,
            10, 9, 5, 4,
            1
            ]
        syb = [
            "M", "CM", "D", "CD",
            "C", "XC", "L", "XL",
            "X", "IX", "V", "IV",
            "I"
            ]
        roman_num = ''
        i = 0
        while  num > 0:
            for _ in range(num // val[i]):
                roman_num += syb[i]
                num -= val[i]
            i += 1
        return roman_num
    def roman_to_int(s):
        rom_val = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
        int_val = 0
        for i in range(len(s)):
            if i > 0 and rom_val[s[i]] > rom_val[s[i - 1]]:
                int_val += rom_val[s[i]] - 2 * rom_val[s[i - 1]]
            else:
                int_val += rom_val[s[i]]
        return int_val
    value = ''.join(value)
    if value.isdigit():
        value = int(value)
        r = int_to_Roman(value)
        s = f'Int: {value} -> Roman: {r}'
    else:
        try:
            r = roman_to_int(value)
            s = f'Roman: {value} -> Int: {r}'
        except KeyError:
            s = f'An error occured, perhas non roman numeral was provided? Only `I`, `V`, `X`, `L`, `C`, `D` and `M` are allowed'
    await self.message(data.channel_id, f'{s}')

@register(group='Global', help='Converts for example 3600s into 1h. Works with `s`, `m`, `h`, `d` and `w`', alias='', category='')
async def timeunits(self, *duration, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    from MFramework.utils.utils import secondsToText
    seconds = 0
    if duration == ():
        return await self.message(data.channel_id, "Provide value you want to convert for example `3540s 1m` as an argument")
    for d in duration:
        if 's' in d:
            seconds += int(d.split('s')[0])
        elif 'm' in d:
            seconds += int(d.split('m')[0])*60
        elif 'h' in d:
            seconds += (int(d.split('h')[0])*60)*60
        elif 'd' in d:
            seconds += ((int(d.split('d')[0])*24)*60)*60
        elif 'w' in d:
            seconds += (((int(d.split('w')[0]) * 7) * 24) * 60) * 60
        else:
            return await self.message(data.channel_id, "Pass `s` for second, `m` for minute, `h` for hour, `d` for day or `w` for week after right after digit as an argument, for example `60s 59m 23h`")
    await self.message(data.channel_id, secondsToText(seconds, language))

@register(group='Global', help='Shows current time in specified timezone(s)', alias='', category='')
async def timezone(self, yymmdd='YYYY-MM-DD', hhmm='HH:MM', *timezones, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    import pytz
    _timezones = []
    now = datetime.datetime.now()
    if ':' in yymmdd or (yymmdd.isdigit() and not hhmm.isdigit()):
        if 'HH:MM' != hhmm:
            timezones = [hhmm, *timezones]
        hhmm = yymmdd
        yymmdd = 'YYYY-MM-DD'
        year = now.year
        month = now.month
        day = now.day
    elif 'YYYY-MM-DD' != yymmdd and ('-' in yymmdd or yymmdd.isdigit()):
        yymmdd = yymmdd.split('-')
        if len(yymmdd) == 3:
            year = int(yymmdd[0])
            month = int(yymmdd[1])
            day = int(yymmdd[2])
        elif len(yymmdd) == 2:
            year = now.year
            month = int(yymmdd[0])
            day = int(yymmdd[1])
        else:
            year = now.year
            month = now.month
            day = int(yymmdd[0])
    elif yymmdd.lower() in ['tomorrow', 'yesterday']:
        now += datetime.timedelta(days=1 if yymmdd == 'tomorrow' else -1)
        year = now.year
        month = now.month
        day = now.day
    else:
        if yymmdd != 'YYYY-MM-DD':
            _timezones.append(yymmdd)
            yymmdd = 'YYYY-MM-DD'
        year = now.year
        month = now.month
        day = now.day
    if hhmm != 'HH:MM' and (':' in hhmm or hhmm.isdigit()):
        is_digit = hhmm.isdigit()
        has_colon = ':' in hhmm
        hhmm = hhmm.split(':')
        if len(hhmm) == 2:
            hour = int(hhmm[0])
            minute = int(hhmm[1])
        else:
            hour = int(hhmm[0])
            minute = 0
    else:
        if hhmm != 'HH:MM':
            _timezones.append(hhmm)
            hhmm = 'HH:MM'
        hour = now.hour
        minute = now.minute
    timezones = (*_timezones, *timezones)
    _timezones = []
    if 'in' in timezones or 'to' in timezones:
        if any(i == timezones[0] for i in ['in', 'to']):
            #use default
            from_timezone = 'UTC'
            timezones = timezones[1:]
        elif any(i == timezones[1] for i in ['in', 'to']):
            from_timezone = timezones[0]
            timezones = timezones[2:]
    else:
        #use default
        from_timezone = 'UTC'
    if yymmdd != 'YYYY-MM-DD' or hhmm != 'HH:MM' or from_timezone != 'UTC':
        if (('gmt+' in from_timezone.lower()) or ('gmt-' in from_timezone.lower())) and 'etc/' not in from_timezone.lower():
            from_timezone = from_timezone.lower().replace('gmt', 'Etc/GMT')
        try:
            _dt = pytz.timezone(from_timezone).localize(datetime.datetime(year, month, day, hour, minute, 0))
        except:
            return await self.message(data.channel_id, tr('commands.timezone.timezoneNotFound', language, from_timezone=from_timezone))#f"Couldn't find timezone {from_timezone}")
        #_dt = tz#datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=0, microsecond=0, tzinfo=tz)
        utc_dt = _dt.astimezone(pytz.timezone('UTC'))
        base = _dt.isoformat()
    else:
        base = data.timestamp
        utc_dt = datetime.datetime.fromisoformat(base)
        #tz = pytz.timezone('UTC').localize(datetime.datetime(utc_dt.year, utc_dt.month, utc_dt.day, utc_dt.hour, utc_dt.minute, utc_dt.second))
        _dt = utc_dt
    e = Embed().setFooter("", f"UTC {utc_dt.strftime('%Y-%m-%d %H:%M:%S')}").setTimestamp(base)
    if from_timezone != 'UTC':
        e.setDescription(f"{from_timezone}: {_dt.strftime('%Y-%m-%d %H:%M:%S %Z%z')}")
    for timezone in timezones:
        if 'gmt' in timezone.lower() and 'etc/' not in timezone.lower():
            timezone = timezone.lower().replace('gmt', 'Etc/GMT').replace('+','MINUS').replace('-','PLUS').replace('MINUS','-').replace('PLUS','+')
        try:
            #tz = pytz.timezone(timezone)
            #tz = tz.localize(datetime.datetime(_dt.year, _dt.month, _dt.day, _dt.hour, _dt.minute, 0))
            dt = _dt.astimezone(pytz.timezone(timezone))
            dt = dt.strftime('%Y-%m-%d %H:%M:%S %Z%z')
        except pytz.UnknownTimeZoneError:
            dt = tr('commands.timezone.notFound', language)
        except Exception as ex:
            dt = ex
        if len(e.fields) <= 25:
            e.addField(timezone, dt)
    await self.embed(data.channel_id, "", e.embed)

@register(group='Global', help='Makes text uʍop ǝpᴉsdn!', alias='', category='')
async def upsidedown(self, *text, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    import upsidedown
    await self.message(data.channel_id, upsidedown.transform(' '.join(text)))

@register(group='Global', help='Short description to use with help command', alias='', category='')
async def rot(self, *key, data, language, shift=13, alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZ', **kwargs):
    '''Extended description to use with detailed help command'''
    dict_alphabet = {}
    msg = '`'
    for x, letter in enumerate(alphabet):
        dict_alphabet[letter] = x
#        msg += f'{x+1+int(shift)}. {letter} '
#        if x % 5 == 0 and x != 0:
#            msg += '\n'
    shifted = ''
    for x, letter in enumerate(alphabet):
        y = int(x) + int(shift)
        if y > 25:
            y = y-26
        shifted += alphabet[y]
    msg += shifted
    msg += '`'
    from_key = ''
    new_key = []
    try_key = list(' '.join(key))
    for k in try_key:
        if not k.isdigit() and k.upper() in alphabet:
            new_key.append(dict_alphabet[k.upper()])
        else:
            new_key.append(' ')
    if new_key != []:
        key = new_key
    for k in key:
        try:
            _key = int(k) + int(shift)
            if _key > 25:
                _key = _key - 26
            from_key += alphabet[_key]
        except:
            from_key += k
    e = Embed().addField("Alphabet", f"`{alphabet}`\n"+msg).setDescription(from_key)
    await self.embed(data.channel_id, "", e.embed)

@register(group='Global', help='Converts Ascii to Numbers', notImpl=True)
async def asciitohex(self, *ascii_, data, **kwargs):
    ascii_ = ' '.join(ascii_)
    f = Embed().setTitle('Ascii to Hex').setDescription(ascii_)
    f.addField('Dec',str(int.from_bytes(bytearray(ascii_, 'ascii'),'big'))[2:1023])
    f.addField('Bin',str(bin(int.from_bytes(bytearray(ascii_, encoding='ascii'), 'big')))[2:1023])
    f.addField('Hex',str(hex(int.from_bytes(bytearray(ascii_, encoding='ascii'), 'big')))[2:1023])
    f.addField('Oct',str(oct(int.from_bytes(bytearray(ascii_, encoding='ascii'), 'big')))[2:1023])
    await self.embed(data.channel_id, '', f.embed)

@register(group='Global', help='Converts currency', alias='cc, currency')
async def currency_exchange(self, amount='1', currency='EUR', to_currency='USD', *args, data, language, fresh=False, **kwargs):
    def check(c):
        from MFramework.utils.utils import currencies
        return currencies.get(c, c).upper()
    if amount.isdigit() or '.' in amount or ',' in amount:
        amount = float(amount.replace(',', '.').replace(' ', ''))
    else:
        to_currency = currency
        currency = amount
        amount = 1
    currency, to_currency = check(currency), check(to_currency)
    if not fresh:
        r = requests.get(f"https://api.cryptonator.com/api/ticker/{currency}-{to_currency}", headers={"user-agent": "Mozilla"})
        result = r.json()
        try:
            result = result.get('ticker', {}).get('price', 0)
            result = "%3.2f" % (amount * float(result))
        except KeyError:
            result = result.get('error', 'Error')
    else:
        if currency.lower() in ['btc', 'ltc', 'eth']:
            #"https://api.crypto.com/v1/ticker/price" this might be useful for various other crypto -> usd or crypto -> crypto
            r = requests.get(f'https://api.crypto.com/v1/ticker?symbol={currency.lower()}usdt')
            try:
                result = r.json()['data']['last']
                result = "%3.2f" % (amount * float(result))
            except KeyError:
                result = r.json().get('msg', 'Error')
            to_currency = 'USD'
        else:
            r = requests.get(f'https://api.exchangeratesapi.io/latest?base={currency}&symbols={to_currency}')
            try:
                result = r.json()['rates'][to_currency]
                result = "%3.2f" % (amount * float(result))
            except KeyError:
                result = r.json().get('error','Error')
    r = tr('commands.currency_exchange.result', language, result=result, to_currency=to_currency, amount=amount, currency=currency)
    await self.message(data.channel_id, r)

@register(group='Global', help='Reverses letters', alias='', category='')
async def reverse(self, *message, data, language, inplace=False, **kwargs):
    '''Extended description to use with detailed help command'''
    if inplace:
        r = ' '.join([i[::-1] for i in message])
    else:
        r = ' '.join(message)[::-1]
    await self.message(data.channel_id, r)