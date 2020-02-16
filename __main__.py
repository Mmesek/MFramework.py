from bot.discord.mbot import Bot
from bot.utils.utils import log
import asyncio


async def cancelTasks():
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    [print(task.get_stack()) for task in tasks]
    [task.cancel() for task in tasks]
    print(f"Cancelling {len(tasks)} tasks")
    await asyncio.gather(*tasks, return_exceptions=True)


async def shutdown(loop, bot=None):
    if bot:
        bot.keepConnection = False
        await bot.close()
        await asyncio.sleep(0)
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    [print(task.get_stack()) for task in tasks]
    [task.cancel() for task in tasks]
    print(f"Cancelling {len(tasks)} tasks")
    await asyncio.gather(*tasks, return_exceptions=True)
    loop.stop()


async def handle_exception(loop, context):
    msg = context.get("exception", context["message"])
    print(f"Handling exception: {msg}")
    log(f"Caught exception: {msg}")
    asyncio.create_task(shutdown(loop))


def run():
    asyncio.run(main())

async def main():
    b = Bot()
    await b.connection()
    try:
        await b.msg()
    except Exception as ex:
        log(f"Main exception: {ex}")
    finally:
        try:
            await asyncio.sleep(1)
            if b.state:
                await b.close()
        except Exception as ex:
            log(f"Clean up exception: {ex}")


try:
    while True:
        run()
except KeyboardInterrupt:
    print("KeyboardInterrupt. Job done.")

