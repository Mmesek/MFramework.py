from dataclasses import dataclass

from MFramework.commands import Groups

from . import Context


class Role:
    server_id: int
    role_id: int


@dataclass
class Role_Permission:
    id: int
    power_level: Groups = Groups.EVERYONE
    permission: int = 0

    def has(self, permission: int) -> bool:
        return self.permission & permission == permission

    def add(self, permission: int):
        self.permission |= permission

    def remove(self, permission: int):
        self.permission &= ~permission


@dataclass
class Command_Permission:
    id: int
    command: str
    allow: bool = None
    deny: bool = None

    def __init__(self, id: int, command: str, allow: bool):
        self.id = id
        self.command = command
        if allow:
            self.allow = True
        else:
            self.deny = True


BOT_OWNER_ID = 0


def get_power(permissions: list[Role_Permission], roles: list[int]) -> int:
    try:
        return min([(i.power_level, i.id) for i in permissions if i.id in roles])[0]
    except (IndexError, ValueError):
        return Groups.EVERYONE


class Permission:
    name: str
    permission: int
    level: int = Groups.EVERYONE
    cache: dict

    def has(self, permissions: list[Role_Permission]) -> bool:
        return any([i for i in permissions if i.has(self.permission)])

    def overwrites(self) -> bool:
        return self.cache.commands.get(self.name)

    def check_overwrites(self, permissions: list[Role_Permission] = None):  # , roles: list[int] = None):
        overwrites = self.overwrites()  # If command is denied
        if (type(overwrites) is bool and not overwrites) or (  # If command is not allowed or not set
            not self.has(permissions)  # If permission is not enough
            # and not (roles and get_power(permissions, roles) >= self.level)  # If level is too low (too high number)
        ):
            return False
        return True


class Permission_Context(Context):
    _cmd_permission: Permission

    @property
    def permission_level(self) -> int:
        if not self.is_dm:
            if self.user_id != BOT_OWNER_ID:
                if self.user_id != self.cache.guild.owner_id:
                    return get_power(self.cache.user_permissions(self.user_id), self.cache.user_roles(self.user_id))
                return Groups.OWNER.value
            return Groups.SYSTEM.value
        return Groups.DM.value

    def can_use(self, required_power: Groups) -> bool:
        if self._cmd_permission.check_overwrites(self.cache.user_permissions(self.user_id)):
            return True
        elif self.permission_level <= required_power.value:
            return True
        return False
