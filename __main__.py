import asyncio

import MFramework
MFramework.import_from('commands-slash')
import MFramework.utils.config as config
import MFramework.database.database
cfg = config.cfg

db = MFramework.database.database.Database(cfg)
db.sql.create_tables()

cache = {"dm": {}}  #MFramework.database.cache.MainCache(cfg)


async def main(name):
    b = MFramework.Client(name, cfg, db, cache)
    while True:
        try:
            await b.connection()
            await b.msg()
        except KeyboardInterrupt:
            return
        except Exception as ex:
            MFramework.log(f"Uncaught Exception: {ex}")
        finally:
            await asyncio.sleep(1)
            if b.connected:
                await b.close()

def run(name):
    asyncio.run(main(name))

from multiprocessing.dummy import Pool
pool = Pool(3)
try:
    while True:
        pool.map(run, cfg["DiscordTokens"])
except KeyboardInterrupt:
    print("KeyboardInterrupt. Job done.")