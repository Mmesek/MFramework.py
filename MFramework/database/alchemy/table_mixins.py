from typing import Any
import datetime

from sqlalchemy import Column, Integer, Enum, Date, String, Boolean, Column, ForeignKey, BigInteger, Float
from sqlalchemy.orm import declared_attr, relationship
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.ext.associationproxy import association_proxy

from mlib.database import Base

from .mixins import Snowflake
from . import types

class ProxiedDictMixin(object):
    """Adds obj[key] access to a mapped class.

    This class basically proxies dictionary access to an attribute
    called ``_proxied``.  The class which inherits this class
    should have an attribute called ``_proxied`` which points to a dictionary.

    """

    def __len__(self):
        return len(self._proxied)

    def __iter__(self):
        return iter(self._proxied)

    def __getitem__(self, key):
        return self._proxied[key]

    def __contains__(self, key):
        return key in self._proxied

    def __setitem__(self, key, value):
        self._proxied[key] = value

    def __delitem__(self, key):
        del self._proxied[key]


class Setting:
    '''Polymorphic Setting mixin
    
    Columns
    -------
    name:
        `Setting` type of this setting
    '''
    name: types.Setting = Column(Enum(types.Setting), primary_key=True)
    int: int = Column(Integer, nullable=True)#default=0)
    str: str = Column(String, nullable=True)
    bool: bool = Column(Boolean, nullable=True)
    snowflake: Snowflake = Column(BigInteger, nullable=True)
    date: datetime.date = Column(Date, nullable=True)
    float: float = Column(Float, nullable=True)

class HasDictSettingsRelated:#(ProxiedDictMixin):
    @declared_attr
    def settings(cls):
        cls.Setting = type(f"Setting_{cls.__tablename__}",
            (Setting, Base),
            dict(
                __tablename__=f"Setting_{cls.__tablename__}",
                id=Column(ForeignKey(f"{cls.__tablename__}.id", ondelete="cascade", onupdate='Cascade'), primary_key=True),
                #parent=relationship(cls)
                __table_args__ = {"extend_existing":True}
            )
        )
        return relationship(cls.Setting, collection_class=attribute_mapped_collection("name"), cascade='all, delete-orphan')
    @declared_attr
    def _settings(cls): #_proxied
        return association_proxy(
            "settings",
            "value",
            creator=lambda name, value: cls.Setting(name=name, value=value),
        )
    @classmethod
    def with_setting(self, name, value):
        return self.settings.any(name=name, **{type(value).__name__.lower():value})
    def add_setting(self, setting: types.Setting, value: Any) -> None:
        setting_type = setting.annotation.__name__
        import enum
        if type(value) in {int, str, bool} and type(value).__name__ != setting_type:
            column = type(value).__name__
        elif type(value).__name__ == setting_type: 
            column = setting_type
        elif isinstance(value, enum.Enum):
            column = setting_type
        else:
            print("[VALUE - SETTING_TYPE MISMATCH]", value, setting)
        self.settings[setting] = self.Setting(**{"name": setting, column.lower():value})
    def modify_setting(self, setting: types.Setting, value: Any) -> None:
        setattr(self.settings[setting], setting.value.__name__, value)
    def remove_setting(self, setting: types.Setting) -> Any:
        return getattr(self.settings.pop(setting, None), setting.annotation.__name__.lower(), None)
    def get_setting(self, setting: types.Setting) -> Any:
        return getattr(self.settings.get(setting, None), setting.annotation.__name__.lower(), None)

