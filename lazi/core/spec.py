from __future__ import annotations

from types import ModuleType
from typing import ForwardRef
from dataclasses import dataclass
from importlib.machinery import ModuleSpec
from pathlib import Path
import sysconfig

from lazi.conf import conf

__all__ = "Spec",

Finder = ForwardRef("Finder")
Loader = ForwardRef("Loader")


getattr(sysconfig, "get_path")  # Preload sysconfig data.


class Spec(ModuleSpec):
    finder: Finder
    loader: Loader
    path: list[str] | None
    target: ModuleType | None

    @dataclass(slots=True, frozen=True)
    class NeedsExecution(StopIteration):
        spec: Spec
        attr: str | None

        def __post_init__(self):
            self.spec.needs.append(self)

    needs: list[NeedsExecution] = []

    def __init__(self, finder: Finder, spec: ModuleSpec, path: list[str] | None = None, target: ModuleType | None = None):
        self.finder = finder
        self.path = path
        self.target = target

        super().__init__(
            name=spec.name,
            loader=spec.loader,
            origin=spec.origin,
            loader_state=spec.loader_state,
            is_package=spec.submodule_search_locations is not None,
        )

        self.__dict__.update(spec.__dict__)

        self.loader = finder.Loader(self) if self.hook else self.loader

    @property
    def hook(self) -> bool:
        return not conf.DISABLE_LOAD_HOOK and (
            not self.is_builtin and
            (not self.is_stdlib or not conf.NO_STDLIB_MODULES)
        )

    @property
    def is_stdlib(self) -> bool:
        return not self.is_builtin and Path(self.origin).is_relative_to(sysconfig.get_path("stdlib"))

    @property
    def is_builtin(self) -> bool:
        return self.origin in (None, "built-in")
