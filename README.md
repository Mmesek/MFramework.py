# MFramework.py
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![GitHub](https://img.shields.io/github/license/Mmesek/MFramework.py)](../../LICENSE.md)
[![Open in Visual Studio Code](https://img.shields.io/static/v1?logo=visualstudiocode&label=&message=Open%20in%20Visual%20Studio%20Code&labelColor=2c2c32&color=007acc&logoColor=007acc)](https://open.vscode.dev/Mmesek/MFramework.py)

[![CodeFactor Grade](https://img.shields.io/codefactor/grade/github/Mmesek/MFramework.py)](https://www.codefactor.io/repository/github/mmesek/mframework.py)
[![Lines of code](https://sloc.xyz/github/Mmesek/MFramework.py)]()
[![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/Mmesek/MFramework.py)]()
[![GitHub repo size](https://img.shields.io/github/repo-size/Mmesek/MFramework.py)]()

[![GitHub issues](https://img.shields.io/github/issues/Mmesek/MFramework.py)](../../issues)
[![GitHub pull requests](https://img.shields.io/github/issues-pr/Mmesek/MFramework.py)](../../pulls)
[![GitHub contributors](https://img.shields.io/github/contributors/Mmesek/MFramework.py)](../../graphs/contributors)
[![Discord](https://img.shields.io/discord/517445947446525952)](https://discord.gg/gXWvDzNcMD)

[![Docker Image Size (latest by date)](https://ghcr-badge.egpl.dev/Mmesek/mframework/size?tag=main)](../../pkgs/container/mframework)
---

Low boilerplate command framework for Discord's REST API with Database, external Cache, Localization, Event Logging support and more.
Bleeding-edge low boilerplate command framework for Discord's REST API extending [mDiscord](https://github.com/Mmesek/mdiscord) wrapper. Batteries Included.


## Features
- Command's [metadata](MFramework/commands/command.py) inferred from Python syntax itself
- Dual availability of [commands](MFramework/commands/runner.py) - define once and use as either message or interaction based
- Implicit [modals](MFramework/commands/runner.py) inferred from argument typehints available as modal or message-based argument polling depending on invocation
- [Hierarchy](MFramework/commands/__init__.py)-based internal permission system
- [Reaction](MFramework/commands/decorators.py)-based commands
- Basic extendable runtime-defined message custom command [parser](MFramework/commands/parser.py)
- Webhook-based [logging](MFramework/utils/log.py) of Discord events
- [Leaderboard](MFramework/utils/leaderboards.py) builder
- Built-in [Database](MFramework/database/alchemy/) support (SQLAlchemy)
- Built-in remote [cache](MFramework/database/cache_internal/models.py) support (Redis)
- Built-in [localization](MFramework/context.py) support (i18n)
- Run as [module](MFramework/__main__.py)
- Easly extendable

## Features against using it
- Volatile
- Repository was used as a monorepo and a "testbed" for unrelated features, certain parts were moved to separate repositories however there are still remnants of them here
- Barely any documentation
- Horror in internal files

## Installation
---
System package requirements for Postgres support:
```sh
sudo apt install libpq5
```

Required packages:
```sh
python3 -m pip install -r requirements.txt
```

# Examples

More examples can be found directly in my [M_Bot](https://github.com/Mmesek/MBot.py) repo.

Unlike other libraries, there is no `bot` or `cog` - everything is registered globally and a lot of information is taken from docstrings and function signatures, mainly for ease of extending.

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

Modal example
```py
from MFramework import register, Groups, Context, Embed
from MFramework.commands.components import TextInput

@register(group=Groups.GLOBAL)
async def suggestion(ctx: Context, title: TextInput[1, 100], your_suggestion: TextInput[1, 2000]) -> Embed:
    '''
    Make a Suggestion!
    Params
    ------
    title:
        Title of suggestion
    your_suggestion:
        Your suggestion
    '''
    return Embed(title=title).set_description(your_suggestion)
```

Autocomplete example
```python
from MFramework import register, Groups, Context, Interaction

async def animals(interaction: Interaction, current: str) -> list[str]:
    """Current represents what user typed so far"""
    return ["Sheep", "Dog", "Cat"]

@register(group=Groups.GLOBAL)
async def choose(ctx: Context, animal: animals) -> str:
    """
    Choose an animal
    Params
    ------
    animal:
        Autocomplete that suggests animal names
    """
    return f"Selected animal: {animal}"
```

Localization example
---

`locale/en-US/bot.json`
```json
{
    "hi": {
        "hello": "Hello!"
    }
}
```

`locale/pl/bot.json`
```json
{
    "hi": {
        "hello": "Cześć!"
    }
}
```

`bot.py`
```py
@register(group=Groups.GLOBAL)
async def hi(ctx: Context) -> str:
    '''Replies in your language'''
    return ctx.t("hello")
```

# Running Bot

## Docker

###### Note: This section is not entirely tested, it's more a PoC rather than final version

via docker compose
```sh
docker-compose up
```

Manually
```sh
docker run -it \
    -v data:/app/data \
    -v bot:/app/bot \
    Mmesek/mframework
```

Build docker image
```sh
docker build --target base -t mframework:latest .
```

Run built image with autoremoving
```sh
docker run -it \
    -v "PATH_TO_DATA_FOLDER:/app/data" \
    -v "PATH_TO_BOT_CODE:/app/bot" \
    --rm mframework
```

## Locally

```sh
python -m MFramework bot --cfg=tokens.ini --log=INFO
```

# Contributing

Any sort of contribution, be it a Documentation, feature implementation, feature suggestion, bug fix, bug report or even a typo fix is welcome. For bigger changes open an issue first.
