from __future__ import annotations

import sys
from types import ModuleType
from typing import ClassVar, ForwardRef
from dataclasses import dataclass, field
from importlib.util import module_from_spec
from importlib.machinery import ModuleSpec
import warnings

from lazi.conf import conf
from lazi.util import classproperty, debug, is_stdlib_or_builtin

__all__ = "SpecRecord",

Finder = ForwardRef("Finder")
Loader = ForwardRef("Loader")


@dataclass(slots=True, kw_only=True)
class SpecRecord:
    RECORD: ClassVar[dict[str, SpecRecord]] = {}
    __stack__: ClassVar[list[SpecRecord]] = []

    name: str
    finder: Finder
    loader: Loader | None = None

    spec: ModuleSpec | None = None

    path: list[str] | None = None
    target: str | None = None

    deps: list[SpecRecord, ...] = field(default_factory=list)
    parent: SpecRecord | None = None

    __used: bool = False
    __module: ModuleType | None = None

    @classproperty
    def RECORD_USED(self):
        return (record for record in self.RECORD.values() if record.used)

    @classproperty
    def RECORD_USED_COUNT(self):
        return sum(1 for rec in self.RECORD_USED)

    def __post_init__(self):
        self.pre_import()

        if self.spec is None:
            self.spec = self.finder.import_spec(self)

        if (self.spec or conf.SPECR_KEEP_EMPTY) and (self.hook or conf.SPECR_KEEP_0HOOK):
            if self.name in self.RECORD:
                raise ValueError(f"SpecRecord {self.name!r} already exists")

            self.RECORD[self.name] = self

        if self.hook:
            self.loader = self.finder.LoaderType(self)
            self.loader.hook()
        else:
            self.__used = self.spec is not None

        if self.spec is not None:
            self.on_import()

    def __hash__(self):
        return hash(self.name)

    @property
    def debug_repr(self):
        return (f"{'+' if self.used else '-'}{self.name} <- " +
                (f"{'+' if self.parent.used else '-'}{self.parent.name} " if self.parent else "* ") +
                f"[{'/'.join(('-', '+')[int(sr.used)] + sr.name for sr in self.__stack__)}]")

    @property
    def used(self) -> bool:
        return self.__used

    @property
    def _module(self):
        """Access the module without creating it."""
        return self._module

    @property
    def module(self) -> ModuleType | None:
        if self.spec is None:
            return None

        return (
            self.__module if self.__module is not None
            else self.__create_module()
        )

    @property
    def has_module(self) -> bool:
        return self.__module is not None

    @property
    def hook(self) -> bool:
        return self.loader is not None or (
            self.spec and self.spec.origin not in (None, "built-in") and
            (conf.SPECR_HOOK_STDBI or not self.stdlib)
        )

    @property
    def stdlib(self) -> bool:
        return is_stdlib_or_builtin(self.spec)

    @property
    def cached(self) -> bool:
        return self.name in self.RECORD

    @classmethod
    def deps_tree(cls, filt=lambda _: _.used) -> dict:
        return {_: cls.__deps_tree(_, filt) for _ in cls.RECORD.values() if _.parent is None and filt(_)}

    @classmethod
    def __deps_tree(cls, record: SpecRecord, filt) -> dict:
        return {_: cls.__deps_tree(_, filt) for _ in record.deps if filt(_)}

    @classmethod
    def register(cls, *, finder: Finder, name: str, path: list[str] | None = None, target: str | None = None) -> SpecRecord:
        if name in cls.RECORD:
            return cls.RECORD[name]
        return cls(name=name, finder=finder, path=path, target=target)

    def __create_module(self) -> ModuleType:
        assert None is debug.trace("create_module", self.name, self.spec.name in sys.modules)
        assert self.__module is None
        assert self.spec is not None

        if self.spec.name in sys.modules:
            self.__module = sys.modules[self.spec.name]
            self.on_exec(self.__module)
            return self.__module

        self.__module = module_from_spec(self.spec)
        sys.modules[self.spec.name] = self.__module

        assert self.__module is not None

        if self.loader is not None:
            self.loader.exec_module(self.__module)
        else:
            loader: Loader = self.__module.__loader__

            if not hasattr(loader, "exec_module"):
                warnings.warn(f"{self.spec.name}.exec_module() not found; falling back to load_module()", ImportWarning)
                loader.load_module(self.spec.name)
            else:
                loader.exec_module(self.__module)

        return self.__module

    def pre_import(self) -> None:
        assert self.__used is False
        self.finder.pre_import(self)

    def on_import(self) -> None:
        assert self.__used is False or self.hook is False
        self.finder.on_import(self)

    def pre_load(self) -> None:
        assert self.hook is True
        assert self.__used is False

        self.__stack__.append(self)
        self.__used = True

        self.finder.pre_load(self)

    def on_load(self) -> None:
        assert self.hook is True
        assert self.__used is True

        pop = self.__stack__.pop()
        assert pop is self

        self.finder.on_load(self)

    def on_load_exc(self, attr: str, exc: Exception) -> None:
        pop = self.__stack__.pop()
        assert pop is self
        self.finder.on_load_exc(self, attr, exc)

    def on_exec(self, module: ModuleType) -> None:
        assert self.hook is True and self.__used is False
        assert self.parent is None or (self in self.parent.deps and self in self.__stack__)
        assert module is not None
        assert module is self.__module or self.__module is None

        self.__module = module

        if parent := self.__stack__[-1] if self.__stack__ else None:
            parent.deps.append(self)
            self.parent = parent

        self.finder.on_exec(self, module)

    def post_exec(self, module: ModuleType) -> bool | None:
        if self.finder.post_exec(self, module) or self.parent is not None and self.parent.used:
            return True
