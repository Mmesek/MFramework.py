# -*- coding: utf-8 -*-
"""
Commands
----------

Command registery & execution framework

:copyright: (c) 2021 Mmesek

"""

from mlib.types import Enum
from typing import Union


class Groups(Enum):
    SYSTEM = 0
    OWNER = 5
    ADMIN = 10
    MODERATOR = 20
    HELPER = 30
    SUPPORT = 40
    PARTNER = 50
    NITRO = 60
    SUPPORTER = 70
    VIP = 80
    GLOBAL = 100
    EVERYONE = 100
    DM = 200
    MUTED = 210
    LIMBO = 220

    def can_use(self, value: Union["Groups", int]) -> bool:
        """Checks if Group is higher or equal than provided one
        Parameters
        ----------
        value:
            Group to compare to. For example, Minimal group that can use"""
        return self.value <= (value if type(value) is int else value.value)


from .decorators import *  # noqa: F401
