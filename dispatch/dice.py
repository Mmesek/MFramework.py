import re, random
async def roll(self, data, update=False):
    if update:
        m = await self.get_channel_message(data.channel_id, data.id)
        if m.reactions:
            return
    reg = re.findall(r"(?:(?=\*)(?<!\*).+?(?!\*\*)(?=\*))", data.content)
    if reg and set(reg) != {'*'}:
        if '*' in reg:
            reg = set(reg)
            reg.remove('*')
            reg = list(reg)
        v = random.SystemRandom().randint(1, 6)
        reactions = {
            0:'0️⃣',
            1:'1️⃣',2:'2️⃣',3:'3️⃣',
            4:'4️⃣',5:'5️⃣',6:'6️⃣'
        }
        dices = {
            0:'dice_0:761760091648294942',
            1:'dice_1:761760091971780628',2:'dice_2:761760091837825075',3:'dice_3:761760092206792750',
            4:'dice_4:761760092767911967',5:'dice_5:761760093435068446',6:'dice_6:761760093817143345'
        }
        z = re.findall(r"(?i)zabij|wyryw|mord", reg[0])
        if z:
            v = 0
        r = reactions.get(v) if self.user_id != 372187189087567872 else dices.get(v)
        await self.create_reaction(data.channel_id, data.id, r)
