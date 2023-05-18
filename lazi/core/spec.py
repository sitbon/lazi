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

NO_HOOK = conf.NO_HOOK
NO_HOOK_BI = conf.NO_HOOK_BI
NO_HOOK_STD = conf.NO_HOOK_STD


class Spec(ModuleSpec):
    finder: Finder
    loader: Loader
    s_path: list[str] | None
    target: ModuleType | None

    stdlib: bool = cached_property(lambda self: self.origin and STDLIB_PATH in Path(self.origin).parents)
    builtin: bool = cached_property(lambda self: self.origin == "built-in")

    _f_name = lambda self, wrap=lambda _, __: f"{_}|{__.replace(f'{_}.', '', 1)}": (
        wrap(parent, name) if (name := self.name) != (parent := self.parent) and parent else name
    )

    f_name: str | None = cached_property(lambda self: self._f_name())

    is_package: bool = cached_property(lambda self: self.submodule_search_locations is not None)

    def __init__(self, finder: Finder, spec: ModuleSpec, path: list[str] | None = None, target: ModuleType | None = None):
        assert spec.loader is not None, "ModuleSpec.loader is None"

        self.finder = finder
        self.s_path = path
        self.target = target

        super().__init__(
            name=spec.name,
            loader=spec.loader,
            origin=spec.origin,
            loader_state=spec.loader_state,
            is_package=spec.submodule_search_locations is not None or path is None,
        )

        self.__dict__.update(spec.__dict__)
        self.loader = finder.Loader(self) if self.hook else self.loader

    @cached_property
    def hook(self) -> bool:
        return not NO_HOOK and (
            (not self.builtin or not NO_HOOK_BI) and
            (not self.stdlib or not NO_HOOK_STD)
        )
