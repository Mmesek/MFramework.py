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
        z = re.findall(r"(?i)zabij|wyryw|mord", reg[0])
        if z:
            v = 0
        await self.create_reaction(data.channel_id, data.id, reactions.get(v))
