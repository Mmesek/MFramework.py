# -*- coding: utf-8 -*-
'''
Commands
--------

Message command execution framework

:copyright: (c) 2020-2021 Mmesek

'''
from MFramework import *
from ._utils import commands, command_shortcuts, commands_regex
from ._utils import get_trigger, get_arguments, get_original_cmd, set_ctx, set_kwargs, add_extra_arguments, is_nested

@onDispatch(event="message_create", priority=2)
async def check_command(client: Bot, message: Message) -> bool:
    if message.is_empty:
        return
    alias = get_trigger(client, message)
    if not alias:
        return False
    
    args = get_arguments(client, message)
    # TODO: Allow some way of specifying keyword-only arguments like -flag=value from command arguments
    # TODO: Command Translations?
    _name = args[0].strip(alias)
    name = get_original_cmd(_name)

    f = commands.get(name, None)
    if not f:
        return
    
    if len(args) > 1:
        while True:
            _f = f
            i = 1
            f = is_nested(None, f, args[i])
            if f == _f:
                args = args[i:]
                break
            i+=1
    if f._only_interaction:
        return
    ctx = set_ctx(client, message, f)
    if not ctx:
        return False
    
    kwargs = set_kwargs(ctx, f, args)
    kwargs = add_extra_arguments(f, kwargs, ctx=ctx, client=client, cmd=_name, alias=alias, language='en', **kwargs)

    await f.execute(ctx, kwargs)

    return True

#@onDispatch(event="message_create", priority=2)
async def check_regex(client: Bot, message: Message) -> bool:
    for regex, cmd in commands_regex.items():
        r = regex.search(message.content)
        if r:
            ctx = set_ctx(client, message, cmd)
            g = r.groupdict()
            await commands_regex[regex](**g)
            return True

#@onDispatch(event="message_create", priority=2)
async def check_shortcuts(client: Bot, message: Message) -> bool:
    alias = get_trigger(client, message)
    if not alias:
        return False
    
    args = get_arguments(client, message)
    _name = args[0].strip(alias)
    name = get_original_cmd(_name)

    f, _kwargs = command_shortcuts.get(name, (None, None))
    ctx = set_ctx(client, message, f)
    if not ctx:
        return False

    kwargs = set_kwargs(ctx, f, args)
    kwargs.update(_kwargs)
    kwargs['ctx'] = ctx
    kwargs['client'] = client
    kwargs['message'] = message
    kwargs['language'] = 'en'
    kwargs['_cmd'] = _name
    
    await f.func(**kwargs)
    return True

@onDispatch(event="reaction_add")
async def check_reaction(client: Bot, reaction: Reaction) -> bool:
    from ._utils import reactions
    f = reactions.get(str(reaction), None)
    ctx = set_ctx(client, reaction, f)
    if not ctx:
        return False
    await f.func(ctx, reaction)