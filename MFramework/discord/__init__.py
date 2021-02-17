# -*- coding: utf-8 -*-
'''
Discord API
----------

Discord API.

:copyright: (c) 2020 Mmesek

'''

Dispatch = {}

async def aInvalid(*args, **kwargs):
    pass

def Invalid(*args, **kwargs):
    pass

def onDispatch(f):
    def inner(f):
        if f.__name__.upper() not in Dispatch:
            Dispatch[f.__name__.upper()] = []
        Dispatch[f.__name__.upper()].append(f)
        return f
    return inner(f)

class Deserializer:
    def __init__(self):
        import zlib
        self._buffer = bytearray()
        self._zlib = zlib.decompressobj()
    def __call__(self, msg: bytes):
        import ujson as json
        if type(msg) is bytes:
            self._buffer.extend(msg)
            if len(msg) >= 4:
                if msg[-4:] == b'\x00\x00\xff\xff':
                    msg = self._zlib.decompress(self._buffer).decode('utf-8')
                    self._buffer = bytearray()
                else:
                    return
            else:
                return
        from .objects import Gateway_Payload
        return Gateway_Payload(**json.loads(msg)) #TODO: Cast to object, not just json here!
