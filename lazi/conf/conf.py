"""Configuration module management... module.

- Add your own configurations by creating modules in the <root>.conf namespace package.
- Any value that is also defined in base.py will be overwritten by the value in the module.
- Configuration values will be accessible from the conf namespace package.
- The import order of the modules determines the resulting configuration.

Use like this (recommended for package mdules):

>>> from lazi.conf import conf
>>> conf.LOADER_AUTO_DEPS

Or like this (recommended for client modules):

>>> import lazi.conf.auto
>>> lazi.conf.LOADER_AUTO_DEPS
>>> from lazi.conf import auto
>>> auto.LOADER_AUTO_DEPS

But not like this:

>>> import lazi.conf        # This is not the same as the above.
>>> import lazi.conf.conf   # This works but is not recommended because lazi.conf.conf becomes inaccessible.
>>> from lazi import conf   # Still no worky. Only imports the namespace module without loading.
"""
import sys

from types import ModuleType, EllipsisType
from typing import Iterator
from pkgutil import ModuleInfo, iter_modules
from importlib import import_module

from lazi.util import SingletonMeta

from .base import *  # noqa: Keep IDE linters happy and in the know.


if __name__ == "__main__":
    raise RuntimeError(f"Cannot run {__file__} as a script.")


class Conf(ModuleType, metaclass=SingletonMeta):
    from . import base  # noqa: Relative import from namespace package -- works here.

    __root__: str = base.__meta__["root"]
    __conf__: str = __name__.rpartition(".")[-1]
    __core__: str = f"{__root__}.{base.__meta__.get('core', 'core')}"

    __namespace__ = import_module(f"{__root__}.{__conf__}")
    __auto__: str = f"{__namespace__.__name__}.{base.__meta__.get('auto', 'auto')}"

    __mods: dict[str, ModuleType] = base.__meta__.get("mods", {})
    __CONF_NO_CACHING: bool = base.__meta__.get("CONF_NO_CACHING", __core__ in sys.modules)
    __CONF_NO_CACHING_DFL: bool = __CONF_NO_CACHING

    conf: dict[str, object | EllipsisType] = {
        key: ... for key in {key for key in base.__dict__ if not key.startswith("_") and key.isupper()}
    }

    def __init__(self):
        super().__init__(__name__)
        self.__namespace__.__getattr__ = self.__getattr__
        if (conf_no_caching := self.CONF_NO_CACHING) is not None:
            self.__CONF_NO_CACHING = conf_no_caching
        else:
            self.CONF_NO_CACHING = self.__CONF_NO_CACHING

    def __iter__(self) -> Iterator[tuple[str, object]]:
        return ((key, getattr(self, key)) for key in self.conf)

    def get(self) -> dict:
        return dict(self)

    def clear(self):
        for key, value in self.conf.items():
            if value is not ...:
                delattr(self, key)
                self.conf[key] = ...

            if self.__auto__ in sys.modules and hasattr(sys.modules[self.__auto__], key):
                delattr(sys.modules[self.__auto__], key)

        self.__CONF_NO_CACHING = self.__CONF_NO_CACHING_DFL

    def __mods__(self) -> Iterator[ModuleInfo]:
        return (
            mi for mi in iter_modules(self.__namespace__.__path__, self.__namespace__.__name__ + ".")
            if mi.name not in (self.__auto__, self.base.__name__, __name__)
        )

    def __getattr__(self, attr) -> object:

        if (value := self.conf.get(attr, miss := AttributeError())) is miss:
            raise AttributeError(f"Module {__name__!r} has no attribute {attr!r}")

        elif value is ...:
            value = base_value = self.base.__dict__[attr]

            for mi in self.__mods__():
                if (mod := self.__mods.get(mi.name, miss)) is miss:
                    mod = self.__mods[mi.name] = import_module(mi.name)

                value = getattr(mod, attr, base_value)

            self.conf[attr] = value

        assert value is not miss and value is not ...
        return self.__update(attr, value)

    def __update(self, key: str, value: object) -> object:
        if not self.__CONF_NO_CACHING:
            setattr(self, key, value)
        return value


sys.modules[__name__] = Conf()
