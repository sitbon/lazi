"""ModuleSpec wrapper class.

https://peps.python.org/pep-0451/
"""
from __future__ import annotations

from types import ModuleType
from typing import ForwardRef
from importlib.machinery import ModuleSpec
from pathlib import Path
from functools import cached_property
import sysconfig

from lazi.conf import conf

__all__ = "Spec",

Finder = ForwardRef("Finder")
Loader = ForwardRef("Loader")


STDLIB_PATH = Path(sysconfig.get_path("stdlib"))  # Preload sysconfig data.


class Spec(ModuleSpec):
    finder: Finder
    loader: Loader
    s_path: list[str] | None
    target: ModuleType | None

    stdlib: bool = cached_property(lambda self: self.origin and STDLIB_PATH in Path(self.origin).parents)
    builtin: bool = cached_property(lambda self: self.origin == "built-in")

    _f_name = lambda self, wrap=lambda _, __: f"[{_}.]{__}": (
        wrap(parent, name) if (name := self.name) != (parent := self.parent) and parent else name
    )

    f_name: str | None = property(lambda self: self._f_name())

    def __init__(self, finder: Finder, spec: ModuleSpec, path: list[str] | None = None, target: ModuleType | None = None):
        self.finder = finder
        self.s_path = path
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

    @cached_property
    def hook(self) -> bool:
        return not conf.NO_HOOK and (
            (not self.builtin or not conf.NO_HOOK_BI) and
            (not self.stdlib or not conf.NO_HOOK_STD)
        )
