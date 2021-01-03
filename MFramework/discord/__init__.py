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