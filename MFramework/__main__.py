import asyncio, sys

from mlib import arguments
arguments.add("-clear_interactions", action='store_true', help="Specifies whether interactions should be cleared")
arguments.add("-clear_global_interactions", action='store_true', help="Specifies whether Global interactions should be cleared")
arguments.add("-clear_guild_interactions", action='store_true', help="Specifies whether Guild interactions should be cleared")
arguments.add("-generate_translations", action='store_true', help="Specifies whether translation file should be generated")
arguments.add("-update_translation", action='store_true', help="Specifies whether translation file should be updated")
arguments.add("-update-permissions", action="store_true", help="Specifies whether permissions should be forced to update in guilds")
arguments.add("paths", nargs="*", help="List of relative paths to import", default="bot")
arguments.add("--cfg", help="Specifies relative path to config", default="secrets.ini")

import MFramework
from mlib.import_functions import import_from
for path in arguments.parse().paths:
    import_from(path)

if '-generate-translation' in sys.argv or '-update-translation' in sys.argv:
    exit()

from mlib.config import ConfigToDict
from os.path import dirname, realpath
path = dirname(realpath('__file__'))+ f"/{arguments.parse().cfg}"
cfg = ConfigToDict(path)

db = MFramework.Database(cfg)
db.sql.create_tables()
from MFramework.database.alchemy import types
db.sql.extend_enums(types)

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

if __name__ == "__main__":
    from multiprocessing.dummy import Pool
    pool = Pool(3)
    try:
        while True:
            pool.map(run, cfg["DiscordTokens"])
    except KeyboardInterrupt:
        print("KeyboardInterrupt. Job done.")