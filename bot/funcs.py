from discord.commands import register

import utils 
import asyncio


@register(group='Mod',help='[user] [reason] - Warns user.')
async def warn(self, data):
    uid = data['mentions'][0]['id']
    reason = data['content'].split(' ',2)
    guild = await self.endpoints.get_guild(data['guild_id'])['name']
    cid = await self.endpoints.make_dm(uid)
    result = await self.endpoints.message(cid['id'], f"You've been warned in {guild} server for {reason[2]}")
    if 'code' in result:
        return await self.endpoints.message(data['channel_id'],f"Couldn't deliver Warning to user <@{uid}> due to: {result['message']}")
    return await self.endpoints.message(data['channel_id'],f"Delivered Warning to user <@{uid}> for: {reason[2]}")

@register(group='Mod',help='[user] (time) [reason] - Mutes user.')
async def mute(self, data):
    uid = data['mentions'][0]['id']
    reason = data['content'].split(' ',2)
    guild = await self.endpoints.get_guild(data['guild_id'])['name']
    cid = await self.endpoints.make_dm(uid)
    result = await self.endpoints.message(cid['id'], f"You've been muted in {guild} for {reason[2]}")
    if 'code' in result:
        return await self.endpoints.message(data['channel_id'],f"Couldn't deliver mute reason to user <@{uid}> due to: {result['message']}")
    return await self.endpoints.message(data['channel_id'],f"Delivered mute reason to user <@{uid}> for: {reason[2]}")

@register(group='Mod',help='[user] (time) [reason] - Bans user.')
async def ban(self, data):
    uid = utils.param(data['content'])[0]
    if data['mentions'] != []:
        uid=f"<@{uid}>"
    await self.endpoints.message(data['channel_id'],f"<:pege:644033864704196649> 🔨 {uid}")

@register(group='Mod',help='[amount] (channel) - Purges previous message in channel.')
async def purge(self, data):
    pass

@register(group='Mod',help='[emoji] [role] - Allows only specified role access certain emoji')
async def lock_emoji(self, data):
    pass

@register(group='Admin',help='[user] [message] - Sends user DM as a bot')
async def send_dm(self, data):
    con = data['content'].split(' ',2)
    if 'mentions' in data != []:
        uid = data['mentions'][0]['id']
    else:
        uid = con[1].replace('<','').replace('@','').replace('>','').replace('&','')
    if '\\' in con[2]:
        con[2] = con[2].replace('\\','')
    if 'a:' in con[2]:
        con[2] = con[2].replace('a:','<a:')
    dm = await self.endpoints.make_dm(uid)
    await self.endpoints.message(dm['id'], con[2])

@register(group='Admin',help='(channel) [message] - Sends message to a channel as a bot')
async def send_message(self, data):
    part = data['content'].split(' ', 2)
    channel = part[1].replace('<','').replace('#','').replace('>','')
    print(channel, part)
    await self.endpoints.message(channel, part[2])

@register(group='Admin',help='(channel) [messageID] [reaction] - Reacts to a message with emoji as a bot')
async def react(self, data):
    print('Reeeeact')
    part = data['content'].split(' ',2)
    chap = part[2].split(' ')
    for each in chap:
        await self.endpoints.react(data['channel_id'],part[1],each.replace('<:','').replace('>',''))
        await asyncio.sleep(0.3)

@register(group='Admin',help="(channel) [messageID] [newMessage] - Edits bot's message")
async def edit_message(self, data):
    part = data['content'].replace('<','').replace('#','').replace('>','').split(' ',3)
    await self.endpoints.edit(part[1],part[2],part[3],0)

@register(group='Admin',help="[emoji ..] [role] - Allows only specific role access to emoji's")
async def edit_emoji(self, data):
    part = data['content'].split(' ')
    for split in part:
        if '<:' in split:
            part2 = split.replace('\\<:','').replace('>','').replace(':',' ').split(' ',2)
            print("Modified emoji: ", await self.endpoints.modify_emoji(data['guild_id'],part2[1],part2[0],[part[1]]))
            await asyncio.sleep(2.5)

@register(group='Admin',help='[Embed] - Sends message in embed')
async def make_embed(self, data):
    pass

@register(group='Admin',help='[name of animated emoji] - Sends animated emoji')
async def aemoji(self, data):
    emojis = await self.endpoints.get_emoji(data['guild_id'])
    e = data['content'].split(' ')[1:]
    message=''
    for one in e:
        for emoji in emojis:
            if emoji['name'] == one:
                if emoji['animated']:
                    message += f"<a:{emoji['name']}:{emoji['id']}> "
                else:
                    message += f"<:{emoji['name']}:{emoji['id']}> "
    try:
        await self.endpoints.delete(data['channel_id'],data['id'])
        await self.endpoints.message(data['channel_id'],message)
    except Exception as ex:
        print(ex)

