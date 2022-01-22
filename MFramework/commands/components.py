from typing import Dict, List

from mdiscord.models import Button_Styles, Emoji, Select_Option
from MFramework import onDispatch, Context, Bot, Interaction, Interaction_Type, Component_Types, log, Button, Component

class MetaCommand:
    auto_deferred: bool = True
    private_response: bool = True
    def __init_subclass__(cls) -> None:
        print("registering", cls.__name__)
        components[cls.__name__] = cls
        return super().__init_subclass__()
    @classmethod
    async def execute(cls, ctx: Context, data: str, values: List[str] = None, not_selected: List[Select_Option] = None):
        pass

components: Dict[str, MetaCommand] = {}

@onDispatch
async def interaction_create(client: Bot, interaction: Interaction):
    '''Called after receiving event INTERACTION_CREATE from Discord
    Reacts only to Components (Buttons)'''
    if interaction.type != Interaction_Type.MESSAGE_COMPONENT:
        return
    ctx = Context(client.cache, client, interaction)
    name, data = interaction.data.custom_id.split("-", 1)
    f = components.get(name, None)
    if not f:
        log.debug("Component %s not found", name)
        return

    if f.auto_deferred:
        await interaction.deferred(f.private_response)
    
    if interaction.data.component_type == Component_Types.SELECT_MENU.value:
        not_selected = []
        for row in interaction.message.components:
            for select_component in filter(lambda x: x.type == Component_Types.SELECT_MENU, row.components):
                if any(v in [_v.value for _v in select_component.options] for v in interaction.data.values):
                    for value in select_component.options:
                        if value.value not in interaction.data.values:
                            not_selected.append(value)
        return await f.execute(ctx, data, interaction.data.values, not_selected)
        # TODO: way to auto send message like for regular commands

    await f.execute(ctx, data)


# BASE

class Row(Component):
    type = Component_Types.ACTION_ROW
    components: List[Component]
    def __init__(self, *components: Component):
        self.components = components

ActionRow = Row

class Component(Component, MetaCommand):
    def __init__(self, custom_id: str = None):
        self.custom_id = self.__class__.__name__ + "-" + str(custom_id)

# SELECT MENUS

class Select(Component):
    def __init__(self, *options: Select_Option, custom_id: str = None, placeholder: str = None, min_values: int = 0, max_values: int = 1, disabled: bool = False):
        self.type = Component_Types.SELECT_MENU.value
        self.options = options
        self.placeholder = placeholder
        self.min_values = min_values
        self.max_values = max_values
        self.disabled = disabled
        super().__init__(custom_id)

    @classmethod
    async def execute(cls, ctx: Context, data: str, values: List[str]):
        return await super().execute(ctx, data)

class Option(Select_Option):
    def __init__(self, label: str, value: str, description: str = None, emoji: Emoji = None, default: bool = False):
        self.label = label
        self.value = value
        self.description = description
        self.emoji = emoji
        self.default = default

SelectMenu = Select
SelectOption = Option

# BUTTONS

class Button(Component):
    type = Component_Types.BUTTON
    style = Button_Styles.PRIMARY
    def __init__(self, label: str, custom_id: str = None, style: Button_Styles = Button_Styles.PRIMARY, emoji: Emoji = None, disabled: bool = False):
        self.style = style.value
        super().__init__(custom_id)
        #self.custom_id = custom_id
        self.type = Component_Types.BUTTON.value
        self.label = label
        self.emoji = emoji
        self.disabled = disabled

class LinkButton(Button):
    style = Button_Styles.LINK
    def __init__(self, label: str, url: str = None, emoji: Emoji = None, disabled: bool = False):
        super().__init__(label, style=Button_Styles.LINK, emoji=emoji, disabled=disabled)
        self.custom_id = None
        self.url = url
