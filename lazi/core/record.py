from __future__ import annotations

from types import ModuleType
from typing import ClassVar, Callable, ForwardRef
from dataclasses import dataclass, field
from importlib.machinery import ModuleSpec

from lazi.conf import conf
from .util import is_stdlib_or_builtin

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
    used: bool = False
    deps: list[SpecRecord, ...] = field(default_factory=list)

    def __post_init__(self):
        self.pre_import()

        if self.spec is None:
            # NOTE: Ellipsis no longer supported, must override __spec__ to create empty spec.
            self.spec = self.finder.__spec__(self.name, self.path, self.target)

        if (self.spec or conf.SPECR_KEEP_EMPTY) and (self.hook or conf.SPECR_KEEP_0HOOK):
            if self.name in self.RECORD:
                raise ValueError(f"SpecRecord {self.name!r} already exists")

            self.RECORD[self.name] = self

        if self.hook:
            self.loader = self.finder.LoaderType(self)
            self.loader.hook()
        else:
            self.used = self.spec is not None

        self.on_import()

    def __hash__(self):
        return hash(self.name)

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
    def register(cls, *, finder: Finder, name: str, path: list[str] | None = None, target: str | None = None) -> SpecRecord:
        if name in cls.RECORD:
            return cls.RECORD[name]

        return cls(
            name=name,
            finder=finder,
            path=path,
            target=target,
        )

    def pre_import(self) -> None:
        assert self.used is False

        return self.finder.pre_import(self)

    def on_import(self) -> None:
        assert self.used is False or self.hook is False

        return self.finder.on_import(self)

    def pre_load(self) -> None:
        assert self.hook is True and self.used is False

        self.__stack__.append(self)

        return self.finder.pre_load(self)

    def on_load(self) -> None:
        assert self.hook is True and self.used is False

        self.used = True
        pop = self.__stack__.pop()

        assert pop is self

        return self.finder.on_load(self)

    def on_create(self, module: ModuleType) -> None:
        assert self.hook is True and self.used is False

        if parent := self.__stack__[-1] if self.__stack__ else None:
            parent.deps.append(self)

        return self.finder.on_create(self, module)
