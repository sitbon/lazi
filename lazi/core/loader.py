from __future__ import annotations

from sys import modules
from types import ModuleType
from typing import ForwardRef
from enum import Enum
from importlib.abc import Loader as _Loader
from importlib.util import module_from_spec

from lazi.conf import conf
from lazi.util import debug

__all__ = "Loader",

Spec = ForwardRef("Spec")
Module = ForwardRef("Module")


class Loader(_Loader):
    loader: _Loader
    __stack__: list[Loader] = []

    class State(Enum):
        __str__ = lambda self: self.name
        INIT = 0
        CREA = 1
        LAZY = 2
        EXEC = 3
        LOAD = 4
        DEAD = 5

    def __init__(self, spec: Spec):
        self.loader = spec.loader
        spec.loader_state = self.State.INIT

    def create_module(self, spec: Spec):
        assert spec.loader is self, (spec.loader, self)

        if self in self.__stack__:
            return None

        self.__stack__.append(self)

        try:
            if (module := self.loader.create_module(spec)) is None:
                module = module_from_spec(spec)

            spec.loader_state = self.State.CREA
            module = spec.finder.Module(spec, module)
            return module
        finally:
            self.__stack__.pop()

    def exec_module(self, module: Module, spec: Spec | None = None, force: bool = False, /):
        spec = spec if spec is not None else module.__spec__
        assert spec.loader is self, (spec.loader, self)

        name = spec.name
        state = spec.loader_state
        nexts = spec.loader_state = self.State.EXEC if force else self.State.LAZY

        assert state in (self.State.INIT, self.State.CREA, self.State.LAZY), state

        if name not in modules:
            assert None is debug.trace(f"[{id(module)}] <exec> {state} {name}:{nexts} missing-in-sys-modules-before")
            modules[name] = module

        elif modules[name] is not module:
            assert None is debug.trace(
                f"[{id(module)}] <exec> {state} {name}:{nexts} replaced-in-sys-modules-before "
                f" by:{id(modules[name])}"
            )
            spec.target = modules[name]
            modules[name] = module

        assert None is debug.traced(1, f"[{id(module)}] <exec> {state} {name}:{nexts} std:{int(spec.stdlib)} bi:{int(spec.builtin)}")

        if spec.loader_state is self.State.EXEC:
            self.loader.exec_module(spec.target, spec, force) if isinstance(self.loader, type(self)) else \
                self.loader.exec_module(spec.target)
            state = nexts
            nexts = spec.loader_state = self.State.LOAD
            assert None is debug.traced(2, f"[{id(module)}] <load> {state} {name}:{nexts}")

        if name not in modules:
            assert None is debug.trace(f"[{id(module)}] <exec> {state} {name}:{nexts} deleted-from-sys-modules-after")
            # TODO: del spec.target?

        elif modules[name] is not spec.target and modules[name] is not module:
            assert None is debug.trace(
                f"[{id(module)}] <exec> {state} {name}:{nexts} replaced-in-sys-modules-after "
                f" by:{id(modules[name])}"
            )
            spec.target = modules[name]

        if nexts is self.State.LOAD:
            modules[name] = spec.target

    def unload_module(self, spec: Spec) -> ModuleType | None:
        module = modules.pop(spec.name, None)
        assert None is debug.traced(
            2,
            f"[{id(module) if module else None}] <dead> {spec.loader_state} {spec.name}:DEAD t:{id(spec.target)}"
        )
        spec.loader_state = self.State.DEAD
        return spec.target
