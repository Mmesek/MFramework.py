from typing import TYPE_CHECKING, Dict, List
from functools import partial

from mdiscord.models import Button_Styles, Emoji, Select_Option, Text_Input_Styles

from MFramework import (
    Button,
    Component,
    Component_Types,
    Embed,
    Interaction,
    Interaction_Application_Command_Callback_Data,
    Interaction_Callback_Type,
    Interaction_Response,
    Interaction_Type,
    log,
    onDispatch,
)

from .exceptions import CooldownError


if TYPE_CHECKING:
    from MFramework import Bot, Context


async def run_function(cmd: "MetaCommand", ctx: "Context", **kwargs):
    try:
        r = await cmd.execute(ctx, **kwargs)
    except CooldownError as ex:
        return await ctx.reply(
            f"<@{ctx.user_id}>, Remaining Cooldown: <t:{ex.args[0]}:R>",
        )

    if isinstance(r, Embed) or (type(r) is list and all(isinstance(i, Embed) for i in r)):
        await ctx.reply(embeds=[r] if type(r) is not list else r)
    elif isinstance(r, Modal):
        await ctx.bot.create_interaction_response(
            ctx.data.id,
            ctx.data.token,
            Interaction_Response(
                type=Interaction_Callback_Type.MODAL,
                data=Interaction_Application_Command_Callback_Data(
                    title=r.title, custom_id=r.custom_id, components=r.components
                ),
            ),
        )
    elif isinstance(r, Component) or (type(r) is list and all(isinstance(i, Component) for i in r)):
        await ctx.reply(components=[r] if type(r) is not list else r)
    elif callable(r):
        if hasattr(r, "_cmd"):
            await ctx.bot.create_interaction_response(ctx.data.id, ctx.data.token, r._cmd.modal)
    elif r:
        await ctx.reply(str(r))


class MetaCommand:
    auto_deferred: bool = True
    private_response: bool = True
    _no_interaction: bool = False

    def __init_subclass__(cls) -> None:
        log.debug("Registering Component %s", cls.__name__)
        components[cls.__name__] = cls
        return super().__init_subclass__()

    def __init__(self) -> None:
        self.func = self.__class__

    @classmethod
    async def execute(
        cls,
        ctx: "Context",
        data: str,
        values: List[str] = None,
        not_selected: List[Select_Option] = None,
    ):
        pass


components: Dict[str, MetaCommand] = {}


@onDispatch
async def interaction_create(client: "Bot", interaction: Interaction):
    """Called after receiving event INTERACTION_CREATE from Discord
    Reacts only to Components (Buttons)"""
    from MFramework import Context

    if interaction.type != Interaction_Type.MESSAGE_COMPONENT and interaction.type != Interaction_Type.MODAL_SUBMIT:
        return
    name, data = interaction.data.custom_id.split("-", 1)
    f = components.get(name, None)
    ctx = Context(client.cache, client, interaction)  # , f)  # FIXME _cmd path not set
    if not f:
        log.debug("Component %s not found", name)
        return

    if f.auto_deferred:
        await interaction.deferred(f.private_response)

    if interaction.data.component_type == Component_Types.SELECT_MENU:
        not_selected = []
        for row in interaction.message.components:
            for select_component in filter(lambda x: x.type == Component_Types.SELECT_MENU, row.components):
                if any(v in [_v.value for _v in select_component.options] for v in interaction.data.values):
                    for value in select_component.options:
                        if value.value not in interaction.data.values:
                            not_selected.append(value)
        return await run_function(f, ctx, data=data, values=interaction.data.values, not_selected=not_selected)
    elif interaction.type == Interaction_Type.MODAL_SUBMIT:
        inputs = {}
        for row in interaction.data.components:
            for text_input in filter(lambda x: x.type == Component_Types.TEXT_INPUT, row.components):
                inputs[text_input.custom_id.split("-", 1)[-1]] = text_input.value
        return await run_function(f, ctx, data=data, inputs=inputs)

    return await run_function(f, ctx, data=data)


# BASE


class Row(Component):
    type = Component_Types.ACTION_ROW.value
    components: List[Component]

    def __init__(self, *components: Component):
        self.components = components


ActionRow = Row


class Component(Component, MetaCommand):
    def __init__(self, custom_id: str = None):
        self.custom_id = self.__class__.__name__ + "-" + str(custom_id)


# SELECT MENUS


