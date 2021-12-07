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

## Examples

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

Button example
```python
from MFramework import Context, Button, Select
class CoolButton(Button):
    @classmethod
    async def execute(self, ctx: Context, data: str):
        # Any kind of logic that happens upon pressing a button
        pass
```

Select Button example
```python
from typing import List
from MFramework import Context, Select, Select_Option
class NiceSelection(Select):
    @classmethod
    async def execute(self, ctx: Context, data: str, values: List[str], not_selected: List[Select_Option]):
        # Any kind of logic that happens upon selecting options from Menu
        pass
```

Using components example
```python
from MFramework import Row
@register(group=Groups.GLOBAL)
async def new_cool_button(ctx: Context, cool_argument: str = "It's cool! Trust!") -> CoolButton:
    '''
    Sends new message with cool button
    Params
    ------
    cool_argument:
        Label's text of this button
    '''
    return CoolButton(label=cool_argument)

@register(group=Groups.GLOBAL)
async def new_cool_button(ctx: Context, name: str = "Cool Option") -> List[Row]:
    '''
    Sends new message with 2 rows, first with Selection with two options and second with two buttons
    Params
    ------
    name:
        name of first option
    '''
    rows = [
        Row(
            NiceSelection(
                Option(
                    label=name, value=123
                ),
                Option(
                    label="Second option", value=256
                ),
                placeholder= "Options"
            )
        ),
        Row(
            CoolButton(label="Cool Button!", style=Button_Styles.SECONDARY),
            Button(label="Not cool button", style=Button_Styles.DANGER)
        )
    ]
    return rows
```
