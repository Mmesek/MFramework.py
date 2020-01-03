### Before starting bot:
Install dependecies:
```sh
$ pip install -r requirements.txt
```
Configure tokens in `/bot/data/secrets.ini`

### Start bot:
```sh
$ cd bot
$ python main.py
```

### Create new commands with:
```python
@register(group='group', help='Short description to use with help command', alias='trigger')
async def commandTrigger(data):
'''Extended description to use with detailed help command'''
  pass
 ```
 
 
