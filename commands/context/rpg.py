from MFramework.commands import ctxRegister, BaseCtx
from MFramework.utils.utils import Embed, getIfromRGB, upperfirst
from MFramework.database import alchemy as db
import asyncio
from collections import Counter
@ctxRegister(group="dm")
class CreateCharacter(BaseCtx):
    """
    Elo mordo
    """

    def __init__(self, *args, **kwargs):
        super().__init__(args, **kwargs)
        #self.order = ["race","gender", "story"]
        self.embed = Embed().setAuthor('[Imię "Przydomek" Nazwisko]',None, None).setDescription("[Twoja Historia]")
        self.order = ["intro",
            #"begin",
            "placeoforigin",
            "who",
            "profession",
            "race",
            "gender",
            "age",
            "whereabouts",
            "ref",
            "reason",
            "color",
            "drink",
            "hate",
            "fear",
            "weakness",
            "strength",
            "items",
            "story", "confirmed"
        ]
        self.answers = {}
        self.last_error_message = None
        self.wrong_answers = ['brak', 'nie posiadam', 'nic', 'niczego', 'nie istnieje', 'wielka', 'wielki','duża','duży','ogromny','ogromna', "niczym","-"]
        self.fields = {
            "placeoforigin": "Przybyto z",
            "who": "Imię",
            "profession": "Profesja",
            "race": "Rasa",
            "gender": "Płeć",
            "age": "Wiek",
            #"whereabouts": "Trafiono do Tawerny z",
            "whereabouts": "Historia trafienia do Tawerny",#"Trafiono do Tawerny w sposób",
            "ref": "Polecony przez",
            #"reason": "Powodem jest",
            "reason": "Powodem przybycia do Tawerny jest",
            "color": "Kolor",
            "drink": "Trunek",
            "hate": "Nienawiść do",
            "fear": "Strach przed",
            "weakness": "Słabość",
            "strength": "Siła",
            "items": "Posiadane Przedmioty",
            "story": "Historia",
        }
        self.lock = False
        for i in self.fields:
            if i not in ["who", "story"]:
                self.embed.addField(self.fields[i], "\u200b", True)
        self.rules = Embed().setAuthor("Tawerna | Menu", None, None).setTitle("Witaj w Tawernie, Podróżniku!").setDescription("""Tawerna jest lekkim semi RP. Akcja dzieje się w <#463437626515652618>, poza wymiarami.
Jest to miejsce w miarę neutralne *(To jest: tak długo jak nie atakujesz właściciela w sposób pośredni bądź bezpośredni)*, niemniej jednak: Przywitaj się jeśli planujesz zostać na dłużej.
> - W razie wątpliwości kieruj się netykietą

> - Rzeczy związane z botami znajdują się w #piwnica w <#464070521835880448>

> - Jeśli poszukujesz kompanów do następnej podróży bądź przygody, <#464072829105733643> jest miejscem dla Ciebie

> - Natomiast jeżeli chcesz być powiadamiany gdy inni szukają kompanów, zajrzyj do <#480716411594080267>
Dodatkowe informacje mogą zostać znalezione w opisach pokoi.""").setImage("https://cdn.discordapp.com/attachments/474917631745327114/557030836835188745/ad.png").setFooter("https://media.discordapp.net/attachments/474917631745327114/557029895025197056/roundav.png","Tawerna 2020").setColor(3106232)
        self.rules.embed["thumbnail"] = {"url":"https://cdn.discordapp.com/attachments/474917631745327114/629240634665861150/tawlog7.1.png",
        "height":64,
        "width": 64}
        self.steps = {}
    async def execute(self, *args, data, **kwargs):
        if self.bot.username != 'M_Bot':
            return await self.end()
        if hasattr(data, "content") and data.content == "--zakończ":
            await self.bot.message(self.channel, "Koniec")
            await self.end()
            return
        if self.currentStep == 0:
            s = self.bot.db.sql.session()
            c = s.query(db.RolePlayCharacters).filter(db.RolePlayCharacters.GuildID == self.guild).filter(db.RolePlayCharacters.UserID == self.user).first()
            if c != None:
                await self.bot.message(self.channel, "Postać już istnieje")
                await self.end()
                return
        if not self.lock:
            self.last = data
            self.lock = True
            self.steps[data.id] = self.currentStep
            if self.currentStep > 0:
                #self.answers[self.order[self.currentStep]] = data.content
                self.answers[self.order[self.currentStep]] = upperfirst(data.content)
                #self.answers[self.order[self.currentStep]][0] = data.content[0].capitalize()
                print(self.order[self.currentStep], data.content)
            if not await getattr(self, self.order[self.currentStep], self.end)():
                embed = self.createEmbed()
                await self.bot.edit_message(self.channel, self.first_embed["id"], "", embed.embed)
                self.iterate()
                if len(self.order) <= self.currentStep or not getattr(self, self.order[self.currentStep], False):
                    await self.end()
            self.lock = False

    def getIntFromColor(self, color):
        from MFramework.utils import colors
        try:
            if "#" in color:
                color = int(color.replace("#", ""), 16)
            elif color.lower() in colors.colors:
                color = int(colors.colors[color.lower()].replace("#",""), 16)
            else:
                rgb = [int(i) for i in color.replace(" ","").split(",")]
                color = getIfromRGB(rgb)
        except Exception as ex:
            color = 0
        return color
    def createEmbed(self):
        embed = Embed()  # .setDescription(k[:2024])
        if 'color' in self.answers:
            from MFramework.utils import colors
            color = self.getIntFromColor(self.answers["color"])
            for _color, hex in colors.colors.items():
                if int(hex.replace("#",""), 16) == color:
                    self.answers["color"] = _color.title()
                    break
            if self.answers['color'][0] == '#':
                self.answers['color'] = self.answers['color'].lower()

            embed.setColor(color)
        for i in self.fields:  # .replace("_", " ").title()
            if i not in self.answers:
                if i == "story" or i == "who":
                    if i == "story":
                        embed.setDescription("[Twoja Historia]")
                    else:
                        embed.setAuthor('[Imię "Przydomek" Nazwisko]', None, None)
                else:
                    embed.addField(self.fields[i], f"\u200b", True)
                continue
            elif i != "story" and i != "who":
                if i == "gender":
                    if self.answers[i].lower()[0] in ['k','d']:
                        self.answers[i] = 'Kobieta'
                        self.fields['ref'] = 'Polecona przez'
                        self.g = "a"
                    elif self.answers[i].lower()[0] in ['m','f']:
                        self.answers[i] = 'Mężczyzna'
                        self.fields['ref'] = 'Polecony przez'
                        self.g = "e"
                elif i == 'who':
                    pass
                elif i == "items":
                    if ',' in self.answers[i]:
                        self._items = ['- ' + upperfirst(i.strip()) for i in self.answers[i].split(',')]
                    else:
                        self._items = ['- ' + upperfirst(i.strip()) for i in self.answers[i].split('\n')]
                    deduplicated_items = Counter(self._items)
                    deduplicated_items_values = list(deduplicated_items.values())
                    deduplicated_items = list(deduplicated_items.keys())
                    self._items = [i + f' x {deduplicated_items_values[x]}' if deduplicated_items_values[x] > 1 else i for x, i in enumerate(deduplicated_items[:3])]
                    items = '\n'.join(self._items)
                    embed.addField(self.fields[i], f"||{items}||", True)
                    continue

                embed.addField(self.fields[i], f"||{self.answers[i][:512]}||", True)
            else:
                if i == "story":
                    embed.setDescription(f"||{self.answers[i][:2000]}||")
                else:
                    embed.setAuthor(self.answers[i][:512],None,None)
        
        return embed

    async def _handle_error_edit(self, *args, data, **kwargs):
        if self.order[self.steps[data.id]] == 'placeoforigin' and data.content.lower() in ['z dalekiej krainy', 'z bardzo daleka','z bardzo dalekiej krainy', 'zniknąd', 'zewsząd']:
            return await self.bot.message(self.channel, "Skąd dokładnie przybywasz?")
        elif self.order[self.steps[data.id]] == "profession" and data.content.lower() in ['nieznany', 'nieznana', 'nic', 'brak']:
            return await self.bot.message(self.channel, "Podaj swoją profesję mordko")
        elif self.order[self.steps[data.id]] == 'race' and data.content.lower() in ['hybryda', 'mieszaniec', 'mieszanka', 'zwierz', 'zwierzę', 'zwierzęcie']:
            if 'hybryda' in data.content.lower():
                return await self.bot.message(self.channel, "Hybryda jakich ras?")
            elif data.content.lower() in ['zwierz', 'zwierzę', 'zwierzęcie']:
                return await self.bot.message(self.channel, "Jakie zwierzęcie?")
            else:
                return await self.bot.message(self.channel, "Mieszanka jakich gatunków?")
        elif self.order[self.steps[data.id]] == 'gender':
            if data.content[0].lower() not in ["m", "k"]:
                return await self.bot.message(self.channel, "Binarna płeć mordo.\nM - Mężczyna\nK - Kobieta")
        elif self.order[self.steps[data.id]] == 'age':
            if not data.content.isdigit():
                return await self.bot.message(self.channel, "Podaj cyfrę.")
        elif self.order[self.steps[data.id]] == 'story':
            if (data.content.lower() == "długa") or (((len(set(data.content.lower().split(' '))) < 5) and len(data.content) < 20)):
                if data.content.lower() == "długa":
                    return await self.bot.message(self.channel, "To bardzo fajnie że jest długa mordko. A teraz ją tutaj opowiedz. Z detalami.")
                elif (len(set(data.content.lower().split(' '))) < 5) and len(data.content) < 20:
                    return await self.bot.message(self.channel, "Nie za długa ta historia mordko tak więc zapytam raz jeszcze: Jaka jest Twoja historia?")
                else:
                    return await self.bot.message(self.channel, "Niby jest. A jednak się nie zgadza.")
        elif self.order[self.steps[data.id]] == 'whereabouts':
            if ((data.content.lower() == "nic") or (((len(set(data.content.lower().split(' '))) < 3) and len(data.content) < 10))):
                if data.content.lower() == "nic":
                    return await self.bot.message(self.channel, f"Raczej nie nic, w jakiś sposób się tutaj musiał{self.g}ś znaleźć. W jaki?")
                elif (len(set(data.content.lower().split(' '))) < 3) and len(data.content) < 10:
                    return await self.bot.message(self.channel, "Doprawdy? Dodaj może odrobinę więcej detali mordko?")
                else:
                    return await self.bot.message(self.channel, "Niby jest. A jednak się nie zgadza.")
        elif self.order[self.steps[data.id]] in ['fear', 'strength', 'weakness', 'hate']:
            if data.content.lower() in self.wrong_answers:
                return await self.bot.message(self.channel, "Raczej nie mordko, coś tam jest.")
        elif self.order[self.steps[data.id]] == 'items':
            if data.content.lower() in ['wszystkie', 'wszystkie potrzebne', 'wszystko', 'wszystko potrzebne', 'cokolwiek', 'nic']:
                return await self.bot.message(self.channel, "Doprecyzuj, co takiego obecnie przy sobie posiadasz?")
        return None

    async def edit(self, *args, data, **kwargs):
        if not self.lock:
            #self.last = data
            self.lock = True
            if data.id in self.steps:
                r = await self._handle_error_edit(data=data)
                if r is not None:
                    self.last_error_message = r.id
                    self.lock = False
                    return
                elif self.last_error_message is not None:
                    self.bot.delete_message(self.channel, self.last_error_message)
                    self.last_error_message = None
                #self.answers[self.order[self.steps[data.id]]] = data.content
                self.answers[self.order[self.steps[data.id]]] = upperfirst(data.content)
                print(self.order[self.steps[data.id]], data.content)
            embed = self.createEmbed()
            await self.bot.edit_message(self.channel, self.first_embed["id"], "", embed.embed)
            self.lock = False
    async def react(self, *args, data, **kwargs):
        if data.emoji.name == '✅':
            await self.confirmed()
            return await self.end()

    async def intro(self):
        '''Entry'''
        #Wędrując samotnie natrafiasz na Tawernę, jedyny otwarty obecnie lokal w okolicy. Postanawiasz zajrzeć do środka.
        #Wędujesz samotnie drogą aż w pewnym momencie natrafiasz na Tawernę, jedyny lokal sprawiający wrażenie będącego otwartym w okolicy, postanawiasz zajrzeć do środka.
        #Samotnie Wędując w pewnym momencie natrafiasz na Tawernę - jedyny lokal sprawiający wrażenie będącego otwartym obecnie w okolicy - postanawiasz zajrzeć do środka.
        await self.bot.message(self.channel, "Wędrując samotnie natrafiasz na Tawernę, jedyny otwarty obecnie lokal w okolicy. Postanawiasz zajrzeć do środka.")
        await self.bot.trigger_typing_indicator(self.channel)
        await asyncio.sleep(3)
        '''Inside'''
        #W środku słyszysz muzykę lecz nie możesz jeszcze zlokalizować jej źródła, przy kontuarze znajduje się grupa osób wraz z dziwną maszyną. 
        #Spoglądając na resztę (/Rozglądając się po wnętrzu?) pomieszczenia dostrzegasz scenę po lewej stronie oraz schody na piętro oraz do piwnicy w prawym rogu pomieszczenia. 
        #Większość stolików wydaje się być pusta.
        #/W środku znajdujesz grupę przy kontuarze, większość stolików jest obecnie pusta. Na lewo znajduje się pusta scena a na prawo są schody.
        #/Wchodąc do środka spotykasz grupę przy kontuarze, większość stolików wydaje się być pusta. Na lewo znajduje się obecnie pusta scena a na prawo są schody.
        await self.bot.message(self.channel, "W środku słyszysz muzykę lecz nie możesz jeszcze zlokalizować jej źródła, przy kontuarze znajduje się grupa osób wraz z dziwną maszyną.")
        await self.bot.trigger_typing_indicator(self.channel)
        await asyncio.sleep(3)
        await self.bot.message(self.channel, "Rozglądając się po wnętrzu pomieszczenia dostrzegasz scenę po lewej stronie oraz schody na piętro jak również do piwnicy w prawym rogu pomieszczenia.")
        await self.bot.trigger_typing_indicator(self.channel)
        await asyncio.sleep(4)
        await self.bot.message(self.channel, "Większość stolików wydaje się być pusta.")
        await self.bot.trigger_typing_indicator(self.channel)
        await asyncio.sleep(2)
        '''Menu'''
        await self.bot.message(self.channel, "Tuż po wejściu pojawia się obok ciebie obłok dymu z którego wyłania się karta Menu:")
        await self.bot.trigger_typing_indicator(self.channel)
        await asyncio.sleep(2)
        await self.bot.embed(self.channel, "", self.rules.embed)
        await self.bot.trigger_typing_indicator(self.channel)
        await asyncio.sleep(10)
        '''Q'''
        await self.bot.message(self.channel, "Tajemnicza Maszyneria zaczyna wydawać dziwne dźwięki i pojawia się przed tobą drugi obłok dymu z którego pokazuje się następna karta tym razem nazwana Kwestionariusz:")
        await self.bot.trigger_typing_indicator(self.channel)
        await asyncio.sleep(3)
        self.first_embed = await self.bot.embed(self.channel, "", self.embed.embed)
        await self.bot.trigger_typing_indicator(self.channel)
        await asyncio.sleep(1)
        await self.begin()

    async def begin(self):
        await self.bot.message(self.channel, "Skąd Przybywasz?")
        self.first = self.last.id

    async def placeoforigin(self):
        if 'placeoforigin' in self.answers and self.answers['placeoforigin'].lower() in ['z dalekiej krainy', 'z bardzo daleka','z bardzo dalekiej krainy', 'zniknąd', 'zewsząd']:
            await self.bot.message(self.channel, "Skąd dokładnie przybywasz?")    
            return True
        await self.bot.message(self.channel, "Jak się nazywasz?")

    async def who(self):
        if "profession" in self.answers and self.answers['profession'].lower() in ['nieznany', 'nieznana', 'nic', 'brak']:
            await self.bot.message(self.channel, "Podaj swoją profesję mordko")
            return True
        await self.bot.message(self.channel, "Czym się zwykle zajmujesz, to jest, jak się nazywa twoja profesja?")

    async def profession(self):
        await self.bot.message(self.channel, "Czym, jakiej rasy bądź gatunku jesteś?")#"Czym jesteś?/Jakiej jesteś rasy?/Jakiego gatunku jesteś?")

    async def race(self):
        if self.answers['race'].lower() in ['hybryda', 'mieszaniec', 'mieszanka','zwierz', 'zwierzę', 'zwierzęcie']:
            if 'hybryda' in self.answers['race'].lower():
                await self.bot.message(self.channel, "Hybryda jakich ras?")
            elif self.answers['race'].lower() in ['zwierz', 'zwierzę', 'zwierzęcie']:
                await self.bot.message(self.channel, "Jakie zwierzęcie?")
            else:
                await self.bot.message(self.channel, "Mieszanka jakich gatunków?")
            return True
        await self.bot.message(self.channel, "Jakiej jesteś płci?")# (M/K)")

    async def gender(self):
        if self.answers["gender"][0].lower() in ["m", "k",'d','f']:
            if self.answers["gender"][0].lower() in ["k",'d']:
                self.g = "a"
            else:
                self.g = "e"
            await self.bot.message(self.channel, "Jaki jest twój wiek?")
            return
        #        if 'age' in self.answers and self.answers['age'].isdigit():
        #           await self.bot.message(self.channel, 'W jaki sposób trafiłeś do Tawerny? Gdzie byłeś?')
        #           return
        await self.bot.message(self.channel, "Binarna płeć mordo.\nM - Mężczyna\nK - Kobieta")  #'Jaki jest twój wiek?')
        return True

    async def age(self):
        if self.answers["age"].isdigit():
            await self.bot.message(self.channel, f"Co się przed chwilą wydarzyło? To jest, gdzie był{self.g}ś, co robił{self.g}ś, w jaki sposób trafił{self.g}ś do Tawerny?")# zanim trafił{self.g}ś do Tawerny?") #W jaki sposób trafił{self.g}ś do Tawerny?
            return
        await self.bot.message(self.channel, "Podaj cyfrę.")
        # self.currentStep -= 1
        return True

    async def whereabouts(self):
        if "whereabouts" in self.answers and ((self.answers["whereabouts"].lower() == "nic") or (((len(set(self.answers['whereabouts'].lower().split(' '))) < 3) and len(self.answers['whereabouts']) < 10))):
            if self.answers['whereabouts'].lower() == "nic":
                await self.bot.message(self.channel, f"Raczej nie nic, w jakiś sposób się tutaj musiał{self.g}ś znaleźć. W jaki?")
            elif (len(set(self.answers['whereabouts'].lower().split(' '))) < 3) and len(self.answers['whereabouts']) < 10:
                await self.bot.message(self.channel, "Doprawdy? Dodaj może odrobinę więcej detali mordko?")
            else:
                await self.bot.message(self.channel, "Niby jest. A jednak się nie zgadza.")
            return True
        await self.bot.message(self.channel, "Kto ci Polecił Tawernę? (Jeśli ktokolwiek, w innym przypadku wstaw `-`)")
        #"Kto lub Co cię sprowadza do Tawerny?")  #/Kto za ciebie ręczy?")
    
    async def ref(self):
        await self.bot.message(self.channel, f"Co cię sprowadza do Tawerny? To jest, Czego (lub kogo) tutaj szukasz, co takiego masz nadzieję tu znaleźć/zastać? Bądź Co sprawiło że zajrzał{self.g}ś do Tawerny?")#"Kto za Ciebie ręczy? (Jeśli ktokolwiek, w innym przypadku wstaw `-`)") #Kto ci Polecił Tawernę? (Jeśli ktokolwiek, w innym przypadku wstaw `-`)

    async def reason(self):
        #if "reason" in self.answers and ("Mmesek".lower() in self.answers["reason"].lower() or "Mms".lower() in self.answers["reason"].lower()):
        #    await self.bot.message(self.channel, "Raczej nie mordko. To Jego Tawerna.")
        #    return True
        await self.bot.message(
            self.channel, "Jaki jest twój ulubiony kolor? *(Dla najlepszego rezultatu w formacie `r,g,b` bądź `#hex`)*"
        )

    async def color(self):
        await self.bot.message(self.channel, "Jaki jest twój ulubiony trunek bądź napój?")# bądź potrawa?")

    async def drink(self):
        if "drink" in self.answers and self.answers['drink'].lower() in self.wrong_answers:
            await self.bot.message(self.channel, "O, naprawdę? Zupełnie nic? Jesteś tego aby na pewno pewn{}? Jaki jest twój ulubiony trunek bądź napój?".format('y' if self.g == 'e' else self.g))
            return True
        await self.bot.message(self.channel, "Czego nie cierpisz?")

    async def hate(self):
        if "hate" in self.answers and self.answers['hate'].lower() in self.wrong_answers:
            await self.bot.message(self.channel, "Raczej nie mordko, coś tam jest.")
            return True
        await self.bot.message(self.channel, "Czym jest twój strach?")

    async def fear(self):
        if "fear" in self.answers and self.answers['fear'].lower() in self.wrong_answers:
            await self.bot.message(self.channel, "Raczej nie mordko, coś tam jest.")
            return True
        await self.bot.message(self.channel, "Czym jest twoja słabość?")

    async def weakness(self):
        if "weakness" in self.answers and self.answers['weakness'].lower() in self.wrong_answers:
            await self.bot.message(self.channel, "Raczej nie mordko, coś tam jest.")
            return True
        await self.bot.message(self.channel, "Jaka jest twoja siła?")

    async def strength(self):
        if "strength" in self.answers and self.answers['strength'].lower() in self.wrong_answers:
            await self.bot.message(self.channel, "Raczej nie mordko, coś tam jest.")
            return True
        await self.bot.message(self.channel, "Jakie przedmioty ze sobą posiadasz?")# *(Do trzech, po przecinku `,`)*")

    async def items(self):
        if "items" in self.answers and self.answers['items'].lower() in ['wszystkie', 'wszystkie potrzebne', 'wszystko', 'wszystko potrzebne', 'cokolwiek', 'nic']:
            await self.bot.message(self.channel, "Doprecyzuj, co takiego obecnie przy sobie posiadasz?")
            return True
        await self.bot.message(self.channel, "Jaka jest Twoja historia?")

    async def story(self):
        if "story" in self.answers and ((self.answers["story"].lower() == "długa") or (((len(set(self.answers['story'].lower().split(' '))) < 5) and len(self.answers['story']) < 20))):
            if self.answers['story'].lower() == "długa":
                await self.bot.message(self.channel, "To bardzo fajnie że jest długa mordko. A teraz ją tutaj opowiedz. Z detalami.")
            elif (len(set(self.answers['story'].lower().split(' '))) < 5) and len(self.answers['story']) < 20:
                await self.bot.message(self.channel, "Nie za długa ta historia mordko tak więc zapytam raz jeszcze: Jaka jest Twoja historia?")
            else:
                await self.bot.message(self.channel, "Niby jest. A jednak się nie zgadza.")
            return True
        embed = self.createEmbed()
        await self.bot.edit_message(self.channel, self.first_embed["id"], "", embed.embed)
        c = await self.bot.embed(self.channel, "", embed.embed)
        self.first_embed = c
        self.confirm = c['id']
        await self.bot.create_reaction(self.channel, c['id'], '✅')
        await self.bot.message(self.channel, "✅ Potwierdź aby potwierdzić wybory. Możesz edytować odpowiednie wiadomości aby zmienić odpowiedzi zanim potwierdzisz.")
    async def confirmed(self):
        embed = self.createEmbed()
        await self.bot.webhook([embed.embed], "", "721248452679434251/QEmhIELl-7VsyBbro2jP0U6GbbHAOay_xe1aqMa1Mhw1vcKaXAH4k6CYH16g1lyOzQhw", self.last.author.username)
        #await self.bot.embed("474917631745327114", "", embed.embed)
        await self.bot.trigger_typing_indicator(self.channel)
        session = self.bot.db.sql.session()
        a = self.answers
        character = db.RolePlayCharacters(self.guild, self.user, a['who'], a['age'], self.getIntFromColor(a['color']), a['profession'], a['gender'], a['race'])
        character.Level = 0
        character.Skills = {}
        character.Items = {}
        if ',' in self.answers['items']:
            items = [upperfirst(i.strip()) for i in self.answers['items'].split(',')]
        else:
            items = [upperfirst(i.strip()) for i in self.answers['items'].split('\n')]
        #for i in [upperfirst(i.strip()) for i in self.answers['items'].split(',')[:3]]:
        for i in items[:3]:
            character.Items[i] = 1
        character.Origin = self.answers['placeoforigin']
        character.Story = self.answers['story']
        character.Goals = {"ref":self.answers['ref'], "reason":self.answers['reason']}
        character.Favorites = {"drink":self.answers['drink'], "hate":self.answers['hate'], "fear":self.answers['fear'],"weakness":self.answers['weakness'], "strength":self.answers['strength']}
            
        self.bot.db.sql.add(character)
        session.commit()
        await asyncio.sleep(1)
        from random import SystemRandom
        choice = SystemRandom().choice
        call = ["Chwilę później Bartender Cię woła", "Po chwili Bartender Cię woła", "Bartender po chwili Cię woła"]
        await self.bot.message(self.channel, "*{call}.*\n→ <#463437626515652618> ←".format(call=choice(call)))#""*.*\n→ <#463437626515652618> ←")
        #await self.bot.trigger_typing_indicator(self.channel)
        await asyncio.sleep(0.5)
        #s = "Witaj {Przybyszu}! Co się do nas sprowadza, napijesz się czegoś może?"
        s = "{welcome} {who}! {question} {drink}?"
        welcome = ["Witaj","Jak się masz","Witamy,"]
        who = {"m": ["Podróżniku", "Poszukiwaczu Przygód", "Awanturniku", "Nieznajomy", "Nowy", "Tułaczu", "Wędrowcze"], "f": ["Podróżniczko", "Poszukiwaczko Przygód", "Awanturniczko", "Nieznajoma", "Nowa", "Białogłowa", "Niewiasto", "Wędrowniczko"], "any": ["Przybyszu", "Obcy", ]}
        question = ["Co się do nas sprowadza,", "Jak przebiegła podróż,", "Nie wyglądasz najlepiej,", "Mamy nadzieję że przyniosłeś pizzę!", "Mam nadzieję że obyło się bez problemów w drodze,", "", "Niezł{ending} {item}.", "Zostaw bronie przy drzwiach,"]
        drink = ["Napijesz się czegoś może", "Nalać może jakiegoś trunku", "Jakieś problemy w drodze", "Nalać może jakiego trunku", "Nalać może czegoś", "Może czego nalać", "Planujesz może dłuższy pobyt", "Zatrzymasz się u nas",
                "Zechcesz może {beverage}", "Napijesz się może {beverage}", "Nalać może {beverage}","Potrzebujesz czego", "Podać {beverage}"]
        if self.g == 'a':
            w = who['f'] + who['any']
        else:
            w = who['m'] + who['any']
        #items = self.answers['items'].split(',')[:3]
        #if ',' in self.answers['items']:
        #    items = ['- ' + upperfirst(i.strip()) for i in self.answers['items'].split(',')]
        #else:
        #    items = ['- ' + upperfirst(i.strip()) for i in self.answers['items'].split('\n')]
        items= items[:3]
        chosen_item = choice(items)
        if chosen_item.strip()[-1] in ['a','ą','ę']:
            gi = 'a'
        elif chosen_item.strip()[-1] in ['e', 'i', 'o', 'u', 'y']:
            gi = 'e'
        else:
            gi = 'y'

        s = s.format(welcome=choice(welcome), who=choice(w),question=choice(question).format(ending=gi, item=chosen_item), drink=choice(drink).format(beverage=self.answers['drink']))

        await self.bot.message(463437626515652618, f'*Bartender wita <@{self.user}>*: "{s}"')
        await self.bot.add_guild_member_role(self.guild, self.user, 466370566665011200, "Created RolePlay character")
        await self.end()
