"""MetaPathFinder implementation for lazy loading modules.

Inspirations:
- https://github.com/facebookincubator/cinder/blob/cinder/3.8/CinderDoc/lazy_imports.rst
- https://snarky.ca/lazy-importing-in-python-3-7/
- https://pypi.org/project/demandimport/
- https://github.com/facebookincubator/cinder (CPython implementation)
"""
from __future__ import annotations

import gc
import sys
import atexit
from types import ModuleType
from importlib.abc import MetaPathFinder
from importlib.machinery import ModuleSpec
from importlib import import_module
from pathlib import Path

from lazi.conf import conf
from lazi.util import classproperty, debug

from .spec import Spec
from .loader import Loader
from .module import Module

__all__ = "Finder", "__finder__"

INVAL_SOFT = conf.INVAL_SOFT
INVAL_GC = conf.INVAL_GC


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
        assert None is debug.traced(3, f"[{id(self)}] INIT {self.__class__.__name__} count:{len(self.__finders__)}")
        self.__finders__.append(self)
        self.specs = {}

    def __del__(self):
        try:
            if self in self.__finders__:
                self.__finders__.remove(self)
                self.invalidate_caches()
        except Exception as e:
            assert None is debug.log(
                f"[{id(self)}] DEL! {self.__class__.__name__} !!!! {type(e).__name__}: {e}"
            )

    def __enter__(self) -> Finder:
        if self not in sys.meta_path:
            assert self.__refs == 0, self.__refs
            assert None is debug.traced(
                2,
                f"[{id(self)}] HOOK {self.__class__.__name__} refs:{self.__refs} "
                f"inst:{len(list(self.meta_path))} sys:{len(sys.meta_path)} "
            )
            sys.meta_path.insert(0, self)
            self.__stack__.append(self)

        self.__refs += 1
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.__refs = max(self.__refs - 1, 0)

        if self.__refs == 0 and self in sys.meta_path:
            pop = self.__stack__.pop()
            assert pop is self, (pop, self)
            sys.meta_path.remove(self)

        assert None is debug.traced(
            2,
            f"[{id(self)}] EXIT {self.__class__.__name__} refs:{self.__refs} "
            f"inst:{len(list(self.meta_path))} sys:{len(sys.meta_path)} "
        )

    def lazy(self, name: str, package: str | None = None) -> ModuleType:
        with self:
            return import_module(name, package)

    def find_spec(self, name: str, path: list[str] | None = None, target: ModuleType | None = None) -> Spec | None:
        assert self in self.__stack__, (self, self.__stack__)

        if self.__busy or self.__stack__[-1] != self:
            return None

        assert None is debug.traced(
            2 if target is None else 1,
            f"[{id(self)}] SPEC FIND {name} [{len(path) if path is not None else '*'}] "
            f"[{id(target) if target is not None else '-'}]"
        )

        if (spec := self.specs.get(name)) is not None:
            assert spec.finder is self, (spec.finder, self)
            if path is not None:
                spec.path = path
            if target is not None:
                spec.target = target
            return spec

        if (spec := self._find_spec(name, path, target)) is not None:

            if not isinstance(spec, self.Spec):
                spec = self.specs[name] = self.Spec(self, spec, path, target)
            else:
                if path is not None:
                    spec.path = path
                if target is not None:
                    spec.target = target

            assert None is debug.traced(
                1 if (target := spec.target) is None else 0,  # NB: Alters state in assert, do not use variable later.
                f"[{id(self)}] FIND {spec.loader_state} {spec.f_name} "
                f"[{Path(c).suffix[1:] if (c:=spec.cached) else Path(o).suffix[1:] if (o:=spec.origin) else '-'}] "
                f"[{id(target) if target is not None else '-'}] {'S' if spec.stdlib else ''}{'B' if spec.builtin else ''} "
            )

            return spec

    def _find_spec(self, name: str, path: list[str] | None, target: ModuleType | None) -> ModuleSpec | None:
        for finder in (_ for _ in sys.meta_path if _ is not self):
            if (spec := finder.find_spec(name, path, target)) is not None:
                return spec

    def invalidate_caches(self) -> None:
        if not INVAL_SOFT:
            while self.specs and (spec := self.specs.popitem()[1]):
                if hasattr(spec.loader, "invalidate_caches"):
                    spec.loader.invalidate_caches(spec)
        else:
            self.specs.clear()

        if INVAL_GC:
            gc.collect()


__finder__: Finder = Finder()

atexit.register(__finder__.invalidate_caches)
