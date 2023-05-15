from __future__ import annotations

from types import ModuleType
from typing import ForwardRef
from importlib.abc import Loader as _Loader
from importlib.util import module_from_spec

from lazi.util import debug

__all__ = "Loader",

Spec = ForwardRef("Spec")
Module = ForwardRef("Module")


class Loader(_Loader):
    loader: _Loader | None = None
    __stack__: list[Loader] = []

    def __init__(self, spec: Spec):
        self.loader = spec.loader
        spec.loader = self

    def create_module(self, spec: Spec):
        if self in self.__stack__:
            return None

        self.__stack__.append(self)

        try:
            if (module := self.loader.create_module(spec)) is None:
                module = module_from_spec(spec)

            return spec.finder.Module(spec, module)
        finally:
            self.__stack__.pop()

    def exec_module(self, module: ModuleType):
        debug.trace("exec_module", module.__name__, type(module))
        return self.loader.exec_module(module)
