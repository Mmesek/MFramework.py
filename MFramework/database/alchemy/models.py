from __future__ import annotations

from typing import List

from mlib.database import Base
from sqlalchemy import BigInteger, Column, ForeignKey, String
from sqlalchemy.orm import relationship

from .mixins import ChannelID, ServerID, Snowflake
from .table_mixins import HasDictSettingsRelated


class Server(HasDictSettingsRelated, Snowflake, Base):
    """Servers table representing server in Database"""

    channels: List[Channel] = relationship("Channel", back_populates="server")
    roles: List[Role] = relationship("Role", back_populates="server")
    # snippets: List[Snippet] = relationship("Snippet")
    # statistics: List[log.Statistic] = relationship("Statistic", lazy="dynamic") #this returns a query or something like that
    # tasks: List[Task] = relationship("Task")
    webhooks: List[Webhook] = relationship("Webhook")


class Role(HasDictSettingsRelated, ServerID, Snowflake, Base):
    """Roles table representing role in Database"""

    server: Server = relationship("Server", back_populates="roles")


class Channel(HasDictSettingsRelated, ServerID, Snowflake, Base):
    """Channels table representing channel in Database"""

    server: Server = relationship("Server", back_populates="channels")
    webhooks: List[Webhook] = relationship("Webhook", back_populates="channel")


###--------------------------------------------------------------------###


class Webhook(ChannelID, ServerID, Snowflake, Base):
    """Webhooks related to Channel"""

    token: str = Column(String)
    subscriptions: List[Subscription] = relationship("Subscription", back_populates="webhook")


class Subscription(Base):
    """Subscriptions related to Webhooks"""

    webhook_id: Snowflake = Column(
        BigInteger,
        ForeignKey("Webhook.id", ondelete="Cascade", onupdate="Cascade"),
        primary_key=True,
    )
    webhook: List[Webhook] = relationship("Webhook")
    thread_id: Snowflake = Column(BigInteger, nullable=True)
    source: str = Column(String, primary_key=True)
    content: str = Column(String)
    regex: str = Column(String, primary_key=True)


# class RoleSetting(ChannelID, RoleID, UserID, ServerID, Base):
#    server_id = Column(BigInteger, ForeignKey("Server.id", ondelete='Cascade', onupdate='Cascade'))
#    role_id = Column(BigInteger)#, ForeignKey("Role.id", ondelete='Cascade', onupdate='Cascade'))
#    type = Column(Enum(types.Setting)) # Reaction, level, presence, custom or special
#    message_id = Column(BigInteger)
#    name = Column(String) # Reaction or name
#    group = Column(String) # For reactions or levels
#    required = Column(Integer) # EXP
