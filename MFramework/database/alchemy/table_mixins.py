from sqlalchemy.sql.sqltypes import Boolean
from .mixins import *
from . import types

from sqlalchemy import Column, Integer, Enum, Date, String

from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.ext.associationproxy import association_proxy

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
    name = Column(Enum(types.Setting), primary_key=True)
    int = Column(Integer, nullable=True)#default=0)
    str = Column(String, nullable=True)
    bool = Column(Boolean, nullable=True)
    snowflake = Column(BigInteger, nullable=True)
    date = Column(Date, nullable=True)

class HasDictSettingsRelated:#(ProxiedDictMixin):
    @declared_attr
    def settings(cls):
        cls.Setting = type(f"Setting_{cls.__tablename__}",
            (Setting, Base),
            dict(
                __tablename__=f"Setting_{cls.__tablename__}",
                id=Column(ForeignKey(f"{cls.__tablename__}.id", ondelete="cascade", onupdate='Cascade'), primary_key=True),
                #parent=relationship(cls)
            )
        )
        return relationship(cls.Setting, collection_class=attribute_mapped_collection("name"))
    @declared_attr
    def _settings(cls): #_proxied
        return association_proxy(
            "settings",
            "value",
            creator=lambda name, value: cls.Setting(name=name, value=value),
        )
    @classmethod
    def with_setting(self, name, value):
        return self.settings.any(name=name, value=value)
    def add_setting(self, setting, value):
        setting_type = setting.value[0].__name__
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
    def modify_setting(self, setting, value):
        setattr(self.settings[setting], setting.value.__name__, value)
    def remove_setting(self, setting):
        self.settings[setting] = None
