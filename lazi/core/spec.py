"""ModuleSpec wrapper class.

https://peps.python.org/pep-0451/
"""
from __future__ import annotations

from types import ModuleType
from typing import ForwardRef
from importlib.machinery import ModuleSpec
from importlib import import_module
from pathlib import Path
from functools import cached_property, cache
from enum import IntEnum

from lazi.conf import conf
from lazi.util.functional import classproperty

__all__ = "Spec",

Finder = ForwardRef("Finder")
Loader = ForwardRef("Loader")


class Spec(ModuleSpec):
    STDLIB_PATH = classproperty(cache(lambda _: Path(import_module("sysconfig").get_path("stdlib"))))

    NO_HOOK: bool = conf.NO_HOOK
    NO_HOOK_BI: bool = conf.NO_HOOK_BI
    NO_HOOK_STD: bool = conf.NO_HOOK_STD
    NO_CHECK_STD_BI: bool = conf.NO_CHECK_STD_BI

    finder: Finder
    loader: Loader
    s_path: list[str] | None
    target: ModuleType | None

    stdlib: bool = cached_property(lambda self: self.origin and self.STDLIB_PATH in Path(self.origin).parents)
    builtin: bool = cached_property(lambda self: self.origin == "built-in")

    _f_name = lambda self, wrap=lambda _, __: f"{_}|{__.replace(f'{_}.', '', 1)}": (
        wrap(parent, name) if (name := self.name) != (parent := self.parent) and parent else name
    )

    f_name: str | None = cached_property(lambda self: self._f_name())  # Formatted name.
    p_name: str | None = cached_property(lambda self: self._f_name(lambda _, __: f"{_}.{__}"))  # Path (full) name.

    is_package: bool = cached_property(lambda self: self.submodule_search_locations is not None)

    @cached_property
    def source_tag(self) -> str:
        return (
                (
                    Path(c).suffix[1:] if (c := self.cached) else
                    (Path(o).suffix[1:] or o[:4]) if (o := self.origin) else
                    '?'
                ) +
                (
                    f"{'S' if self.stdlib else ''}{'B' if self.builtin else ''}"
                    if not self.NO_CHECK_STD_BI else ""
                )
        )

    class Level(IntEnum):
        __str__ = lambda self: self.name
        NONE = -1
        LAZY = 0
        SWAP = 1
        LOAD = 2
        UNMO = 3
        UNLO = 4

        @classmethod
        def get(cls, level: str | int) -> Spec.Level:
            if isinstance(level, str):
                return cls[level.upper()]
            return cls(level)

    level: Level

    def __init__(
            self,
            finder: Finder,
            spec: ModuleSpec,
            path: list[str] | None,
            target: ModuleType | None,
    ):
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

        self.level = finder.get_level(self.p_name)
        self.loader = finder.Loader(self) if self.hook else self.loader

    @cached_property
    def hook(self) -> bool:
        return not self.NO_HOOK and (
            ((self.level > Spec.Level.NONE) or self.NO_CHECK_STD_BI) or
            ((not self.builtin or not self.NO_HOOK_BI) and
                (not self.stdlib or not self.NO_HOOK_STD))
        )
