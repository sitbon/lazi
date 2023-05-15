from __future__ import annotations

import sys
from types import ModuleType
from importlib.util import find_spec, module_from_spec
from importlib.abc import MetaPathFinder

from lazi.conf import conf
from lazi.util import classproperty, debug

from .spec import Spec
from .loader import Loader
from .module import Module

__all__ = "Finder",


class Finder(MetaPathFinder):
    Spec: type[Spec] = Spec
    Loader: type[Loader] = Loader
    Module: type[Module] = Module

    __specs__: dict[str, Spec]
    __stack__: list[Finder] = []
    __refs: int = 0

    finders = classproperty(lambda cls: (_ for _ in sys.meta_path if isinstance(_, cls)))

    @property
    def refs(self) -> int:
        return self.__refs

    def __init__(self):
        self.__specs__ = {}

    def __hash__(self) -> int:
        return id(self)

    def __enter__(self) -> Finder:
        if self not in sys.meta_path:
            assert self.__refs == 0, self.__refs
            assert None is debug.trace(
                f"+ {self.__class__.__name__}[{id(self)}] "
                f"<{len([_ for _ in sys.meta_path if isinstance(_, type(self))])}>"
            )

            self.__refs += 1
            sys.meta_path.insert(0, self)

        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        if __debug__ and self.__refs == 1:
            assert None is debug.trace(f"- {self.__class__.__name__}[{id(self)}]")

        self.__refs = max(self.__refs - 1, 0)

        if self.__refs == 0 and self in sys.meta_path:
            sys.meta_path.remove(self)
            self.invalidate_caches()
            
    def lazy(self, name: str, path: list[str] | None = None, target: ModuleType | None = None) -> ModuleType:
        if (spec := self.find_spec(name, path, target)) is not None:
            module = module_from_spec(spec)
            spec.loader.exec_module(module)
            return module

    def find_spec(self, name: str, path: list[str] | None = None, target: ModuleType | None = None) -> Spec | None:
        if self in self.__stack__:
            return None

        if conf.DEBUG_TRACING > 1:
            assert None is debug.trace(f"find_spec {name!r} {path!r} {target!r}")

        if (spec := self.__specs__.get(name)) is not None:
            assert spec.finder is self
            return spec

        self.__stack__.append(self)

        try:
            if (spec := find_spec(name, path)) is not None:
                spec = self.__specs__[name] = self.Spec(self, spec, path, target)
                return spec

        finally:
            pop = self.__stack__.pop()
            assert pop is self

    def invalidate_caches(self) -> None:
        self.__specs__.clear()

    # @classmethod
    # def lazy(cls, name: str, path: list[str] | None = None, target: ModuleType | None = None) -> ModuleType:
    #     record = cls.lazy_record(name, path, target)
    #     if record.spec is None:
    #         raise ModuleNotFoundError(f"No module named {name!r}", name=name, path=path)
    #     return record.module

    # def pre_import(self, spec_record: SpecRecord) -> None:
    #     if conf.DEBUG_TRACING > 2:
    #         assert None is debug.trace("pre_import", spec_record.name, spec_record.spec)
    #
    # def on_import(self, spec_record: SpecRecord) -> None:
    #     if spec_record.hook or conf.DEBUG_TRACING > 1:
    #         if conf.DEBUG_TRACING > 2:
    #             assert None is debug.trace("on_import", spec_record.name, spec_record.path, spec_record.spec)
    #         else:
    #             assert None is debug.trace("on_import", spec_record.debug_repr)
    #
    # def pre_load(self, spec_record: SpecRecord) -> None:
    #     assert None is debug.trace("pre_load", spec_record.debug_repr)
    #
    # def on_load(self, spec_record: SpecRecord) -> None:
    #     assert None is debug.trace("on_load", spec_record.debug_repr)
    #
    # def on_load_exc(self, spec_record: SpecRecord, attr: str | None, exc: Exception) -> None:
    #     assert None is debug.trace("on_load_exc", spec_record.name, attr, type(exc).__name__, exc)
    #     assert None is debug.trace("           ", spec_record.debug_repr)
    #
    # def on_exec(self, spec_record: SpecRecord, module: ModuleType) -> None:
    #     assert None is debug.trace("on_exec", spec_record.debug_repr)
    #
    # def post_exec(self, spec_record: SpecRecord, module: ModuleType) -> bool | None:
    #     assert None is debug.trace("post_exec", spec_record.debug_repr)
    #     return
