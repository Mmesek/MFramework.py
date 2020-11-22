import asyncio
import MFramework

MFramework.import_from('commands')


def run(token):
    asyncio.run(main(token))

async def main(token):
    b = MFramework.Bot(token)
    try:
        while True:
            try:
                await b.connection()
            except Exception as ex:
                if "name resolution" in ex:
                    await asyncio.sleep(10)
                else:
                    print(ex)
            try:
                await b.msg()
                await asyncio.sleep(1)
                if b.state:
                    await b.close()
            except Exception as ex:
                if "name resolution" in ex:
                    await asyncio.sleep(10)
                else:
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
