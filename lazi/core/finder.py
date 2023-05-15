from __future__ import annotations

import sys
from types import ModuleType
from dataclasses import dataclass
from importlib.util import find_spec, module_from_spec
from importlib.abc import MetaPathFinder

from lazi.conf import conf
from lazi.util import classproperty, debug

from .spec import Spec
from .loader import Loader
from .module import Module

__all__ = "Finder", "__finder__"


class Finder(MetaPathFinder):
    Spec: type[Spec] = Spec
    Loader: type[Loader] = Loader
    Module: type[Module] = Module

    __refs__: int = 0
    __specs__: dict[str, Spec]

    __stack__: list[Finder] = []

    finders = classproperty(lambda cls: (_ for _ in sys.meta_path if isinstance(_, cls)))

    def __init__(self):
        self.__specs__ = {}

    def __enter__(self) -> Finder:
        if self not in sys.meta_path:
            assert self.__refs__ == 0, self.__refs__
            if __debug__ and conf.DEBUG_TRACING > 1:
                assert None is debug.trace(
                    f"+ {self.__class__.__name__}[{id(self)}] "
                    f"<{len([_ for _ in sys.meta_path if isinstance(_, type(self))])}>"
                )

            self.__refs__ += 1
            sys.meta_path.insert(0, self)

        return self

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        if __debug__ and conf.DEBUG_TRACING > 1 and self.__refs__ == 1:
            assert None is debug.trace(f"- {self.__class__.__name__}[{id(self)}]")

        self.__refs__ = max(self.__refs__ - 1, 0)

        if self.__refs__ == 0 and self in sys.meta_path:
            sys.meta_path.remove(self)
            self.invalidate_caches()
            return True

        return False

    @classmethod
    def install(cls) -> Finder:
        return __finder__.__enter__()

    @classmethod
    def uninstall(cls) -> bool:
        return __finder__.__exit__(None, None, None)

    def lazy(self, name: str, path: list[str] | None = None, target: ModuleType | None = None) -> ModuleType:
        if (spec := self.find_spec(name, path, target)) is not None:
            module = module_from_spec(spec)
            spec.loader.exec_module(module)
            return module

    def find_spec(self, name: str, path: list[str] | None = None, target: ModuleType | None = None) -> Spec | None:
        if self in self.__stack__:
            return None

        if conf.DEBUG_TRACING > 1:
            assert None is debug.trace(f"<find> {name} <p:{len(path) if path else path!r}> <t:{target!r}>")

        if (spec := self.__specs__.get(name)) is not None:
            assert spec.finder is self, (spec.finder, self)
            return spec

        self.__stack__.append(self)

        try:
            if (spec := find_spec(name, path)) is not None:
                spec = self.__specs__[name] = self.Spec(self, spec, path, target)
                if conf.DEBUG_TRACING > 1:
                    assert None is debug.trace(f"<foun> {spec.name} <L:{spec.loader_state}>")
                return spec

        finally:
            pop = self.__stack__.pop()
            assert pop is self, (pop, self)

    def invalidate_caches(self) -> None:
        while self.__specs__ and (spec := self.__specs__.popitem()[1]):
            if spec.loader_state == spec.loader.State.LOAD:
                spec.loader.unload_module(spec)


__finder__: Finder = Finder()
