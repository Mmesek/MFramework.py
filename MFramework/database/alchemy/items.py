from sqlalchemy import Column, Integer, ForeignKey, Enum, Float, UnicodeText, TIMESTAMP, String
from sqlalchemy.orm import relationship
from . import types

from .mixins import *

class Location(Default, Cooldown, Base):
    pass

class Event(Default, Base):
    start = Column(TIMESTAMP(True))
    end = Column(TIMESTAMP(True))
    def __init__(self, name, start, end):
        self.name = name
        self.start = start
        self.end = end

class Item(Default, Cooldown, Base):
    type = Column(Enum(types.Item), nullable=False)
    descriptin = Column(UnicodeText)
    global_limit = Column(Integer)
    rarity = Column(Enum(types.Rarity))
    worth = Column(Integer, default=0)
    durability = Column(Integer)
    repairs = Column(Integer)
    damage = Column(Integer)
    flags = Column(Integer, default=0)
    req_skill = Column(ForeignKey('Skill.id', ondelete='SET NULL', onupdate='Cascade'))
    
    icon = Column(String, nullable=True)
    emoji = Column(String, nullable=True)
    def __init__(self, name, _type) -> None:
        super().__init__(name)
        self.type = _type if type(_type) is not str else types.Item.get(_type)

class Inventory(ItemID, UserID, Base):
    user_id = Column(ForeignKey("User.id", ondelete='Cascade', onupdate='Cascade'), primary_key=True, nullable=False)
    quantity = Column(Integer, default=0)
    item = relationship("Item")
    def __init__(self, Item=None, quantity=1):
        self.item = Item
        self.quantity = quantity

class Drop(ItemID, LocationID, EventID, Base):
    location_id = Column(ForeignKey("Location.id", ondelete='Cascade', onupdate='Cascade'), primary_key=True)
    weight = Column(Float)
    chance = Column(Float)
    region_limit = Column(Integer)
    quantity_min = Column(Integer, default=0)
    quantity_max = Column(Integer, default=1)
    
    item = relationship("Item", uselist=False)
    location = relationship("Location", uselist=False)
    event = relationship("Event", uselist=False)

from . import types# as types
class Items:
    Coin = types.Item.Currency
    Crypto = types.Item.Currency

    Material = types.Item.Resource
    Scrap = types.Item.Resource
    Junk = types.Item.Resource
    Trash = types.Item.Resource
    Metal = types.Item.Resource
    Ore = types.Item.Resource
    Ingot = types.Item.Resource

    Liquid = types.Item.Fluid

    Food = types.Item.Resource
    Drink = types.Item.Resource
    Cookie = types.Item.Resource
    Beverage = types.Item.Resource

    Sword = types.Item.Weapon
    Bow = types.Item.Weapon

    Advent = types.Item.Event
    EasterEgg = types.Item.Event

    Upgrade = types.Item.Modification
    Enemy = types.Item.Entity
    NPC = types.Item.Entity
    Ally = types.Item.Entity

