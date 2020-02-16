from os.path import dirname#, basename, isfile, join, isdir
import glob
#modules = glob.glob(join(dirname(__file__), "*.py"))
#__all__ = [ basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]
sub_modules = glob.glob(f'{dirname(__file__)}/**/*.py',recursive=True)
fm=[]
import importlib
for one in sub_modules:
    if '__' in one:
        continue
    p = dirname(__file__)
    o = one.replace(f'{p}\\','').replace(f'{p}/','').replace('\\','.').replace('.py','').replace('/','.')
    importlib.import_module(f'bot.command.{o}')
    fm+=[o]
print(fm)
