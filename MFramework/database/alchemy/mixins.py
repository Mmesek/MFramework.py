from sqlalchemy import Column, BigInteger, ForeignKey
from sqlalchemy.orm import declared_attr, relationship
from sqlalchemy.sql.sqltypes import Interval
from mlib.database import Base, ID, Default, File, Timestamp, TimestampUpdate # noqa: F401
from datetime import timedelta
class Snowflake:
    id: int = Column(BigInteger, primary_key=True, autoincrement=False, nullable=False)

class Cooldown:
    cooldown: timedelta = Column(Interval)

class ForeignMixin:
    _table: str = None

class TypeID:
    @declared_attr
    def type_id(cls) -> int:
        return Column(ForeignKey("Type.id"), nullable=False)

class ServerID:
    @declared_attr
    def server_id(cls) -> int:
        return Column(ForeignKey("Server.id", ondelete='Cascade', onupdate='Cascade'), primary_key=False, nullable=False)
    #@declared_attr
    #def server(cls):
    #    return relationship("Server", foreign_keys=f"{cls.__name__}.server_id", lazy=True)

class UserID:
    @declared_attr
    def user_id(cls) -> int:
        return Column(ForeignKey("User.id", ondelete='Cascade', onupdate='Cascade'), primary_key=False, nullable=False)
    #@declared_attr
    #def user(cls):
    #    return relationship("User", foreign_keys=f"{cls.__name__}.user_id", lazy=True)

class RoleID:
    @declared_attr
    def role_id(cls) -> int:
        return Column(ForeignKey("Role.id", ondelete='Cascade', onupdate='Cascade'))
    @declared_attr
    def role(cls):
        return relationship("Role", foreign_keys=f"{cls.__name__}.role_id", lazy=True)

class ChannelID:
    @declared_attr
    def channel_id(cls) -> int:
        return Column(ForeignKey("Channel.id", ondelete='Cascade', onupdate='Cascade'))
    @declared_attr
    def channel(cls):
        return relationship("Channel", foreign_keys=f"{cls.__name__}.channel_id", lazy=True)

class ItemID:
    @declared_attr
    def item_id(cls) -> int:
        return Column(ForeignKey("Item.id", ondelete='Cascade', onupdate='Cascade'), primary_key=True)
    @declared_attr
    def item(cls):
        return relationship("Item", foreign_keys=f"{cls.__name__}.item_id", lazy=True)

class SkillID:
    @declared_attr
    def skill_id(cls) -> int:
        return Column(ForeignKey("Skill.id", ondelete='SET NULL', onupdate='Cascade'), primary_key=True)
    @declared_attr
    def skill(cls):
        return relationship("Skill", foreign_keys=f"{cls.__name__}.skill_id", lazy=True)

class LocationID:
    @declared_attr
    def location_id(cls) -> int:
        return Column(ForeignKey("Location.id", ondelete='Cascade', onupdate='Cascade'))
    @declared_attr
    def location(cls):
        return relationship("Location", foreign_keys=f"{cls.__name__}.location_id", lazy=True)

class EventID:
    @declared_attr
    def event_id(cls) -> int:
        return Column(ForeignKey("Event.id", ondelete='SET NULL', onupdate='Cascade'))
    @declared_attr
    def event(cls):
        return relationship("Event", foreign_keys=f"{cls.__name__}.event_id", lazy=True)

class CharacterID:
    @declared_attr
    def character_id(cls) -> int:
        return Column(ForeignKey("Character.id", ondelete='Cascade', onupdate='Cascade'), primary_key=True)
    #@declared_attr
    #def character(cls):
    #    return relationship("Character", foreign_keys=f"{cls.__name__}.character_id", lazy=True)
