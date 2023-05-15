from __future__ import annotations

import sys
from types import ModuleType
from typing import ForwardRef
from enum import Enum
from importlib.abc import Loader as _Loader
from importlib.util import module_from_spec
from importlib.machinery import ModuleSpec

from lazi.conf import conf
from lazi.util import debug

__all__ = "Loader",

Spec = ForwardRef("Spec")
Module = ForwardRef("Module")


class Loader(_Loader):
    loader: _Loader | None = None
    __stack__: list[Loader] = []

    class State(Enum):
        INIT = 0
        CREA = 1
        LAZY = 2
        EXEC = 3
        LOAD = 4
        DEAD = 5

    def __init__(self, spec: Spec):
        self.loader = spec.loader
        spec.loader_state = self.State.INIT

    def create_module(self, spec: Spec | ModuleSpec):
        assert spec.loader is self, (spec.loader, self)

        if self in self.__stack__:
            return None

        self.__stack__.append(self)

        try:
            if (module := self.loader.create_module(spec)) is None:
                module = module_from_spec(spec)

            spec.loader_state = self.State.CREA
            return spec.finder.Module(spec, module)
        finally:
            self.__stack__.pop()

    def exec_module(self, module: Module | ModuleType, lazy: bool = True):
        spec = module.__spec__
        assert spec.loader is self, (spec.loader, self)
        assert spec.loader_state in (self.State.CREA, self.State.LAZY), spec.loader_state

        assert None is debug.traced(
            1,
            f"<exec> {spec.name} <L:{spec.loader_state}> <l:{lazy}> <std:{spec.is_stdlib}> <bi:{spec.is_builtin}> "
            f"<in:{spec.name in sys.modules}> <is-m:{sys.modules.get(spec.name) is module}> "
            f"<is-t:{sys.modules[spec.name] is spec.target}>"
        )

        if spec.name not in sys.modules:
            assert None is debug.trace(
                f"<exec> {spec.name} <L:{spec.loader_state}> <l:{lazy}> "
                f"<missing-in-sys-modules-before>"
            )
            sys.modules[spec.name] = module

        elif sys.modules[spec.name] is not module:
            assert None is debug.trace(
                f"<exec> {spec.name} <L:{spec.loader_state}> <l:{lazy}> "
                f"<replaced-in-sys-modules-before>"
            )
            spec.target = sys.modules[spec.name]
            sys.modules[spec.name] = module

        if not lazy or conf.FORCE_LOAD_MODULE:
            spec.loader_state = self.State.EXEC
            self.loader.exec_module(module)
            spec.loader_state = self.State.LOAD
        else:
            spec.loader_state = self.State.LAZY

        assert None is debug.traced(
            3,
            f"<sys> {spec.name} <L:{spec.loader_state}> <l:{lazy}> <m:{module}:{module.__name__}> "
            f"<in:{spec.name in sys.modules}> <is-m:{sys.modules[spec.name] is module}> "
            f"<is-t:{sys.modules[spec.name] is spec.target}>"
        )

        if spec.name not in sys.modules:
            assert None is debug.trace(
                f"<exec> {spec.name} <L:{spec.loader_state}> <l:{lazy}> "
                f"<deleted-from-sys-modules-after>"
            )

        elif sys.modules[spec.name] is not spec.target and sys.modules[spec.name] is not module:
            assert None is debug.trace(
                f"<exec> {spec.name} <L:{spec.loader_state}> <l:{lazy}> "
                f"<replaced-in-sys-modules-after>"
            )
            spec.target = sys.modules[spec.name]
            pass

    def unload_module(self, spec: Spec):
        assert spec.loader is self, (spec.loader, self)
        assert spec.loader_state is self.State.LOAD, spec.loader_state
        
        if (name := spec.target.__name__) in sys.modules:
            del sys.modules[name]

        spec.loader_state = self.State.DEAD
