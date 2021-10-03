from typing import Dict, Set

from MFramework import Snowflake, Guild_Member
from MFramework.commands import Groups

class Base:
    name: str
    color: int
    bot: Guild_Member
    groups: Dict[Groups, Set[Snowflake]]
    def __init__(self, *, bot, **kwargs) -> None:
        self.groups = {i:set() for i in Groups}
        self.setBot(bot.user_id)
        if self.bot:
            self.setColor()

    def setBot(self, user_id):
        self.bot = self.members[user_id]
        if self.bot:
            self.calculate_permissions()

    def setColor(self):
        color = None
        for role_id in self.bot.roles:
            role = self.roles[role_id]
            if role.managed is True:
                color = (role.position, role.color, True)
            elif color == None:
                color = (role.position, role.color, False)
            elif role.position > color[0] and color[2] != True:
                color = (role.position, role.color, False)
        self.color = color[1] if color else None
    
    def calculate_permissions(self):
        for role in self.bot.roles:
            self.permissions |= int(self.roles[role].permissions)
    
    def cachedRoles(self, roles):
        for group in self.groups:
            if any(i in roles for i in self.groups[group]):
                return group
        return Groups.GLOBAL

class Commands(Base):
    alias: str = '?'

    _permissions_set: bool = False