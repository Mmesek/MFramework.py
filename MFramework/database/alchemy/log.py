from sqlalchemy import Enum, Boolean, UnicodeText
from sqlalchemy.orm import relationship

from .mixins import *
from . import types

class TransactionInventory(ItemID, UserID, Base):
    user_id = Column(ForeignKey("User.id", ondelete='SET NULL', onupdate='Cascade'), nullable=True)
    id = Column(ForeignKey("Transaction.id", ondelete="Cascade", onupdate='Cascade'), primary_key=True)
    quantity = Column(Integer, default=0)
    incoming = Column(Boolean, default=False, nullable=False)

class Transaction(Timestamp, ServerID, ID, Base):
    server_id = Column(ForeignKey("Server.id", ondelete='SET NULL', onupdate='Cascade'), nullable=True)
    items = relationship(TransactionInventory)
    def add(self, to_user_id, item):
        self.items.append(TransactionInventory(user_id=to_user_id, item_id=item.item_id, quantity=item.quantity, incoming=True))
    def remove(self, from_user_id, item):
        self.items.append(TransactionInventory(user_id=from_user_id, item_id=item.item_id, quantity=item.quantity, incoming=False))

class Activity(Timestamp, UserID, ServerID, Base):
    '''Append-only table'''
    server_id = Column(ForeignKey("Server.id", ondelete='Cascade', onupdate='Cascade'), primary_key=True, nullable=False)
    user_id = Column(ForeignKey("User.id", ondelete='Cascade', onupdate='Cascade'), primary_key=True, nullable=False)
    name = Column(Enum(types.Statistic), primary_key=True)
    value = Column(Integer, default=0)

class Infraction(Timestamp, UserID, ServerID, ID, Base):
    user_id = Column(ForeignKey("User.id", ondelete='SET DEFAULT', onupdate='Cascade'), nullable=False, default=0)
    user = relationship("User", foreign_keys="Infraction.user_id")
    moderator_id = Column(ForeignKey("User.id", ondelete='SET DEFAULT', onupdate='Cascade'), nullable=True, default=0)
    moderator = relationship("User", foreign_keys="Infraction.moderator_id")

    type = Column(Enum(types.Infraction))
    reason = Column(UnicodeText, nullable=True)
    duration = Column(Interval, nullable=True)

    channel_id = Column(BigInteger, nullable=True)
    message_id = Column(BigInteger, nullable=True)
    active = Column(Boolean, default=True, nullable=True)

class Log(Timestamp, UserID, ServerID, ID, Base):
    user_id = Column(ForeignKey("User.id", ondelete='Cascade', onupdate='Cascade'), nullable=True)
    type = Column(String)
    value = Column(UnicodeText)

class Statistic(TimestampUpdate, ServerID, UserID, Base):
    '''Updateable table'''
    server_id = Column(ForeignKey("Server.id", ondelete='Cascade', onupdate='Cascade'), primary_key=True, nullable=False, default=0)
    user_id = Column(ForeignKey("User.id", ondelete='Cascade', onupdate='Cascade'), primary_key=True, nullable=False, default=0)

    name = Column(Enum(types.Statistic), primary_key=True)
    value = Column(Integer, default=0)
    @classmethod
    def get(cls, s, server_id, user_id, name):
        r = cls.filter(s, server_id = server_id, user_id=user_id, name=name).first()
        if not r:
            r = cls(server_id = server_id, user_id=user_id, name = name, value=0)
            s.add(r)
        return r
    @classmethod
    def increment(cls, s, server_id, user_id, name):
        _s = cls.get(s, server_id, user_id, name)
        _s.value += 1
        s.commit()
    @classmethod
    def decrement(cls, s, server_id, user_id, name):
        _s = cls.get(s, server_id, user_id, name)
        _s.value -= 1
        s.commit()

class Presence(TimestampUpdate, ServerID, UserID, Snowflake, Base):
    type = Column(Enum(types.Statistic))
    name = Column(String, primary_key=True)
    server_id = Column(ForeignKey("Server.id", onupdate='Cascade', ondelete='Cascade'), primary_key=True)
    user_id = Column(ForeignKey("User.id", onupdate='Cascade', ondelete='Cascade'), primary_key=True)
    duration = Column(Interval)