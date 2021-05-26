import enum
from mlib.types import Enum
class Infraction(Enum):
    Warn = 0
    Mute = 1
    Kick = 2
    Ban = 3
    Temp_Mute = 4
    Temp_Ban = 5
    Unban = 6
    Unmute = 7
    Limbo = 8
    DM_Mute = 9
    DM_Unmute = 10

class Snippet(Enum):
    Snippet = 0
    Regex = 1
    Rule = 2
    Emoji = 3
    Reaction = 4
    Canned_Response = 5
    Meme = 6
    Blacklisted_Word = 7
    Whitelisted = 8
    Response_Reaction = 9

class Statistic(Enum):
    Chat = 0
    Voice = 1
    Game = 2
    Spotify = 3
    Infractions_Active = 4
    Infractions_Total = 5

    DM_Total = 10
    DM_Forwarded = 11
    Spawned_Eggs = 12
    Spawned_Presents = 13

    Halloween_Turn_Count = 20

from datetime import date
from mdiscord import Snowflake
class Setting(Enum):
    Flags = int, 0#, enum.IntFlag # Tracking
    Permissions = int, 1#, enum.IntFlag
    Color = int, 2
    Exp = int, 3
    Voice_Exp = int, 4
    Gender = bool, 5

    Timezone = str, 6
    Birthday = date, 7
    Locale = str, 8
    Region = str, 9
    Currency = float, 10
    Alias = str, 11

    Dynamic = bool, 12
    Buffer = bool, 13
    RPG = bool, 14

    Level = int, 15
    Reaction = str, 16
    Presence = str, 17
    Custom = Snowflake, 18
    Activity = int, 19
    Voice_Link = Snowflake, 20
    Special = str, 21
    Group = str, 22

    ServerID = Snowflake, 23
    ChannelID = Snowflake, 24
    MessageID = Snowflake, 25
    RoleID = Snowflake, 26
    UserID = Snowflake, 27
    Allowed_Duplicated_Messages = int, 28

class Item(Enum):
    SYSTEM = 0 # Metadata Items
    Entity = 0 # Mobs
    Race = 0 # Race

    Event = 1 # Event Items

    Currency = 2 # Valuable on it's own
    Energy = 2 # Non static values like electric current or mana
    Fluid = 2 # Water
    
    Resource = 3 # Rocks
    Gift = 4 # Presents, items obtainable only via receiving from someone 
    
    Weapon = 5 # Offensive
    Protection = 6 # Defensive
    
    Tool = 7 # Important utilities, like keys
    Potion = 8 # Consumable with effects
    Recipe = 9 # Crafting recipes
    Spell = 9 # Spells
    Book = 10 # Lore bits?
    
    Knowledge = 11 # Known "things" like recipes/spells
    
    Effects = 11 # Active effects
    #Booster = 11 # Active effects
    #Upgrade = 12 # Grants bonus stats to an item (Same as mod below tbh)
    Modification = 12 # Effects on item 

    Experience = 13 # Experience in certain fields/skills?
    Reputation = 13 # Repuation received from other players (should be stat tbh), Standing with factions?

    Achievement = 14 # Collectible "Static" Achievements for certain actions
    Collectible = 14 # Hidden collectibles. Unlike above, they can be more "fluid"

    Utility = 15 # Usable item
    Miscellaneous = 16 # Fluff?
    Secret = 17 # Even I don't know
    Other = 18 # Catch-all


class Task(Enum):
    Generic = 0
    Giveaway = 1
    Hidden_Giveaway = 2
    Reminder = 3
    Quest = 4

class Rarity(Enum):
    Trash = 0
    Event = 1
    Common = 2
    Uncommon = 3
    Rare = 4
    Epic = 5
    Legendary = 6
    Mythic = 7
    Exotic = 8
    Mystic = 9
    Special = 10
    Artifact = 11
    Relic = 12
    Cursed = 13
    Dark = 14

class Difficulty(Enum):
    Simple = 0
    Rookie = 1
    Novice = 2
    Easy = 3
    Normal = 4
    Hard = 5
    Deadly = 6
    Overkill = 7
    Nightmare = 8
    Hardcore = 9

class Reward(Enum):
    ITEM = Rarity.Common
    JUNK = Rarity.Common
    TWIG = Rarity.Common
    KEY = Rarity.Epic

class Present(Enum):
    WHITE = Rarity.Common
    TWIG = Rarity.Common
    GREEN = Rarity.Uncommon
    BLUE = Rarity.Rare
    RED = Rarity.Epic
    SOCK = Rarity.Event
    DARK = Rarity.Mythic
    CURSED = Rarity.Cursed
    GOLD = Rarity.Legendary

class ItemFlags(enum.IntFlag):
    Exclusive = 1 << 0
    Stackable = 1 << 1
    Tradeable = 1 << 2
    Purchasable = 1 << 3
    Special = 1 << 4
    Event = 1 << 5
    Drinkable = 1 << 6
    Edible = 1 << 7
    Giftable = 1 << 8

class HalloweenRaces(Enum):
    Human = 0, Item.Race
    Vampyre = 1, Item.Race
    Werewolf = 2, Item.Race
    Zombie = 3, Item.Race
    Hunter = 4, Item.Race
    Huntsmen = 5, Item.Race
    Enchanter = 6, Item.Race

class Flags(enum.IntFlag):
    Chat = 1 << 0
    Voice = 1 << 1
    Presence = 1 << 2
    Activity = 1 << 3
    Nitro = 1 << 4