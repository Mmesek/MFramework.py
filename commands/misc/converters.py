from MFramework.commands import register

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
