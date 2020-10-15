from MFramework.commands import register
from MFramework.database import alchemy as db
from datetime import datetime, timedelta, timezone
from MFramework.utils.utils import parseMention
immune_table = {
    "Vampire": "Vampire Hunter",
    "Werewolf": "Huntsman",
    "Zombie": "Zombie Slayer",
    "Zombie Slayer": "Zombie",
    "Huntsman": "Werewolf",
    "Vampire Hunter": "Vampire"
}
monsters = ['Vampire', "Werewolf", "Zombie"]
hunters = ["Vampire Hunter", "Huntsman", "Zombie Slayer"]
drinks = {
    "wine": "Vampire",
    "bloody red wine": "Vampire",
    "moonshine": "Werewolf",
    "vodka": "Zombie",
    'vodka braaaainzz?':"Zombie"    
}
@register(group='Global', help='HALLOWEEN COMMAND', alias='bite, drink, cure, enlist', category='')
async def halloween(self, *class_or_user, data, language, cmd, **kwargs):
    '''Extended description to use with detailed help command'''
    if ' '.join(class_or_user) == 'help':
        await self.message(data.channel_id, 'Available commands are:\nenlist [class] - Join Hunters\ndrink [drink] - Drink an elixir to join the Dark Side™\nbite [user] - Bite someone!\ncure [user] - Bring them back to The Light!')
    s = self.db.sql.session()
    self_user = s.query(db.HalloweenClasses).filter(db.HalloweenClasses.GuildID == data.guild_id, db.HalloweenClasses.UserID == data.author.id).first()
    if self_user is not None and self_user.LastAction is not None and ' '.join(class_or_user) == 'cooldown':
        cooldown = datetime.now(tz=timezone.utc) - self_user.LastAction
        return await self.message(data.channel_id, f"Remaining Cooldown: {timedelta(hours=8) - cooldown}")
    if self_user is None or self_user.CurrentClass == 'Human':
        _class = ' '.join(class_or_user)
        if cmd in ['drink'] and self_user is None and (_class.lower() in ['vampire', 'werewolf', 'zombie'] or _class.lower() in drinks):
            if _class.lower() in drinks:
                _class = drinks.get(_class.lower())
            self_user = db.HalloweenClasses(data.guild_id, data.author.id)
            self_user.CurrentClass = _class.capitalize()
            self.db.sql.add(self_user)
            await self.message(data.channel_id, "Welcome to the Dark Side™. You can now use `bite` command.")
        elif _class.lower() in ['vampire hunter', 'huntsman', 'zombie slayer']:
            self_user = db.HalloweenClasses(data.guild_id, data.author.id)
            self_user.CurrentClass = _class.title()
            self.db.sql.add(self_user)
            await self.message(data.channel_id, "You have successfully joined ranks of hunters. You can now use `cure` command.")
        else:
            if cmd in ['drink'] and self_user is None:
                await self.message(data.channel_id, 'Available drinks:\n- Bloody Red Wine (Become Vampire)\n- Moonshine (Become Werewolf)\n- Vodka "Braaaainzz?" (Become Zombie)')
            elif cmd in ['drink']:
                await self.message(data.channel_id, "Sorry. Drinks are only available to freshbloods")
            elif cmd in ['enlist']:
                await self.message(data.channel_id, 'Available classes:\n- Vampire Hunter\n- Huntsman\n- Zombie Slayer')
    elif cmd in ['drink']:
        await self.message(data.channel_id, "Sorry. Drinks are only available to freshbloods")
    elif cmd in ['enlist']:
        await self.message(data.channel_id, "You have to be human to use that!")
    else:
        if self_user.LastAction == None or (datetime.now(tz=timezone.utc) - self_user.LastAction > timedelta(hours=8)):
            if class_or_user != ():
                target = parseMention(class_or_user[0])
                if target.isdigit():
                    target = int(target)
            else:
                target = None
            target_user = s.query(db.HalloweenClasses).filter(db.HalloweenClasses.GuildID == data.guild_id, db.HalloweenClasses.UserID == target).first()
            if cmd in ['bite'] and self_user.CurrentClass in monsters:
                if (target_user is not None and target_user.CurrentClass not in monsters) or target_user is None:
                    _target_user = False
                    if target_user is None:
                        target_user = db.HalloweenClasses(data.guild_id, target, 'Human')
                        _target_user = None
                    if immune_table.get(target_user.CurrentClass, '') != self_user.CurrentClass:
                        target_user.CurrentClass = self_user.CurrentClass
                        target_user.LastUser = self_user.UserID
                        self_user.LastVictim = target_user.UserID
                        self_user.LastAction = datetime.now(tz=timezone.utc)
                        if self_user.CurrentClass == 'Vampire':
                            self_user.VampireStats += 1
                        elif self_user.CurrentClass == 'Werewolf':
                            self_user.WerewolfStats += 1
                        elif self_user.CurrentClass == 'Zombie':
                            self_user.ZombieStats += 1
                        target_user.TurnCount += 1
                        if _target_user is None:
                            self.db.sql.add(target_user)
                        else:
                            s.merge(target_user)
                        await self.message(data.channel_id, f'Successfully turned <@{target}> into {self_user.CurrentClass}', allowed_mentions={"parse":[]})
                    else:
                        await self.message(data.channel_id, "Your target is immune to that")
                else:
                    await self.message(data.channel_id, "Your target is immune to that")
            elif cmd in ['cure'] and self_user.CurrentClass in hunters:
                if target_user is not None and target_user.CurrentClass not in hunters:
                    if immune_table.get(target_user.CurrentClass) == self_user.CurrentClass:
                        previousClass = target_user.CurrentClass
                        target_user.CurrentClass = 'Human'
                        target_user.LastUser = self_user.UserID
                        self_user.LastVictim = target_user.UserID
                        self_user.LastAction = datetime.now(tz=timezone.utc)
                        if self_user.CurrentClass == 'Vampire Hunter':
                            self_user.VampireHunterStats += 1
                        elif self_user.CurrentClass == 'Huntsman':
                            self_user.HuntsmanStats += 1
                        elif self_user.CurrentClass == 'Zombie Slayer':
                            self_user.ZombieSlayerStats += 1
                        target_user.TurnCount += 1
                        s.merge(target_user)
                        await self.message(data.channel_id, f'Successfully cured <@{target}> from {previousClass}', allowed_mentions={"parse":[]})
                    else:
                        await self.message(data.channel_id, f"Provided user is not {immune_table.get(self_user.CurrentClass)}")
                else:
                    await self.message(data.channel_id, f"Provided user is not {immune_table.get(self_user.CurrentClass)}")
            elif cmd in ['bite'] and self_user.CurrentClass not in monsters:
                await self.message(data.channel_id, f"You can't do that!")
            elif cmd in ['cure'] and self_user.CurrentClass not in hunters:
                await self.message(data.channel_id, f"You can't do that!")
        else:
            cooldown = datetime.now(tz=timezone.utc) - self_user.LastAction
            await self.message(data.channel_id, f"Last action was done less than 8h ago! Remaining Cooldown: {timedelta(hours=8) - cooldown}")
    s.commit()
