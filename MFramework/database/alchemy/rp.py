from sqlalchemy.orm import relationship
from .modern_alchemy import Base
from sqlalchemy import Column, String, Integer, Boolean, UnicodeText
from .mixins import *


class Skill(Default, Base):
    pass

class Character_Skills(SkillID, CharacterID, Base):
    skill_id = Column(ForeignKey("Skill.id", ondelete='Cascade', onupdate='Cascade'), primary_key=True)
    exp = Column(Integer, default=0)

class Character_Items(ItemID, CharacterID, Base):
    quantity = Column(Integer, default=0)

class Character(UserID, ID, Base):
    name = Column(String)
    race = Column(String)
    gender = Column(Boolean)
    age = Column(Integer)
    color = Column(Integer)

    profession = Column(String)
    place_of_origin = Column(UnicodeText)
    story = Column(UnicodeText)

    drink = Column(String)
    hate = Column(String)
    fear = Column(String)
    weakness = Column(String)
    strength = Column(String)
    skills = relationship("Character_Skills")
    items = relationship("Character_Items")
