from sqlalchemy import Column, TIMESTAMP, Integer, String, BigInteger, ForeignKey, func
from sqlalchemy.orm import declared_attr, Query, relationship
from sqlalchemy.sql.sqltypes import Interval
from typing import List
class Base:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__  #.lower()
    @classmethod
    def filter(cls, session, **kwargs) -> Query:
        ''':param kwargs: Column = Value''' 
        return session.query(cls).filter_by(**kwargs)
    @classmethod
    def fetch_or_add(cls, s, **kwargs) -> object:
        m = cls.filter(s, **kwargs).first()
        if not m:
            m = cls(**kwargs)
            s.add(m)
        return m
    @classmethod
    def fetch_or_add_multiple(cls, s, *ids: int) -> List[object]:
        objects = []
        for id in ids:
            objects.append(cls.fetch_or_add(s, id=id))
        return objects
    @classmethod
    def by_id(cls, s, id: int) -> object:
        return cls.filter(s, id = id).first()
    @classmethod
    def by_name(cls, s, name: str) -> object:
        return cls.filter(s, name = name).first()
#    def __repr__(self) -> str:
#        return "{}({})".format(
#            self.__class__.__name__,
#            ", ".join(["{}={!r}".format(attr, getattr(self, attr)) for attr in vars(self) if not attr.startswith('_')])
#        )
    def __init__(self, **kwargs) -> None:
        for key, value in kwargs.items():
            setattr(self, key, value)


from sqlalchemy.orm import declarative_base
Base = declarative_base(cls=Base)

class ID:
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

class Default(ID):
    name = Column(String, unique=True, nullable=False)
    def __init__(self, name) -> None:
        self.name = name

class File(ID):
    filename = Column(String)

class Snowflake:
    id = Column(BigInteger, primary_key=True, autoincrement=False, nullable=False)

class Timestamp:
    timestamp = Column(TIMESTAMP(timezone=True), server_default=func.now())

class TimestampUpdate:
    timestamp = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

class Cooldown:
    cooldown = Column(Interval)

class ForeignMixin:
    _table: str = None

class TypeID:
    @declared_attr
    def type_id(cls):
        return Column(ForeignKey("Type.id"), nullable=False)

class ServerID:
    @declared_attr
    def server_id(cls):
        return Column(ForeignKey("Server.id", ondelete='Cascade', onupdate='Cascade'), primary_key=False, nullable=False)
    #@declared_attr
    #def server(cls):
    #    return relationship("Server", foreign_keys=f"{cls.__name__}.server_id", lazy=True)

class UserID:
    @declared_attr
    def user_id(cls): 
        return Column(ForeignKey("User.id", ondelete='Cascade', onupdate='Cascade'), primary_key=False, nullable=False)
    #@declared_attr
    #def user(cls):
    #    return relationship("User", foreign_keys=f"{cls.__name__}.user_id", lazy=True)

class RoleID:
    @declared_attr
    def role_id(cls):
        return Column(ForeignKey("Role.id", ondelete='Cascade', onupdate='Cascade'))
    @declared_attr
    def role(cls):
        return relationship("Role", foreign_keys=f"{cls.__name__}.role_id", lazy=True)

class ChannelID:
    @declared_attr
    def channel_id(cls):
        return Column(ForeignKey("Channel.id", ondelete='Cascade', onupdate='Cascade'))
    @declared_attr
    def channel(cls):
        return relationship("Channel", foreign_keys=f"{cls.__name__}.channel_id", lazy=True)

class ItemID:
    @declared_attr
    def item_id(cls):
        return Column(ForeignKey("Item.id", ondelete='Cascade', onupdate='Cascade'), primary_key=True)
    @declared_attr
    def item(cls):
        return relationship("Item", foreign_keys=f"{cls.__name__}.item_id", lazy=True)

class SkillID:
    @declared_attr
    def skill_id(cls):
        return Column(ForeignKey("Skill.id", ondelete='SET NULL', onupdate='Cascade'), primary_key=True)
    @declared_attr
    def skill(cls):
        return relationship("Skill", foreign_keys=f"{cls.__name__}.skill_id", lazy=True)

class LocationID:
    @declared_attr
    def location_id(cls):
        return Column(ForeignKey("Location.id", ondelete='Cascade', onupdate='Cascade'))
    @declared_attr
    def location(cls):
        return relationship("Location", foreign_keys=f"{cls.__name__}.location_id", lazy=True)

class EventID:
    @declared_attr
    def event_id(cls):
        return Column(ForeignKey("Event.id", ondelete='SET NULL', onupdate='Cascade'))
    @declared_attr
    def event(cls):
        return relationship("Event", foreign_keys=f"{cls.__name__}.event_id", lazy=True)

class CharacterID:
    @declared_attr
    def character_id(cls):
        return Column(ForeignKey("Character.id", ondelete='Cascade', onupdate='Cascade'), primary_key=True)
    #@declared_attr
    #def character(cls):
    #    return relationship("Character", foreign_keys=f"{cls.__name__}.character_id", lazy=True)
