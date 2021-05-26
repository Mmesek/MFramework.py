import asyncio, sys

import MFramework
from mlib.import_functions import import_from
import_from('dispatch')
import_from('commands_slash')
import_from('commands')
if '-generate-translation' in sys.argv or '-update-translation' in sys.argv:
    exit()

from mlib.config import ConfigToDict
from os.path import dirname
path = dirname(__file__)+"/data/secrets.ini"
cfg = ConfigToDict(path)

db = MFramework.Database(cfg)
db.sql.create_tables()

cache = {0: {}}  #MFramework.database.cache.MainCache(cfg)
#cache = MFramework.Cache(cfg)


async def main(name):
    b = MFramework.Bot(name, cfg, db, cache)
    while True:
        async with b:
            try:
                await b.receive()
            except KeyboardInterrupt:
                return
            except Exception as ex:
                MFramework.log.critical(f"Uncaught Exception: {ex}")

def run(name):
    asyncio.run(main(name))

from multiprocessing.dummy import Pool
pool = Pool(3)
try:
    while True:
        pool.map(run, cfg["DiscordTokens"])
except KeyboardInterrupt:
    print("KeyboardInterrupt. Job done.")