from MFramework import register, Groups, Context, Interaction

@register()
async def roll(ctx: Context, interaction: Interaction, *args, language, **kwargs):
    '''Random Numbers'''
    pass

@register(group=Groups.GLOBAL, main=roll)
async def chance(ctx: Context, interaction: Interaction, argument: str, *args, language, **kwargs):
    '''Rolls a percentage chance
    Params
    ------
    argument:
        String to roll
    '''
    from random import seed, randint
    statement = argument
    seed(statement)
    await interaction.send(f"{randint(1, 100)}% chance {'that' if 'is' in statement else 'of'} {statement}")

@register(group=Groups.GLOBAL, main=roll)
async def dice(ctx: Context, interaction: Interaction, number: int=20, times: int=1, *args, language, **kwargs):
    '''Rolls a die
    Params
    ------
    number:
        Maximal number dice should have
    times:
        How many dices should be rolled
    '''
    import random
    await interaction.send(', '.join([str(number) + ": " + str(random.SystemRandom().randrange(int(number)) + 1) for i in range(times)]))
