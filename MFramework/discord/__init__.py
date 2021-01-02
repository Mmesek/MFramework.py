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
        Dispatch[f"{f.__name__.upper()}"] = f
        return f
    return inner(f)