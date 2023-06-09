"""MetaPathFinder implementation for lazy loading modules.

Inspirations:
- https://github.com/facebookincubator/cinder/blob/cinder/3.8/CinderDoc/lazy_imports.rst
- https://snarky.ca/lazy-importing-in-python-3-7/
- https://pypi.org/project/demandimport/
- https://github.com/facebookincubator/cinder (CPython implementation)
"""
from __future__ import annotations

import sys
import atexit
from types import ModuleType
from importlib.abc import MetaPathFinder
from importlib.machinery import ModuleSpec
from importlib import import_module
import re

from lazi.conf import conf
from lazi.util import classproperty, debug, oid

from .spec import Spec
from .loader import Loader
from .module import Module

__all__ = "Finder", "__finder__"


class Finder(MetaPathFinder):
    Spec: type[Spec] = Spec
    Loader: type[Loader] = Loader
    Module: type[Module] = Module

    NO_LAZY: Spec.Level = Spec.Level(conf.NO_LAZY)
    LAZY: dict[str, int | str] = conf.LAZY
    CONTEXT_INVALIDATION: bool = conf.CONTEXT_INVALIDATION

    meta_path = classproperty(lambda cls: (_ for _ in sys.meta_path if isinstance(_, cls)))
    __finders__: list[Finder] = []

    __refs: int = 0
    refs = property(lambda self: self.__refs)
    specs: dict[str, Spec]

    def __init__(self, **CONF):
        assert None is debug.traced(3, f"[{oid(self)}] INIT {self.__class__.__name__} count:{len(self.__finders__)}")

        for k, v in CONF.items():
            if not k.isupper() or k.startswith("_"):
                raise ValueError(f"Invalid configuration key: {k}")
            setattr(self, k, v)

        self.specs = {}
        self.__finders__.append(self)

    def __del__(self):
        if self in self.__finders__:
            self.__finders__.remove(self)
        try:
            self.invalidate_caches()
        except Exception as e:
            self.specs.clear()
            assert None is debug.exception(
                f"[{oid(self)}] DEL! {self.__class__.__name__} !!!! {type(e).__name__}: {e}"
            )

    def __enter__(self) -> Finder:
        if self.__refs == 0:
            assert None is debug.traced(
                2,
                f"[{oid(self)}] HOOK {self.__class__.__name__} refs:{self.__refs} "
                f"inst:{len(list(self.meta_path))} sys:{len(sys.meta_path)} "
            )
            sys.meta_path.insert(0, self)

        self.__refs += 1
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.__refs = max(self.__refs - 1, 0)

        if self.__refs == 0 and self in sys.meta_path:
            sys.meta_path.remove(self)
            if self.CONTEXT_INVALIDATION:
                self.invalidate_caches()

        assert None is debug.traced(
            2,
            f"[{oid(self)}] EXIT {self.__class__.__name__} refs:{self.__refs} "
            f"inst:{len(list(self.meta_path))} sys:{len(sys.meta_path)} "
        )

    @classmethod
    def lazy(cls, name: str, package: str | None = None, **CONF) -> ModuleType:
        if CONF:
            with cls(**CONF):
                return import_module(name, package)

        with __finder__:
            return import_module(name, package)

    def find_spec(self, name: str, path: list[str] | None = None, target: ModuleType | None = None) -> Spec | None:
        assert None is debug.traced(
            4 if target is None else 1,
            f"[{oid(self)}] SPEC FIND {name}"
        )

        if (spec := self.specs.get(name)) is not None:
            assert None is debug.traced(
                4 if target is None else 1,
                f"[{oid(self)}] SPEC FOUN {name}"
            )
            return spec

        if (spec := self._find_spec(name, path, target)) is not None:
            spec = self.specs[name] = self.Spec(self, spec, path, target)

            assert None is debug.traced(
                1,
                f"[{oid(self)}] FIND {spec.source_tag.ljust(4)} "
                f"{spec.f_name} {'?' if spec.loader is None else ''}"
            )

        return spec

    def _find_spec(self, name: str, path: list[str] | None, target: ModuleType | None) -> ModuleSpec | None:
        for finder in (_ for _ in sys.meta_path if not isinstance(_, self.__class__)):
            if (spec := finder.find_spec(name, path, target)) is not None:
                return spec

    def get_level(self, full_name: str) -> Spec.Level:
        for name, level in self.LAZY.items():
            if re.match(name, full_name):
                return max(Spec.Level.get(level), self.NO_LAZY)
        return self.NO_LAZY

    def invalidate_caches(self) -> None:
        while self.specs:
            if hasattr(loader := self.specs.popitem()[1].loader, "invalidate_caches"):
                loader.invalidate_caches()


__finder__: Finder = Finder()

atexit.register(lambda: [finder.invalidate_caches() for finder in Finder.__finders__])
