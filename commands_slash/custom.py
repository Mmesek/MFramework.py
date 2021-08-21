from datetime import datetime

from MFramework import register, Groups, Context, Interaction, Embed, Embed_Footer, Embed_Thumbnail, Embed_Author, Discord_Paths, Message, Bitwise_Permission_Flags

@register(group=Groups.MODERATOR, guild=289739584546275339)
async def docket(ctx: Context, interaction: Interaction, docket: str, description: str='', publish: bool=False):
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

@register(group=Groups.MODERATOR, interaction=False)
async def bookmark(ctx: Context, title: str=None):
    '''
    Bookmark a moment in chat to save in your DMs for easy navigation
    Params
    ------
    title:
        title of the bookmark
    '''
    title = title or "Your bookmark"
    await ctx.send_dm(content=title+': \n'+Discord_Paths.MessageLink.link.format(guild_id=ctx.guild_id, channel_id=ctx.channel_id, message_id=ctx.message_id))

@register(group=Groups.GLOBAL)
async def Bookmark(ctx: Context, message: Message):
    '''Bookmark a moment in chat to save in your DMs for easy navigation'''
    await ctx.deferred(private=True)
    e = Embed(title="Your bookmark", description=message.content or None)
    e = message.attachments_as_embed(e)
    try:
        await ctx.send_dm(content=Discord_Paths.MessageLink.link.format(guild_id=ctx.guild_id, channel_id=message.channel_id, message_id=message.id), embeds=[e])
        await ctx.reply("Bookmarked in your DM successfully!")
    except:
        await ctx.reply("Couldn't send you a DM message!")

@register(group=Groups.GLOBAL)
async def Quote(ctx: Context, message: Message):
    '''Quotes a message'''
    if any(Bitwise_Permission_Flags.check(None, int(i.deny), 2048) for i in list(filter(lambda x: x.id in ctx.member.roles+[ctx.guild_id], ctx.channel.permission_overwrites))):
        await ctx.deferred(private=True)
        return await ctx.reply("Sorry, you can't use it here")
    await ctx.deferred()
    e = Embed()
    e = message.attachments_as_embed(e, title_attachments=None)
    e.setDescription(message.content)
    e.setTimestamp(message.timestamp)
    e.setAuthor(
        name=f"{message.author.username}#{message.author.discriminator}", 
        url=Discord_Paths.MessageLink.link.format(guild_id=ctx.guild_id, channel_id=message.channel_id, message_id=message.id), 
        icon_url=message.author.get_avatar()
    )
    e.setFooter(text=f"Quoted by {ctx.user.username}#{ctx.user.discriminator}")
    e.setColor("#3275a8")
    await ctx.reply(embeds=e)

