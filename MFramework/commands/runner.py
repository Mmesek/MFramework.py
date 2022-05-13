from typing import Dict, TYPE_CHECKING, Union

from MFramework import (
    onDispatch,
    Interaction,
    Message,
    Interaction_Type,
    Component_Types,
    Embed,
)

from .command import Command
from .arguments import Arguments
from ._utils import set_context, retrieve_command


if TYPE_CHECKING:
    from MFramework import Context, Bot


async def modal_response(ctx: "Context", data: Union[Message, Interaction], cmd: Command) -> Dict[str, str]:
    """Responds with modal for interactions, or with message based questions awaiting each input"""
    if type(data) is Interaction:
        await ctx.bot.create_interaction_response(data.id, data.token, response=cmd.modal)
        # NOTE: This way we can take additional arguments from regular command and can merge both.
        # Modals are usually ephemeral so timeout shouldn't be a problem.
        # However in case of "raw" Modal input, we still need legacy way to support while making modals from params
        interaction: Interaction = await ctx.bot.wait_for(
            "interaction_create",
            check=lambda _data: _data.type == Interaction_Type.MODAL_SUBMIT
            and _data.data.custom_id == cmd.modal.data.custom_id
            and (_data.member.user.id == data.member.user.id if data.guild_id else _data.user.id == data.user.id),
            timeout=300,
            # NOTE: If somehow someone sends a modal after timeout expires, it should be handled by separate flow
        )
        # NOTE: Overwriting token and ID since previous one doesn't matter anymore
        ctx.data.token = interaction.token
        ctx.data.id = interaction.id
        # Rest of the payload isn't necessary needed as we are parsing it into dictionary anyway
        return await parse_modal_submit(interaction)

    # NOTE: This is message-based way to take parameters, considering modals are nicer, this is entirely useless
    # TODO: Extend this to take regular parameters in case of message-based command with partial arguments
    inputs = {}

    for text_input in cmd.modal.data.components:
        text_input = text_input.components[0]
        e = Embed()
        e.set_title(text_input.label)
        e.set_description(text_input.placeholder)
        e.add_field("Minimum characters", str(text_input.min_length), True)
        e.add_field("Maximum characters", str(text_input.max_length), True)
        e.add_field("Required", "Yes" if text_input.required else "Skip by sending `-`", True)
        await data.reply(embeds=[e])
        msg: Message = await ctx.bot.wait_for(
            "message_create" if not data.guild_id else "direct_message_create",
            check=lambda x: x.author.id == data.author.id
            and x.channel_id == data.channel_id
            and (
                (len(x.content) <= text_input.max_length and len(x.content) >= text_input.min_length)
                or (not text_input.required and x.content == "-")
            ),
            timeout=300,
        )
        inputs[text_input.label.lower().replace(" ", "_")] = msg.content

    return inputs


async def parse_modal_submit(interaction: Interaction):
    inputs = {}

    for row in interaction.data.components:
        # NOTE: This will work only for TextInput, it'll require updating when Modals will support more types!
        for text_input in filter(lambda x: x.type == Component_Types.TEXT_INPUT, row.components):
            inputs[text_input.custom_id.split("-", 1)[-1]] = text_input.value

    inputs.update({"inputs": inputs.copy()})

    return inputs


@onDispatch(event="message_create", optional=True, priority=5)
@onDispatch(event="direct_message_create", optional=True, priority=5)
@onDispatch(
    event="interaction_create",
    predicate=lambda x: x.type in {Interaction_Type.APPLICATION_COMMAND, Interaction_Type.MODAL_SUBMIT},
)
async def run(client: "Bot", data: Union[Message, Interaction]) -> bool:
    cmd = retrieve_command(data)

    ctx = set_context(client, cmd, data)

    if type(data) is Interaction and data.type is Interaction_Type.MODAL_SUBMIT:
        inputs = await parse_modal_submit(data)
    elif cmd.modal:
        try:
            inputs = await modal_response(ctx, data, cmd)
        except TimeoutError:
            if type(data) is Message:
                # NOTE: This response is only for message, as interaction can be continued in separate MODAL_SUBMIT
                # TODO: However that's a problem if command accepts any other arguments before modal
                await data.reply("Waited too long for an answer. Use command again if you would like to retry")
            return False
    else:
        inputs = {}

    if cmd.auto_deferred:
        await ctx.deferred(cmd.private_response)

    kwargs = Arguments(cmd, ctx, inputs)
    await cmd.execute(ctx, kwargs.kwargs)
    return True
