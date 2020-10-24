IMMUNE_TABLE = {
    "Vampire": "Vampire Hunter",
    "Werewolf": "Huntsman",
    "Zombie": "Zombie Slayer",
    "Zombie Slayer": "Zombie",
    "Huntsman": "Werewolf",
    "Vampire Hunter": "Vampire"
}
MONSTERS = ['Vampire', "Werewolf", "Zombie"]
HUNTERS = ["Vampire Hunter", "Huntsman", "Zombie Slayer"]
DRINKS = {
    "wine": "Vampire",
    "bloody red wine": "Vampire",
    "moonshine": "Werewolf",
    "vodka": "Zombie",
    'vodka braaaainzz?': "Zombie",
    "nightmare":"random"
}
ROLES = ["Human",
    "Vampire", "Werewolf",
    "Zombie", "Vampire Hunter",
    "Huntsman", "Zombie Slayer"]
from enum import Enum
class Responses(Enum):
    ERROR = 0
    CANT = 1
    SUCCESS = 2
    FAILED = 3
    IMMUNE = 4
    COOLDOWN = 5
    AVAILABLE = 6
    PROTECTED = 7
    OTHER = 8

from datetime import timedelta
COOLDOWNS = {
    "defend": timedelta(hours=1),
    "cure": timedelta(hours=2),
    "bite": timedelta(hours=3),
    "betray": timedelta(hours=4)
}
_HGROUPS = {}
_HHELP = {}