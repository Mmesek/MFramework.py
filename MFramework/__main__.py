import sys

from mlib import arguments
from os.path import dirname, isfile, realpath

from mlib.config import ConfigToDict
from mlib.import_functions import import_from, import_modules

import MFramework

from MFramework.cache import Cache
from MFramework.cache.listeners import create_cache_listeners

arguments.add(
    "-clear_interactions",
    action="store_true",
    help="Specifies whether interactions should be cleared",
)
arguments.add(
    "-clear_global_interactions",
    action="store_true",
    help="Specifies whether Global interactions should be cleared",
)
arguments.add(
    "-clear_guild_interactions",
    action="store_true",
    help="Specifies whether Guild interactions should be cleared",
)
arguments.add(
    "-generate_translations",
    action="store_true",
    help="Specifies whether translation file should be generated",
)
arguments.add(
    "-update_translation",
    action="store_true",
    help="Specifies whether translation file should be updated",
)
arguments.add(
    "-update-permissions",
    action="store_true",
    help="Specifies whether permissions should be forced to update in guilds",
)
arguments.add("paths", nargs="*", help="List of relative paths to import", default=["bot"])
arguments.add("--cfg", help="Specifies relative path to config", default="secrets.ini")
arguments.add(
    "--ext",
    help="Path to directory with extensions to load (Packages containing __init__.py)",
    default="extensions",
)

try:
    for path in arguments.parse().paths:
        import_from(path)
    import_modules(arguments.parse().ext)
except Exception as ex:
    MFramework.log.exception(ex, exc_info=ex)

if "-generate-translation" in sys.argv or "-update-translation" in sys.argv:
    from MFramework.utils.localizations import update_all_localizations

    update_all_localizations()
    exit()

default_cfg = {"DiscordTokens": {"bot": "YOUR_TOKEN"}, "bot": {"alias": "!"}}

if isfile("/proc/self/cgroup") and any("docker" in line for line in open("/proc/self/cgroup")):
    default_cfg.update({
        "redis": {"host": "redis"},
        "Database": {
            "db": "postgresql+psycopg2",
            "user": "postgres",
            "password": "postgres",
            "location": "postgres",
            "name": "postgres",
            "port": 5432,
            "echo": False,
        },
    })

path = dirname(realpath("__file__")) + f"/{arguments.parse().cfg}"
cfg = ConfigToDict(path, default_cfg)

db = MFramework.Database(cfg)
db.sql.create_tables()

cache = {0: {}}  # MFramework.database.cache.MainCache(cfg)
# cache = MFramework.Cache(cfg)


create_cache_listeners(Cache)


def run(name):
    MFramework.Bot.run(name=name, cfg=cfg, db=db, cache=cache)


if __name__ == "__main__":
    from multiprocessing.dummy import Pool

    pool = Pool(tokens := len(cfg["DiscordTokens"]))
    try:
        while True:
            if tokens == 1:
                run(next(iter((cfg["DiscordTokens"]))))
            else:
                pool.map(run, cfg["DiscordTokens"])
    except KeyboardInterrupt:
        print("KeyboardInterrupt. Job done.")
