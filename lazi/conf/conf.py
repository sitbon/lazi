import sys

from types import ModuleType, EllipsisType
from typing import Iterator
from pkgutil import ModuleInfo, iter_modules
from importlib import import_module

from lazi.util import SingletonMeta

from lazi.conf.base import *  # noqa: Keep IDE linters happy and in the know (mostly).


class Conf(ModuleType, metaclass=SingletonMeta):
    import lazi.conf as __ns__
    import lazi.conf.base as base

    conf: dict[str, object | EllipsisType] = {
        key: ... for key in {key for key in base.__dict__ if not key.startswith("_") and key.isupper()}
    }

    __mods: dict[str, ModuleType] = {}
    __auto: str = f"{__ns__.__name__}.auto"
    __CONF_DISABLE_CACHING: bool = False

    def __init__(self):
        super().__init__(__name__)
        self.__ns__.__getattr__ = lambda attr: getattr(self, attr)
        self.__CONF_DISABLE_CACHING = bool(self.__getattr__("CONF_DISABLE_CACHING"))

    def __call__(self):
        return self

    def __iter__(self) -> Iterator[tuple[str, object]]:
        return ((key, getattr(self, key)) for key in self.conf)

    def get(self) -> dict:
        return dict(self)

    def clear(self):
        for key, value in self.conf.items():
            if value is not ...:
                delattr(self, key)
                self.conf[key] = ...

            if self.__auto in sys.modules and hasattr(sys.modules[self.__auto], key):
                delattr(sys.modules[self.__auto], key)

        self.__CONF_DISABLE_CACHING = False

    def __mods_iter__(self) -> Iterator[ModuleInfo]:
        return (
            mi for mi in iter_modules(self.__ns__.__path__, self.__ns__.__name__ + ".")
            if mi.name not in (self.__auto, self.base.__name__, __name__)
        )

    def __getattr__(self, attr, *, init: bool = False) -> object:

        if (value := self.conf.get(attr, miss := AttributeError())) is miss:
            raise AttributeError(f"Module {__name__!r} has no attribute {attr!r}")

        elif value is ...:
            value = base_value = self.base.__dict__[attr]

            for mi in self.__mods_iter__():
                if (mod := self.__mods.get(mi.name, miss)) is miss:
                    mod = self.__mods[mi.name] = import_module(mi.name)

                value = getattr(mod, attr, base_value)

        assert value is not miss and value is not ...
        value = self.conf[attr] = self.__update(attr, value)
        return value

    def __update(self, key: str, value: object) -> object:
        if not self.__CONF_DISABLE_CACHING:
            setattr(self, key, value)
        return value


sys.modules[__name__] = Conf()
