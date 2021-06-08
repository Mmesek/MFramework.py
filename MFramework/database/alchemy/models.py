from __future__ import annotations
from datetime import timedelta
from sqlalchemy.orm import relationship
from .mixins import *
from .table_mixins import *
from typing import List
from .items import Inventory
from .log import Infraction, Transaction

class User(HasDictSettingsRelated, Snowflake, Base):
    infractions = relationship("Infraction", back_populates="user", foreign_keys="Infraction.user_id", order_by="desc(Infraction.timestamp)")
    mod_actions = relationship("Infraction", back_populates="moderator", foreign_keys="Infraction.moderator_id", order_by="desc(Infraction.timestamp)")
    transactions = relationship("TransactionInventory", order_by="desc(Transaction.timestamp)")
    activities = relationship("Activity", order_by="desc(Activity.timestamp)")
    statistics = relationship("Statistic")

    items = relationship('Inventory')
    def __init__(self, id) -> None:
        self.id = id
    def add_item(self, Inventory: Inventory, transaction: Transaction = None):
        if transaction:
            transaction.add(self.id, Inventory)
        for item in self.items:
            if Inventory.item.name == item.item.name:
                item.quantity += Inventory.quantity
                return
        self.items.append(Inventory)
    
    def add_items(self, *items: List[Inventory]):
        for i in items:
            self.add_item(i)
    
    def remove_item(self, Inventory: Inventory, transaction: Transaction = None):
        if transaction:
            transaction.remove(self.id, Inventory)
        for item in self.items:
            if Inventory.item.name == item.item.name:
                item.quantity -= Inventory.quantity
                if item.quantity == 0:
                    self.items.remove(item) # No idea if it'll work
                    #pass # TODO: Remove from mapping/association or something
                return
    
    def remove_items(self, *Items: List[Inventory]):
        for i in Items:
            self.remove_item(i)
    
    def add_infraction(self, server_id: int, moderator_id: int, type: types.Infraction, reason: str=None, duration: timedelta=None, channel_id: int=None, message_id: int=None) -> List[Infraction]:
        '''
        Add infraction to current user. Returns total user infractions on server
        '''
        self.infractions.append(Infraction(server_id = server_id, moderator_id = moderator_id, type=type, reason=reason, duration=duration, channel_id=channel_id, message_id=message_id))
        return [i for i in self.infractions if i.server_id == server_id]
    
    def transfer(self, server_id: int, recipent: User, sent: List[Inventory] = None, recv: List[Inventory] = None, remove_item:bool=True, turn_item:bool=False) -> Transaction:
        '''
        Transfers item from current user to another user & returns transaction log (Which needs to be added to session manually[!])

        Params
        ------
        server_id:
            ID of Server on which transfer is happening
        recipent:
            User object (DB one) which receives the items
        sent:
            Inventory object containing item that should be removed from current user and added to remote user
        recv:
            Inventory object containing item that should be added to current user and removed from remote user
        remove_item: 
            Whether it should remove item from another user 
            (Sent removed from current user and/or Received removed from another user, useful for exchanges)
        turn_item:
            Whether it should remove received item from current user 
            (Useful when turning item from one to another on same user)
        '''
        transaction = Transaction(server_id = server_id)
        if sent: #TODO: Multiple different items/inventories for sent/recv 
            recipent.add_items(sent, transaction)
            if remove_item and not turn_item:
                self.remove_items(sent, transaction)
        if recv:
            if not turn_item:
                self.add_items(recv, transaction)
            else:
                self.remove_items(recv, transaction)
            if remove_item and not turn_item:
                recipent.remove_items(recv, transaction)
        return transaction
    def claim_items(self, server_id: int, items: List[Inventory]) -> Transaction:
        return self.transfer(server_id, None, recv=items, remove_item=False)
    def gift_items(self, server_id: int, recipent: User, items: List[Inventory]) -> Transaction:
        return self.transfer(server_id, recipent, items)
    def turn_race(self, server_id: int, recipent: User, from_race: types.HalloweenRaces, into_race: types.HalloweenRaces) -> Transaction:
        return self.transfer(server_id, recipent, [from_race], [into_race], False, True) # That is definitly not what was planned #FIXME

class Server(HasDictSettingsRelated, Snowflake, Base):
    channels = relationship("Channel", back_populates="server")
    roles = relationship("Role", back_populates="server")
    snippets = relationship("Snippet")
    statistics = relationship("Statistic", lazy="dynamic") #this returns a query or something like that
    tasks = relationship("Task")
    webhooks = relationship("Webhook")

class Role(HasDictSettingsRelated, ServerID, Snowflake, Base):
    server = relationship("Server", back_populates="roles")

class Channel(HasDictSettingsRelated, ServerID, Snowflake, Base):
    server = relationship("Server", back_populates="channels")
    webhooks = relationship("Webhook", back_populates="channel")


'''
###--------------------------------------------------------------------###
'''

from . import types
from sqlalchemy import Column, Integer, Enum, Boolean, UnicodeText, TIMESTAMP

class Webhook(ChannelID, ServerID, Snowflake, Base):
    token = Column(String)
    subscriptions = relationship("Subscription", back_populates="webhook")

from MFramework.commands._utils import Groups
class Snippet(Timestamp, File, RoleID, UserID, ServerID, Base):
    role_id = Column(ForeignKey("Role.id", ondelete='SET NULL', onupdate='Cascade'))
    group = Column(Enum(Groups))
    type = Column(Enum(types.Snippet))
    name = Column(String)
    trigger = Column(String)
    content = Column(UnicodeText)
    cooldown = Column(Interval)
    locale = Column(String)

class Task(Timestamp, ServerID, ChannelID, UserID, Base):
    user_id = Column(ForeignKey("User.id", ondelete='Cascade', onupdate='Cascade'), primary_key=True, nullable=False)
    message_id = Column(BigInteger, primary_key=True, autoincrement=False)

    finished = Column(Boolean, default=False)
    type = Column(Enum(types.Task))
    end = Column(TIMESTAMP(True))

    title = Column(String)
    description = Column(UnicodeText)
    count = Column(Integer)

class Subscription(Base):
    webhook_id = Column(BigInteger, ForeignKey("Webhook.id", ondelete='Cascade', onupdate='Cascade'), primary_key=True)
    webhook = relationship("Webhook")
    source = Column(String, primary_key=True)
    content = Column(String)
    regex = Column(String, primary_key=True)

class RSS(Base):
    source = Column(String, primary_key=True)
    last = Column(Integer)
    url = Column(String)
    color = Column(Integer)
    language = Column(String)
    avatar_url = Column(String)
    refresh_rate = Column(Interval)

class Spotify(Base):
    id = Column(String, primary_key=True)
    artist = Column(String)
    added_by = Column(ForeignKey("User.id", ondelete='SET NULL', onupdate='Cascade'))

#class RoleSetting(ChannelID, RoleID, UserID, ServerID, Base):
#    server_id = Column(BigInteger, ForeignKey("Server.id", ondelete='Cascade', onupdate='Cascade'))
#    role_id = Column(BigInteger)#, ForeignKey("Role.id", ondelete='Cascade', onupdate='Cascade'))
#    type = Column(Enum(types.Setting)) # Reaction, level, presence, custom or special
#    message_id = Column(BigInteger)
#    name = Column(String) # Reaction or name
#    group = Column(String) # For reactions or levels
#    required = Column(Integer) # EXP