class Select(Component):
    def __init__(
        self,
        *options: Select_Option,
        custom_id: str = None,
        placeholder: str = None,
        min_values: int = 0,
        max_values: int = 1,
        disabled: bool = False,
    ):
        self.type = Component_Types.SELECT_MENU.value
        self.options = options
        self.placeholder = placeholder
        self.min_values = min_values
        self.max_values = max_values
        self.disabled = disabled
        super().__init__(custom_id)

    @classmethod
    async def execute(
        cls,
        ctx: "Context",
        data: str,
        values: List[str],
        not_selected: List[Select_Option],
    ):
        return await super().execute(ctx, data)


class Option(Select_Option):
    def __init__(
        self,
        label: str,
        value: str,
        description: str = None,
        emoji: Emoji = None,
        default: bool = False,
    ):
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

    def __init__(
        self,
        label: str,
        custom_id: str = None,
        style: Button_Styles = Button_Styles.PRIMARY,
        emoji: Emoji = None,
        disabled: bool = False,
    ):
        self.style = style.value
        super().__init__(custom_id)
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


# MODALS


class Modal(Component):
    type = None
    disabled = None

    def __init__(self, *components: Component, title: str = None, custom_id: str = None):
        self.title = title or self.__class__.__name__
        self.components = components
        super().__init__(custom_id)

    @classmethod
    async def execute(cls, ctx: "Context", data: str, inputs: Dict[str, str]):
        return await super().execute(ctx, data)


class TextInput(Component):
    """
    Usage as a typehint: TextInput[min, max(, step)] or just TextInput[max] where min/max/step are integer values
    """

    type: int = Component_Types.TEXT_INPUT.value

    def __init__(
        self,
        label: str,
        custom_id: str = None,
        style: Text_Input_Styles = Text_Input_Styles.Paragraph,
        min_length: int = 0,
        max_length: int = 4000,
        required: bool = False,
        value: str = None,
        placeholder: str = None,
    ):
        super().__init__(custom_id or label)
        self.style = style.value
        self.label = label
        self.min_length = min_length
        self.max_length = max_length
        self.required = required
        self.value = value
        self.placeholder = placeholder

    def __class_getitem__(cls: "TextInput", obj: tuple) -> "TextInput":
        if type(obj) is tuple:
            if len(obj) == 3:
                _range = range(int(obj[0]), int(obj[1]), int(obj[2]))
            _range = range(int(obj[0]), int(obj[1]))
        else:
            _range = range(obj)
        return type(
            "TextInput",
            (TextInput,),
            {"min_length": _range.start, "max_length": _range.stop},
        )


def button(name: str = None, style: Button_Styles = Button_Styles.PRIMARY, emoji: Emoji = None):
    """
    Allows using decorated function like it's a button (in place of) factory.
    Creates button that responds or injects Modal response to fill remaining arguments

    Parameters
    ----------
    name:
        Default label of the button
    style:
        Default Style of the button
    emoji:
        Default Emoji of the button

    Examples
    --------
    ```py
    >>> @register()
    >>> @button("Click Click Click")
    >>> async def multiply_text(text: str, number: int = 0) -> str:
            '''
            Params
            ------
            text:
                Text you want to send!
            number:
                How many times should it be duplicated?
            '''
    >>>     return text * amount

    >>> @register()
    >>> async def create_button():
            '''Sends button that executes multiply_text'''
    >>>     return multiply_text.button()
    ```
    """

    def inner(f):
        components = []
        for arg in f.command.arguments.values()[:5]:
            components.append(
                Row(
                    TextInput(
                        label=arg.name.replace("_", " ").title(),
                        custom_id=str(arg.name),
                        style=Text_Input_Styles.Short if issubclass(arg.type, int) else Text_Input_Styles.Paragraph,
                        placeholder=arg.description,
                        required=arg.default != None,
                    )
                )
            )
        f.button = partial(
            type(
                f.__name__,
                (Button),
                {
                    "execute": lambda x: Modal(
                        *components,
                        title=f.__name__.replace("_", " ").title(),
                        custom_id=f.__name__ + "-None",
                    )
                    if components
                    else f
                },
            ),
            style=style,
            label=name or f.__name__.title(),
            emoji=emoji,
        )

        return f

    return inner


def select(placeholder: str = None, min_values: int = None, max_values: int = None):
    """
    Allows using function like it's a select menu (in place of) factory.
    Creates select menu that responds or injects Modal response to fill remaining arguments

    Parameters
    ----------
    placeholder:
        Default placeholder of the select menu
    min_values:
        Minimal amount of values to select
    max_values:
        Maximal amount of values to select
    """

    def inner(f):
        f.select = partial(
            type(f.__name__, (Select), {"execute": f}),
            placeholder=placeholder,
            min_values=min_values,
            max_values=max_values,
        )
        return f

    return inner
