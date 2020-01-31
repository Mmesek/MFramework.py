from bot.discord.commands import register
import re, random

@register(help="(number) - Rolls Random Number")
async def rd(self, data):
    reg = re.search(r'\d+',data['content'])
    await self.endpoints.message(data['channel_id'],str(reg.group(0))+': '+str(random.randrange(int(reg.group(0)))+1))


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
                cipher+='/'
#                cipher+=morse_dict['-']+' '
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
    if 'decode' in data['content']:
        reward = decrypt(data['content'].split('decode ',1)[1])
        org = data['content'].split('decode ',1)[1]
        t = "Morse -> Normal"
    else:
        reward = encrypt(data['content'])
        org = data['content']
        t = "Normal -> Morse"
    await self.endpoints.embed(data['channel_id'], 'Orginal: '+org, {"title":t,"description":reward})


@register(group='System', help='name, url, language, color - Add RSS to watchlist')
async def add_rss(self, data):
    params = data['content'].split(',')
    src = params[0]
    url = params[1]
    language = params[2]
    color = params[3]
    await self.db.insert('RSS','Source, Last, URL, Language, Color',[src, 0, url, language, color])

@register(group='System', help='channel, name, [content] - Sub current channel to a RSS source')
async def sub_rss(self, data):
    params = data['content'].split(',')
    if '/' in params[0]:
        webhook = params[0]
    else:
        channel = params[0]
        webhooks = await self.endpoints.get_webhooks(channel)
        for wh in webhooks:
            if 'user' in wh and wh['user'] == self.user_id:
                webhook = f"{wh['id']}/{wh['token']}"
                break
            elif 'RSS' in wh['name']:
                webhook = f"{wh['id']}/{wh['token']}"
                break
    if webhook is None:
        await self.endpoints.create_webhook(channel, 'RSS', f"Requested by {data['author']['username']}")
    src = params[1]
    if len(params) > 2:
        content = params[2]
    else:
        content = ''
    await self.db.insert('Webhooks','GuildID, Webhook, Source, Content, AddedBy',
                            [data['guild_id'],webhook, src, content, data['author']['id']])


@register(group='System',help='spotifyID artist - Add Artist to tracking new releases')
async def addSpotify(self, data):
    s = data['content'].split(' ',1)
    sid = s[0]
    artist = s[1]
    await self.db.insert('Spotify','SpotifyID, Artist, AddedBy',[sid, artist, data['author']['id']])
from bot.api import Spotify
@register(group='System',help='Fetch new spotify releases')
async def spotify(self, data):
    s = Spotify()
    await s.connect()
    try:
        embed = await s.makeList(db=self.db)
    finally:
        await s.disconnect()
    if '-w' not in data['content']:
        await self.endpoints.embed(data['channel_id'],'',embed)
    elif '-w' in data['content']:
        w = await self.db.selectMultiple('Webhooks','webhook, content', 'WHERE Source=?',['Spotify'])
        for one in w:
            await self.endpoints.webhook([embed], one[1], one[0], "Spotify", "https://images-eu.ssl-images-amazon.com/images/I/51rttY7a%2B9L.png")

from bot.rss import rss
@register(group='System', help='Fetch RSS manually')
async def fetch_rss(self, data):
    await rss(self, 'pl')