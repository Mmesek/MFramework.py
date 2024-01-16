from datetime import timedelta

from sqlalchemy import BigInteger, Column, ForeignKey
from sqlalchemy.orm import declared_attr, relationship
from sqlalchemy.sql.sqltypes import Interval

from typing import Annotated
from sqlalchemy import orm


int_pk = Annotated[int, orm.mapped_column(BigInteger, primary_key=True, autoincrement=False, nullable=False)]


class Snowflake:
    # id: int  # = Column(BigInteger, primary_key=True, autoincrement=False, nullable=False)
    id: orm.Mapped[int_pk]


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
        return Column(
            ForeignKey("Server.id", ondelete="Cascade", onupdate="Cascade"),
            primary_key=False,
            nullable=False,
        )

    # @declared_attr
    # def server(cls):
    #    return relationship("Server", foreign_keys=f"{cls.__name__}.server_id", lazy=True)


class RoleID:
    @declared_attr
    def role_id(cls) -> int:
        return Column(ForeignKey("Role.id", ondelete="Cascade", onupdate="Cascade"))

    @declared_attr
    def role(cls):
        return relationship("Role", foreign_keys=f"{cls.__name__}.role_id", lazy=True)


class ChannelID:
    @declared_attr
    def channel_id(cls) -> int:
        return Column(ForeignKey("Channel.id", ondelete="Cascade", onupdate="Cascade"))

    @declared_attr
    def channel(cls):
        return relationship("Channel", foreign_keys=f"{cls.__name__}.channel_id", lazy=True)
