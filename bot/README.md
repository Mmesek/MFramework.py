### Before starting bot:
Install dependecies:
```sh
$ pip install -r requirements.txt
```


### Obtaining tokens:
[Discord](https://discordapp.com/developers/applications/)
[Steam](http://www.steamcommunity.com/dev/apikey)
[Spotify](https://developer.spotify.com/dashboard/applications)
[Twitter](https://developer.twitter.com/en/apps)
[Twitch](https://dev.twitch.tv/console)

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
 
 
