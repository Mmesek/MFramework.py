from datetime import timedelta
from typing import Annotated

from sqlalchemy import BigInteger, ForeignKey, orm
from sqlalchemy.orm import declared_attr
from sqlalchemy.orm import mapped_column as Column
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import Interval

int_pk = Annotated[int, Column(BigInteger, primary_key=True, autoincrement=False, nullable=False)]


class Snowflake(orm.MappedAsDataclass):
    id: orm.Mapped[int_pk]


class Cooldown(orm.MappedAsDataclass):
    cooldown: orm.Mapped[timedelta] = Column(Interval)


class ForeignMixin:
    _table: str = None


class TypeID(orm.MappedAsDataclass):
    type_id: orm.Mapped[int] = Column(ForeignKey("Type.id", nullable=True))


class ServerID(orm.MappedAsDataclass):
    server_id: orm.Mapped[int] = Column(
        BigInteger, ForeignKey("Server.id", ondelete="Cascade", onupdate="Cascade"), primary_key=False, nullable=False
    )

    @declared_attr
    def server(cls):
        return relationship("Server", foreign_keys=f"{cls.__name__}.server_id", lazy=True)


class RoleID(orm.MappedAsDataclass):
    role_id: orm.Mapped[int] = Column(BigInteger, ForeignKey("Role.id", ondelete="Cascade", onupdate="Cascade"))

    @declared_attr
    def role(cls):
        return relationship("Role", foreign_keys=f"{cls.__name__}.role_id", lazy=True)


class ChannelID(orm.MappedAsDataclass):
    channel_id: orm.Mapped[int] = Column(BigInteger, ForeignKey("Channel.id", ondelete="Cascade", onupdate="Cascade"))

    @declared_attr
    def channel(cls):
        return relationship("Channel", foreign_keys=f"{cls.__name__}.channel_id", lazy=True)
