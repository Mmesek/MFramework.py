from datetime import datetime
from MFramework import register, Groups, Context, Interaction, Embed, Embed_Footer, Embed_Thumbnail, Embed_Author

@register(group=Groups.MODERATOR, guild=289739584546275339)
async def docket(ctx: Context, interaction: Interaction, docket: str, description: str='', publish: bool=False, *args, language, **kwargs):
    '''
    Sends new docket in an embed
    
    Params
    ------
    docket:
        Docket code
    description:
        Optional description of docket
    publish:
        Whether message should be published to following channels or not (Works only in announcement channels)
        Choices:
            True = True
            False = False
    '''
    if description != '':
        description = f"\n{description}\n"
    embed = Embed(
        description=f"New Docket Code: {docket.upper()}\n{description}\n[Redeem Here](https://techland.gg/redeem?code={docket.replace(' ','')})",
        color=13602095,
        timestamp=datetime.utcnow(),
        footer=Embed_Footer(
            text=interaction.member.nick or interaction.member.user.username,
            icon_url=interaction.member.user.get_avatar()
        ),
        thumbnail=Embed_Thumbnail(height=128, width=128,
            url="https://cdn.discordapp.com/emojis/545912886074015745.png",
        ),
        author=Embed_Author(
            name=docket.upper(), url=f"https://techland.gg/redeem?code={docket.replace(' ','')}",
            icon_url="https://cdn.discordapp.com/emojis/545912886074015745.png"
        ),
    )
    msg = await ctx.send("<@&545856777623961611>", embeds=[embed], allowed_mentions=None)
    if publish:
        await msg.publish()