import asyncio
import MFramework
#from os.path import dirname
#import glob, time, importlib
#__all__ = [ basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]
#t = time.time()
#sub_modules = glob.glob(''.join((dirname(__file__)+'/commands', '/**/*.py')), recursive=True)
#fm = [one.replace(dirname(__file__)+'/commands','').replace('/','.').replace('\\','.')[:-3] for one in sub_modules if '__' not in one]
#for o in fm:
#    importlib.import_module(''.join(['commands', o]))
#f = time.time()
#print("Loaded in:",f-t)
#print(fm)
MFramework.import_from('commands')

# Permission management with bit shifting?
# Bit shifting for permission calculation of Discord roles
# Better handling of starting multiple bots
# Roleplay character management
# Split Listener with Backend (Backend being sort of server and Listener being sort of a proxy)
#Embeds, Modernise memes above, fix sending DMs, perhaps store Quotes in database? Also dockets as a sort of generic data, in Influx maybe? 
#Sockets for Voice Connection
#Context Commands for multimessage commands, i.e, character management, minigames like card games or panstwa-miasta
#Stock simulation game?
#User profiles (birthdays etc)
#Spotify presence tracking
#Wolfram Alpha integration/support?
#Localized commands?
#UI for admin panel?
#Presence based on currently played song in Mopidy?

def run(token):
    asyncio.run(main(token))

async def main(token):
    b = MFramework.Bot(token)
    try:
        while True:
            try:
                await b.connection()
            except Exception as ex:
                print(ex)
            try:
                await b.msg()
                await asyncio.sleep(1)
                if b.state:
                    await b.close()
            except Exception as ex:
                print(ex)
    except KeyboardInterrupt:
        return
    except Exception as ex:
        MFramework.log(f"Main exception: {ex}")
    finally:
        try:
            await asyncio.sleep(1)
            if b.state:
                await b.close()
        except Exception as ex:
            MFramework.log(f"Clean up exception: {ex}")
from multiprocessing.dummy import Pool
pool = Pool(3)
from MFramework.utils.config import cfg
tokens = []
for token in cfg['DiscordTokens']:
    tokens += [token]

try:
    while True:
        pool.map(run, tokens)
except KeyboardInterrupt:
    print("KeyboardInterrupt. Job done.")
