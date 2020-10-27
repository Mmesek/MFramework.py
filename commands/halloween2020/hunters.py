from MFramework.database import alchemy as db

from datetime import timedelta
from random import SystemRandom

from .helpers import *
from .helpers.utils import _t

@Hunters(alias='protect', help="Protects fellow hunter from being bitten")
async def defend(self, *user, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    s = self.db.sql.session()
    self_user = get_user(data.guild_id, data.author.id, s)
    if self_user is None or self_user.CurrentClass not in HUNTERS:
        return

    now = get_current_time()
    if self_user.ActionCooldownEnd is not None:
        if now < self_user.ActionCooldownEnd:
            cooldown = self_user.ActionCooldownEnd - now
            return await self.message(data.channel_id, _t("remaining_cooldown", language, cooldown=cooldown))

    target = get_user_id(user)
    if target == data.author.id:
        return await self.message(data.channel_id, _t("failed_defend", language))
    target_user = s.query(db.HalloweenClasses).filter(db.HalloweenClasses.GuildID == data.guild_id, db.HalloweenClasses.UserID == target).first()
    
    if target_user.CurrentClass not in HUNTERS:
        return await self.message(data.channel_id, _t("cant_defend", language))
    
    if target_user.ProtectionEnds is None or target_user.ProtectionEnds < now:
        duration = SystemRandom().randint(5, 40)
        delta = now + timedelta(minutes=duration)
        target_user.ProtectedBy = data.author.id
        target_user.ProtectionEnds = delta
        self_user.ActionCooldownEnd = now + timedelta(hours=1)
        s.add(db.HalloweenLog(data.guild_id, target_user.UserID, target_user.CurrentClass, target_user.CurrentClass, self_user.UserID, now))
        s.commit()
        return await self.message(data.channel_id, _t("success_defend", language, duration=duration))

    return await self.message(data.channel_id, _t("error_defend", language))

@Hunters(help="Tries to convince a monster you are hunting to join the cause and fight with darkness")
async def betray(self, *user, data, language, **kwargs):
    '''Extended description to use with detailed help command'''
    s = self.db.sql.session()
    self_user = get_user(data.guild_id, data.author.id, s)
    if self_user is None or self_user.CurrentClass not in HUNTERS:
        return
    now = get_current_time()
    if self_user.ActionCooldownEnd is not None and now < self_user.ActionCooldownEnd:
        cooldown = self_user.ActionCooldownEnd - now
        return await self.message(data.channel_id, _t("remaining_cooldown", language, cooldown=cooldown))
    roll = SystemRandom().randint(0, 100)
    self_user.ActionCooldownEnd = now + timedelta(hours=4)
    s.commit()
    if roll > 92:
        await turning_logic(self, data, user, HUNTERS, True, skip_cooldown=True)
        return await self.message(data.channel_id, _t("success_betray", language))
    return await self.message(data.channel_id, _t("error_betray", language))
