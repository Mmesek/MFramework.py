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