@register(group=Groups.GLOBAL, guild=340185368655560704)
async def loadout(ctx: Context):
    '''
    Losuje ekwipunek
    '''
    eq = {
        "primary_weapon": [
            "R-201", "R-101", "Cykuta BF-R", "G2A5", "V-47 Kostucha",
            "CAR", "Alternator", "Wolt", "R97",
            "Spitfire", "L-STAR", "X-55 Oddanie",
            ["Kraber-AP", {"Szybki i Wściekły": "Rykoszet"}], ["D-2 Dublet", {"Szybki i Wściekły": "Rykoszet"}], "Longbow-DMR",
            "EVA-8 Auto", "Mastiff",
            "Grzechotnik SMR", "EPG-1", "R-6P Softball", "EM-4 Zimna Wojna",
            ["Elitarny Skrzydowy", {"Zmiana Broni": "Rykoszet"}], "SA-3 Mozambik"
        ],
        "primary_mods": ["Szybkie Przeładowanie", "Szybki i Wściekły", "Rewolwerowiec", "Zmiana Broni", "Taktyczna Eliminacja", "Dodatkowa Amunicja"],
        "secondary_weapon": ["RE-45 Auto", "Hammond P2016", "Skrzydłowy B3"],
        "secondary_mods": ["Szybkie Przeładowanie", "Tłumik", "Szybki i Wściekły", "Rewolwerowiec", "Taktyczna Eliminacja", "Dodatkowa Amunicja"],
        "anti_titan_weapon": [["Karabin Ładunkowy",{"Szybkie Przeładowanie": "Hakowanie Ładowania"}], "Wyrzutnia Magnetyczna WGM", "LG-97 Grom", "Łucznik"],
        "anti_titan_mods": ["Szybkie Przeładowanie", "Rewolwerowiec", "Dobycie Broni", "Dodatkowa Amunicja"],
        "ordnance": ["Odłamkowy", "Łukowy", "Gwiazda Ognista", "Gwiazda Grawitacyjna", "Elektro-Dymny", "Ładunek Wybuchowy"],
        "booster": ["Wzmocniona Broń", "Kleszcze", "Wieżyczka Przeciw Pilotom", "Hakowanie Mapy", "Zapasowa Bateria", "Zakłócacz Radaru", "Wieżyczka Przeciw Tytanom", "Pistolet Cyfrowy", "Przewinięcie Fazowe", "Twarda Osłona", "Multi Holopilot", "Rzut Kostką"],

        "faction": ["Korpus Łupieżców", "Łowcy Alfa", "Vinson Dynamics", "Elita Miasta Aniołów", "6-4", "Dywizja ARES", "Marvińska Elita"],

        "pilot_tactical": ["Maskowanie", "Ostrze Pulsacyjne", "Lina z Hakiem", "Stymulant", "Ściana Energetyczna", "Przeskok Fazowy", "Holopilot"],
        "pilot_kit": ["Bateria", "Szybka Regeneracja", "Gadżeciarz", "Wejście Fazowe"],
        "pilot_kit_2": ["Raport o Poległych", "Ścianołaz", "Zawis", "Cichociemny", "Łowca Tytanów"],

        "titan": {
            "Kationa":["Splątana Energia", "Mina Wiązkowa", "Wzmacniacz Wirowy", "Megadziałko", "Soczewka Refrakcyjna"], 
            "Spopielacz":["Pożoga", "Wzmocnione Poszycie", "Piekielna Tarcza", "Zapas Paliwa", "Spalona Ziemia"], 
            "Polaris":["Strzał Penetrujący", "Zwiększony Ładunek", "Podwójne Pułapki", "Silniki pomocnicze Żmija", "Optyka Detektorowa"], 
            "Ronin":["Naboje Rykoszetujące", "Gromowładny", "Anomalia Czasowa", "Fechmistrz", "Unik Fazowy"], 
            "Ton":["Pociski Śledzące +", "Wzmocniona Ściana Energetyczna", "Echo Pulsowe", "Rakietowa Salwa", "Zasobnik Seryjny"], 
            "Legion":["Większy Zasób Amunicji", "Siatka Czujników", "Zapora", "Lekkie Materiały", "Ukryta Komora"], 
            "Monarcha":["Wzmacniacz Tarczy", "Złodziej Energii", "Szybkie Przezbrojenie", "Przetrwają Najsilniejsi"]
        },
        "titan_kit": ["Chip Szturmowy", "Katapulta z Maskowaniem", "Silnik Turbo", "Doładowanie Rdzenia", "Nuklearna Katapulta", "Gotowa Riposta"],
        "titanfall_kit": ["Tarcza Sklepieniowa", "Hiperzrzut"],

        "mode": {"Wyniszczenie": True, "Starcie Pilotów": True, "Obrona Umocnień": False, "Łowy": True, "Walka o Flagę": False, "Do Ostatniego Tytana": True, "Piloci Kontra Piloci": False, "Szybki Szturm": False, "Na Celowniku": False, "Starcie Tytanów": True, "Obrona Kresów": True, "Koloseum": True},
        "map": {"Baza Kodai": True, "Wybuchowo": False, "Gospodarstwo": True, "Egzoplaneta": True, "Kanał ,,Czarna Toń''": True, "Eden": False, "Suchy Dok": True, "Miejsce Katastrofy": False, "Kompleks": False, "Miasto Aniołów": True, "Kolonia": False, "Błąd": False, "Relikt": False, "Gry Wojenne": True, "Powstanie": True, "Stosy": False, "Pokład": False, "Łąka": False, "Ruch Uliczny": False, "Miasto": False, "UMA": False}
    }
    cores = {
        1: ["Pociski Łukowe", "Zasobink Rakietowy", "Transfer Energii"],
        2: ["Przezbrojenie i Przeładowanie", "Wir", "Pole Energetyczne"],
        3: ["Wielokrotne Namierzanie", "Udoskonalony Kadłub", "Akcelerator XO-16"]
    }

    from random import SystemRandom
    random = SystemRandom()

    r = {}
    mods_overwrite = {}
    for k, v in eq.items():
        if type(v) is dict:
            _v = [i for i in v.keys()]
        else:
            _v = v
        if 'mods' in k:
            c = random.sample(_v, k=2)
            mods = []
            for i in c:
                if i in mods_overwrite:
                    i = mods_overwrite[i]
                mods.append(i)
            mods_overwrite = {}

            c = "\n- ".join([""]+mods)
            r[k.replace("mods", "weapon")] += c
            continue
        else:
            c = random.choice(_v)
        if type(c) is list:
            mods_overwrite = c[1]
            c = c[0]
        if k == 'map':
            if eq['mode'][r['mode']]:
                if r['mode'] == 'Obrona Kresów':
                    maps = [i[0] for i in filter(lambda i: i[1], eq['map'].items())]
                else:
                    maps = [i for i in eq['map'].keys()][:-6]
                c = random.choice(maps)

        r[k] = c
        if c == 'Monarcha':
            for level, core in cores.items():
                r[f"core_{level}"] = random.choice(core)

        if k == 'titan':
            c = random.choice(v[c])
            r['class_kit'] = c
        if k == 'mode' and r['mode'] == 'Koloseum':
            break

    embed = Embed()
    from mlib.localization import tr
    for k, v in r.items():
        embed.addField(tr("commands.loadout."+k, language='pl'), v, True)

    await ctx.reply(None, [embed])

@register(group=Groups.GLOBAL, guild=289739584546275339, interaction=False)
async def when(ctx: Context, arg:str=None):
    '''
    Shows remaining delta    
    '''
    from random import SystemRandom as random
    if arg:
        try:
            with open("data/bad_words.txt", encoding="utf-8") as word_file:
                bad_words = word_file.read().split("\\n")
            bad_words = set(i.strip() for i in bad_words)
        except:
            bad_words = set()
        if any(i in bad_words for i in arg.lower().split(' ')):
            return await ctx.reply("Hey, that's rude! <:pepemad:676181484238798868>")
    if random().random() < 5 / 100:
        return await ctx.reply("When it's ready.")
    from datetime import datetime
    date = datetime(2021, 12, 7, 19)
    timestamp = int(date.timestamp())
    delta = date - datetime.now()
    if delta.total_seconds() < 0:
        return await ctx.reply("Released!")
    await ctx.reply(f"Remaining `{delta}` until <t:{timestamp}:D> which is <t:{timestamp}:R>")