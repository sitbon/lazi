"""Configuration module management... module.

- Add your own configurations by creating modules in the <root>.conf namespace package.
- Any value that is also defined in base.py will be overwritten by the value in the module.
- Configuration values will be accessible from the conf namespace package.
- The import order of the modules determines the resulting configuration.

Use like this (recommended for package mdules):

>>> from lazi.conf import conf
>>> conf.TRACE

Or like this (recommended for client modules):

>>> import lazi.conf.auto
>>> lazi.conf.TRACE
>>> from lazi.conf import auto
>>> auto.TRACE

But not like this:

>>> import lazi.conf        # This is not the same as the above.
>>> from lazi import conf   # Still no worky. Only imports the namespace module without loading.
"""
import sys as _sys

from types import ModuleType, EllipsisType
from typing import Iterator
from pkgutil import ModuleInfo, iter_modules as _iter_modules
from importlib import import_module as _import_module

__all__ = [
    "base", "conf", "__root__", "__conf__", "__core__", "__auto__", "__keys__",
]

if __name__ == "__main__":
    raise RuntimeError(f"Cannot run {__file__} as a script.")


from .base import *  # noqa: Keep IDE linters happy and in the know.

base: ModuleType

__root__: ModuleType        # <meta: root>
__conf__: ModuleType        # <root>.conf
__core__: str               # <root>.<meta: core>
__auto__: str               # <conf>.<meta: auto>
__keys__: set               # <meta: keys>

conf: dict


class Conf(ModuleType):
    __all__ = __all__

    from . import base  # noqa: Relative import from namespace package -- works here.

    __root__: ModuleType = _import_module(base.__meta__["root"])
    __conf__: ModuleType = _import_module(f"{__root__.__name__}.{__name__.rpartition('.')[-1]}")

    __core__: str = f"{__root__.__name__}.{base.__meta__.get('core', 'core')}"
    __auto__: str = f"{__conf__.__name__}.{base.__meta__.get('auto', 'auto')}"

    __keys__: set = {"CONF_KEYS"} | CONF_KEYS | base.__meta__.get("keys", set())

    conf: dict[str, object | EllipsisType] = {key: ... for key in __keys__}

    __mods: dict[str, ModuleType] = base.__meta__.get("mods", {})
    __CONF_NO_CACHING: bool = base.__meta__.get("CONF_NO_CACHING", __core__ in _sys.modules)
    __CONF_NO_CACHING_DFL: bool = __CONF_NO_CACHING

    def __init__(self):
        super().__init__(__name__)
        self.__conf__.__getattr__ = lambda attr: getattr(self, attr)
        if (conf_no_caching := self.CONF_NO_CACHING) is not None:
            self.__CONF_NO_CACHING = conf_no_caching
        self.CONF_NO_CACHING = self.__CONF_NO_CACHING
        self.CONF_KEYS = self.__keys__

    def __iter__(self) -> Iterator[tuple[str, object]]:
        return ((key, getattr(self, key)) for key in self.conf)

    def get(self) -> dict:
        return dict(self)

    def clear(self):
        for key, value in self.conf.items():
            if value is not ...:
                delattr(self, key)
                self.conf[key] = ...

            if self.__auto__ in _sys.modules and hasattr(_sys.modules[self.__auto__], key):
                delattr(_sys.modules[self.__auto__], key)

        self.__CONF_NO_CACHING = self.__CONF_NO_CACHING_DFL

    def __mods__(self) -> Iterator[ModuleInfo]:
        return (
            mi for mi in _iter_modules(self.__conf__.__path__, self.__conf__.__name__ + ".")
            if mi.name not in {self.__root__.__name__, self.base.__name__, self.__auto__, self.__name__}
        )

    def __getattr__(self, attr) -> object:

        if (value := self.conf.get(attr, miss := AttributeError())) is miss:
            raise AttributeError(f"Module {__name__!r} has no attribute {attr!r}")

        elif value is ...:
            value = getattr(self.base, attr)

            for mi in self.__mods__():
                if (mod := self.__mods.get(mi.name, miss)) is miss:
                    mod = _import_module(mi.name)
                    if not self.__CONF_NO_CACHING:
                        self.__mods[mi.name] = mod

                value = getattr(mod, attr, value)

            value = self.__setattr__(attr, value)

        return value

    def __setattr__(self, key, value) -> object:
        if key.startswith("_"):
            super().__setattr__(key, value)
            return value

        if key not in self.conf and key != "CONF_KEYS" and key not in self.CONF_KEYS:
            raise AttributeError(f"Conf key {key!r} is not defined.")
        if not self.__CONF_NO_CACHING:

            if key == "CONF_KEYS" and value is not self.__keys__:
                self.__all__ = list(set(self.__all__) | set(value))
                for conf_key in (_ for _ in dict(self.conf) if _ != "CONF_KEYS" and _ not in value):
                    del self.conf[conf_key]
                for conf_key in (_ for _ in value if _ != "CONF_KEYS" and _ not in self.conf):
                    self.conf[conf_key] = ...
                self.conf["CONF_KEYS"] = value

            self.conf[key] = value
            super().__setattr__(key, value)

        return value


_sys.modules[__name__] = Conf()  # Replace module with instance.

__all__.extend(_sys.modules[__name__].__keys__)

del ModuleType, EllipsisType, Iterator, ModuleInfo
