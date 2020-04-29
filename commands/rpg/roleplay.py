from MFramework.commands import register

import re, random
@register(group="Vip", help="Roll the Die")
async def rtd(self, *args, data, **kwargs):
    reg = re.findall(r"\*.+\*",data.content)
    reeg = re.findall(r"\*\*.+\*\*",data.content)
    effect = {
        0:"Fail.",
        1:"Complete failure. Usually has a very negative effect.",
        2:"Failure. Not much happens.",
        3:"Partial success. The amount of success is determined by the GM.",
        4:"Success. The action was performed.",
        5:"Very successful. The action was performed in the most positive way.",
        6:"Too successful. The action was performed but backfires horribly.",
        7:"Epic Success."
    }
    if reg != reeg:
        for one in reg:
            roll = random.randrange(6)
            roll+=1
            try:
                bonus = re.search(r'(\+|\-)( ?)\d',one)
                print('Roll:',roll,'Bonus:', int(bonus[0][-1:]))
            except Exception as ex:
                print(ex)
                bonus = '0'
            if bonus[0][0] == '+':
                print('Executing +')
                if bonus[0][-1:] == '2' and roll == 4 or roll == 5:
                    print('4 or 5 that is')
                    roll = 7
                elif (int(bonus[0][-1:]) + roll) > 6:
                    print('Above 6?')
                    roll = 7
                else:
                    roll+=int(bonus[0][-1:])
            elif bonus[0][0] == '-':
                print('Executing -')
                if bonus[0][-1:] == '2' and roll == 2 or roll == 3:
                    roll = 0
                elif (roll - int(bonus[0][-1:])) < 1:
                    roll = 0
                else:
                    roll-=int(bonus[0][-1:])
            print('It should work')
            naw = re.findall(r"\*\(.+\)\*",data.content)
            if reg != naw:
                await self.message(data.channel_id, f"{data.author.username} performs action \"{one}\" with effect: [{roll}] {effect[roll]}")

