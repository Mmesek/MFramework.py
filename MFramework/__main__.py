import asyncio, sys

from mlib import arguments
arguments.add("-clear_interactions", action='store_true', help="Specifies whether interactions should be cleared")
arguments.add("-clear_global_interactions", action='store_true', help="Specifies whether Global interactions should be cleared")
arguments.add("-clear_guild_interactions", action='store_true', help="Specifies whether Guild interactions should be cleared")
arguments.add("-generate_translations", action='store_true', help="Specifies whether translation file should be generated")
arguments.add("-update_translation", action='store_true', help="Specifies whether translation file should be updated")
arguments.add("-update-permissions", action="store_true", help="Specifies whether permissions should be forced to update in guilds")
arguments.add("paths", nargs="*", help="List of relative paths to import", default=["bot"])
arguments.add("--cfg", help="Specifies relative path to config", default="secrets.ini")
arguments.add("--ext", help="Path to directory with extensions to load (Packages containing __init__.py)", default="extensions")

import MFramework
from mlib.import_functions import import_from, import_modules

try:
    for path in arguments.parse().paths:
        import_from(path)
    import_modules(arguments.parse().ext)
except Exception as ex:
    print(ex)

if '-generate-translation' in sys.argv or '-update-translation' in sys.argv:
    exit()

from mlib.config import ConfigToDict
from os.path import dirname, realpath, isfile

default_cfg = {
    "DiscordTokens":{
        "bot":"YOUR_TOKEN"
    },
    "bot":{
        "alias":"!"
    }
}

if isfile("/proc/self/cgroup") and any("docker" in line for line in open("/proc/self/cgroup")):
    default_cfg.update({
        "redis":{
            "host":"redis"
        }, 
        "Database":{
            "db":"postgresql+psycopg2", 
            "user":"postgres", 
            "password":"postgres", 
            "location":"postgres", 
            "name":"postgres", 
            "port":5432, 
            "echo":False
        }
    })

path = dirname(realpath('__file__'))+ f"/{arguments.parse().cfg}"
cfg = ConfigToDict(path, default_cfg)

db = MFramework.Database(cfg)
db.sql.create_tables()
from MFramework.database.alchemy import types
db.sql.extend_enums(types)

cache = {0: {}}  #MFramework.database.cache.MainCache(cfg)
#cache = MFramework.Cache(cfg)

from MFramework.database.cache import Cache
from MFramework.database.cache.listeners import create_cache_listeners
create_cache_listeners(Cache)

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