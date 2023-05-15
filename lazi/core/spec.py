from __future__ import annotations

from types import ModuleType
from typing import ForwardRef
from dataclasses import dataclass
from importlib.machinery import ModuleSpec


__all__ = "Spec",

Finder = ForwardRef("Finder")
Loader = ForwardRef("Loader")


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
        self.loader = finder.Loader(self) if not isinstance(self.loader, finder.Loader) else self.loader