@register(group='Admin',help="- Lists all available emoji's in guild")
async def list_emoji(self, data):
    emojis = await self.endpoints.get_emoji(data['guild_id'])
    elist = ""
    for emoji in emojis:
        if emoji['animated']:
            elist+=f"\n> <a:{emoji['name']}:{emoji['id']}> - \\<a:{emoji['name']}:{emoji['id']}>"
        elif 'all' in data['content']:
            elist+=f"\n> <:{emoji['name']}:{emoji['id']}> - \\<:{emoji['name']}:{emoji['id']}>"
    await self.endpoints.message(data['channel_id'], elist[:2000])

@register(group='Admin',help="(channel) [message] - Delete's message")
async def delete(self, data):
    chop = data['content'].split(' ',2)
    channel = chop[1]
    message = chop[2]
    print(channel, message)
    await self.endpoints.delete(channel, message)


import re, random

@register(help="(number) - Rolls Random Number")
async def rd(self, data):
    reg = re.search(r'\d+',data['content'])
    await self.endpoints.message(data['channel_id'],str(reg.group(0))+': '+str(random.randrange(int(reg.group(0)))))


@register(help='(decode) [message] - Decodes or Encodes message in Morse')
async def morse(self, data):
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
        'Ĝ':'--.-.','Ĵ':'.---.','Ś':'...-...','Þ':'.--..','Ź':'--..-.','Ż':'--..-',
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
                cipher+=morse_dict['-']+' '
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
            if letter not in '.-' and letter is not ' ':
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
    if 'decode' in data['content']:
        reward = decrypt(data['content'].split('decode ',1)[1])
        org = data['content'].split('decode ',1)[1]
        t = "Morse -> Normal"
    else:
        reward = encrypt(data['content'].split(' ',1)[1])
        org = data['content'].split(' ',1)[1]
        t = "Normal -> Morse"
    await self.endpoints.embed(data['channel_id'], 'Orginal: '+org, {"title":t,"description":reward})

import time, datetime
@register(help="[link] - Quotes message")
async def quote(self, data):
    url = data['content'].split(' ')
    if len(url) > 1:
        url = url[1]
    else:
        url = url[0]
    mid = url.split('channels/')[1].split('/')
    message = await self.endpoints.get_message(mid[1],mid[2])
    embed = utils.Embed().setDescription('>>> '+message['content']).setTimestamp(message['timestamp'])
    embed.setAuthor(message['author']['username']+'#'+message['author']['discriminator'],url,f"https://cdn.discordapp.com/avatars/{message['author']['id']}/{message['author']['avatar']}")
    embed.addField("Channel",f"<#{mid[1]}>",True).addField("Quoted by",f"<@{data['author']['id']}>",True)
    if message['edited_timestamp'] != None:
        embed.addField("Edited at",str(time.strftime("%Y-%m-%d %H:%M:%S",datetime.datetime.fromisoformat(message['edited_timestamp']).timetuple())), True)
    await self.endpoints.embed(data['channel_id'],'',embed.embed)
    await self.endpoints.delete(data['channel_id'],data['id'])

@register(help="Retrives messages from DM", group="Admin")
async def getmessagesfromdm(self, data):
    s = data['content'].split(' ',2)
    dm = await self.endpoints.make_dm(s[1])
    print(dm)
    messages = await self.endpoints.get_messages(dm['id'],dm['last_message_id'])
    message = ''
    for each in messages:
        print(each['author'],each['content'])
        message+=f"[{each['id']}] - {each['author']['username']}: {each['content']}"
    await self.endpoints.embed(data['channel_id'],'',{"title":dm['id'],"description":message})








import pickle
from collections import namedtuple
import numpy as np
from utils import timed
_model = None

Scores = namedtuple("Scores", ["toxic", "severe_toxic",
                               "obscence", "insult", "identity_hate"])
@timed
async def warm(model_path):
    global _model
    if _model is None:
        with open("data/pipeline.dat",'rb') as fp:
            pipeline = pickle.load(fp)
            _model = pipeline
    return True
@timed
async def predict(message):
    results = _model.predict_proba([message])
    results = np.array(results).T[1].tolist()[0]
    return Scores(*results)
@timed
async def mod(self, data):
    await warm(0)
    scores = await predict(data["content"])
    print(scores)
    if np.average([scores.toxic, scores.insult]) >= 0.4:
        await self.endpoints.message(data['channel_id'], f'Detected averange of Toxicity and Insult above set value: {scores.toxic} and {scores.insult}')


#import os, time
#@register(group='Admin',help='Shows temperature of Raspberry')
#def measure_temp():
#    temp = os.popen("vcgencmd measure_temp").readline()
#    return (temp.replace("temp=",""))
#@register(group='Admin',help='Shows uptime of Raspberry')
#def uptime():
#    ut = os.popen("uptime -p").readline()
#    return (ut.replace('up ',''))
#@register(group='Admin',help='Pings discord servers and shows the result')
#def ping():
#    ping = os.popen("ping -c 4 www.discordapp.com") 
#    for line in ping:
#        lastline=line
#    return lastline