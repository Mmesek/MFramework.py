import asyncio
from ..database import alchemy as db

tasks = {}

def scheduledTask(func):
    tasks[func.__name__.lower()] = func
    return func

def add_guild_tasks(self, guild_id):
    session = self.db.sql.session()
    _tasks = session.query(db.Tasks).filter(db.Tasks.GuildID == guild_id).filter(db.Tasks.Finished == False).all()
    for task in _tasks:
        _appendTasksToCache(self, task)

def add_task(self, guild_id, type, channel_id, message_id, author_id, timestamp, finish, prize, winner_count, finished=False):
    s = self.db.sql.session()
    task = db.Tasks(guild_id, type, channel_id, message_id, author_id, timestamp, finish, prize, winner_count, finished)
    self.db.sql.add(task)
    _appendTasksToCache(self, task)

def _appendTasksToCache(self, task, *args, **kwargs):
    cache = self.cache[task.GuildID].tasks
    if task.Type not in cache:
        cache[task.Type] = {}
    cache[task.Type][int(task.MessageID)] = asyncio.create_task(tasks.get(task.Type)(self, task, *args, **kwargs))



async def wait_for_scheduled_task(self, TimestampEnd):
    from datetime import datetime, timezone
    delta = (TimestampEnd - datetime.now(tz=timezone.utc)).total_seconds()
    if delta > 0:
        await asyncio.sleep(delta)
    return True
