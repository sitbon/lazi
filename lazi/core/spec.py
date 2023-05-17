from __future__ import annotations

from types import ModuleType
from typing import ForwardRef
from importlib.machinery import ModuleSpec
from pathlib import Path
import sysconfig

from lazi.conf import conf

__all__ = "Spec",

Finder = ForwardRef("Finder")
Loader = ForwardRef("Loader")


STDLIB_PATH = Path(sysconfig.get_path("stdlib"))  # Preload sysconfig data.


class Spec(ModuleSpec):
    finder: Finder
    loader: Loader
    path: list[str] | None
    target: ModuleType | None

    stdlib: bool = property(lambda self: self.origin and Path(self.origin).is_relative_to(STDLIB_PATH))
    builtin: bool = property(lambda self: self.origin == "built-in")

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
            not self.builtin and
            (not self.stdlib or not conf.NO_STDLIB_HOOKING)
        )
