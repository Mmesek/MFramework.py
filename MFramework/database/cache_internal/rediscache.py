from datetime import timedelta
import redis


class RDS:
    r: redis.Redis
    def __init__(self, address: str) -> None:
        self.r = redis.Redis(address)
    def _to_dict(self, value):
        if type(value) is bytes:
            import ujson
            value = ujson.loads(value)
        return value
    def _from_dict(self, value):
        if type(value) is dict:
            import ujson
            value = ujson.dumps(value)
        return value
    def add(self, name: str, value: str, expire_time: timedelta = None) -> str:
        value = self._from_dict(value)
        return self.r.set(name, value, ex=expire_time)
    def get(self, name: str) -> str:
        r = self.r.get(name)
        return self._to_dict(r)
    def update(self, name: str, new_value: str) -> str:
        new_value = self._from_dict(new_value)
        r = self.r.getset(name, new_value)
        return self._to_dict(r)
    def delete(self, name: str) -> str:
        return self.r.delete(name)
    def save(self):
        return self.r.save()
    def shutdown(self):
        return self.r.shutdown()
    def db_size(self):
        return self.r.dbsize()
    def has(self, name):
        return True if self.r.exists(name) else False
    def count(self, name):
        return self.r.exists(name)
    def keys(self, pattern):
        return self.r.keys(pattern)
