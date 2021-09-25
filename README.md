# MFramework.py
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Open in Visual Studio Code](https://open.vscode.dev/badges/open-in-vscode.svg)](https://open.vscode.dev/Mmesek/MFramework.py)

Low boilerplate command framework for Discord's REST API used by my bots like [M_Bot](https://github.com/Mmesek/MBot.py)

General usage bot's framework, originally made to use with Discord API

Reference:
- [Discord API](https://discordapp.com/developers/docs/intro)
- [Python Documentation](https://docs.python.org/3/)

Notes:
---
System package requirements:
```sh
sudo apt install libpq5
```

Required packages:
```sh
python3.7 pip install -r requirements.txt
```

Command example
```python
from MFramework import register, Groups, Context
@register(group=Groups.GLOBAL)
async def say(ctx: Context, text: str, i: int=1) -> str:
    '''
    Sends a specifed message x times and finishes with replying with Done
    Params
    ------
    text:
        Message to send
    i:
        Amount of times
    '''
    for x in range(i):
        await ctx.send(f"{text} x {x}")
    return "Done"
```
