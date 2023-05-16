from __future__ import annotations

import gc
import sys
from types import ModuleType
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

    __finders__: list[Finder] = []
    __stack__: list[Finder] = []

    specs: dict[str, Spec]
    __busy: bool = False
    __refs: int = 0; refs = property(lambda self: self.__refs)  # noqa

    meta_path = classproperty(lambda cls: (_ for _ in sys.meta_path if isinstance(_, cls)))

    def __init__(self):
        self.__finders__.append(self)
        self.specs = {}

    def __del__(self):
        self.__finders__.remove(self)

    def __enter__(self) -> Finder:
        if self not in sys.meta_path:
            assert self.__refs == 0, self.__refs
            assert None is debug.trace(
                f"[{id(self)}] +{self.__class__.__name__} refs:{self.__refs} "
                f"inst:{len(list(self.meta_path))} sys:{len(sys.meta_path)} "
            )
            sys.meta_path.insert(0, self)
            self.__stack__.append(self)

        self.__refs += 1
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        assert None is debug.trace(
            f"[{id(self)}] -{self.__class__.__name__} refs:{self.__refs} "
            f"inst:{len(list(self.meta_path))} sys:{len(sys.meta_path)} "
        )

        self.__refs = max(self.__refs - 1, 0)

        if self.__refs == 0 and self in sys.meta_path:
            pop = self.__stack__.pop()
            assert pop is self, (pop, self)
            sys.meta_path.remove(self)
            self.invalidate_caches()
            return True
        return False

    def lazy(self, name: str, path: list[str] | None = None, target: ModuleType | None = None) -> ModuleType:
        pop = False

        if self not in self.__stack__:
            self.__stack__.append(self)
            pop = True

        try:
            if (spec := self.find_spec(name, path, target)) is not None:
                module = module_from_spec(spec)
                spec.loader.exec_module(module)
                return module

        finally:
            if pop:
                pop = self.__stack__.pop()
                assert pop is self, (pop, self)

    def find_spec(self, name: str, path: list[str] | None = None, target: ModuleType | None = None) -> Spec | None:
        assert self in self.__stack__, (self, self.__stack__)

        if self.__busy or self.__stack__[-1] != self:
            return None

        assert None is debug.traced(
            1,
            f"[{id(self)}] <find> {name} p:{len(path) if path else path!r} t:{target!r} "
            f"stack:{len(self.__stack__)}"
        )

        if (spec := self.specs.get(name)) is not None:
            assert spec.finder is self, (spec.finder, self)
            return spec

        self.__busy = True
        try:
            if (spec := find_spec(name, path)) is not None:
                spec = self.specs[name] = self.Spec(self, spec, path, target)
                assert None is debug.traced(2, f"[{id(self)}] <foun> {spec.name} L:{spec.loader_state} o:{spec.origin}")
                if conf.FORCE_LOAD_MODULE and (module := sys.modules.get(spec.name)):
                    spec.loader.exec_module(module, spec, True)
                return spec
        finally:
            self.__busy = False

    def invalidate_caches(self) -> None:
        if not conf.SOFT_INVALIDATION:
            while self.specs and (spec := self.specs.popitem()[1]):
                if hasattr(spec.loader, "unload_module"):
                    spec.loader.unload_module(spec)
        else:
            self.specs.clear()

        if conf.GARBAG_COLLECTION:
            gc.collect()


__finder__: Finder = Finder()
