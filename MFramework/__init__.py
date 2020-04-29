# -*- coding: utf-8 -*-
'''
MFramework
----------

Discord API framework with Database support.

:copyright: (c) 2020 Mmesek

'''
__name__ = "MFramework"
__version__ = "3.0"
__package__ = "MFramework"
__module__ = "MFramework"

import i18n
i18n.load_path.append("././locale")
#i18n.set('filename_format', '{locale}.{format}')
i18n.set('filename_format','{namespace}.{format}')
i18n.set('skip_locale_root_data', True)
from .utils.utils import log # noqa: F401
from .discord.mbot import Bot # noqa: F401

def import_from(dirname):
    import importlib, time, pkgutil, sys, os
    t = time.time()
    dirname = [dirname]+[os.path.join(dirname,o) for o in os.listdir(dirname) if os.path.isdir(os.path.join(dirname, o)) and '__' not in o]
    for importer, package_name, _ in pkgutil.iter_modules(dirname):
        full_package_name = '.'.join([importer.path.replace('\\','.').replace('/','.'), package_name])
        if full_package_name not in sys.modules:
            module = importlib.import_module(full_package_name)
    f = time.time()
    print("Loaded in:", f - t)
#import_from('commands')

def import_commands(path='commands'):
    from os.path import dirname
    import glob, time, importlib
    t = time.time()
    sub_modules = glob.glob(''.join((dirname(__file__)+'/.././'+path, '/**/*.py')), recursive=True)
    fm = [one.replace(dirname(__file__)+'/.././'+path,'').replace('/','.').replace('\\','.')[:-3] for one in sub_modules if '__' not in one]
    for o in fm:
        importlib.import_module(''.join([path, o]))
    f = time.time()
    print("Loaded in:", f - t)
#import_commands()
