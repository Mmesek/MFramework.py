### Before starting bot:
Install dependecies:
```sh
$ sudo apt install python3-numpy python3-sklearn python3-scipy python3-scikit-learn python3-pandas
$ pip install -r requirements.txt
```


### Obtaining tokens:
[Discord](https://discordapp.com/developers/applications/)
[Steam](http://www.steamcommunity.com/dev/apikey)
[Spotify](https://developer.spotify.com/dashboard/applications)
[Twitter](https://developer.twitter.com/en/apps)
[Twitch](https://dev.twitch.tv/console)

Generate config file by running bot once.

Configure tokens in `data/secrets.ini`

### Start bot:
```sh
$ python __main__.py
```

### Create new commands with:
```python
@register(group='group', help='Short description to use with help command', alias='trigger', category='Command Category')
async def commandTrigger(self, *args, data, language, **kwargs):
'''Extended description to use with detailed help command'''
    await self.create_message(channel_id, content, embed, allowed_mentions)
```
