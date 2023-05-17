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
    __busy: bool = False
    __forc: bool = False

    class State(Enum):
        __str__ = lambda self: self.name
        INIT = 0
        CREA = 1
        LAZY = 2
        EXEC = 3
        LOAD = 4
        DEAD = 5
        next = lambda self: type(self)((self.value + 1) % len(self.__members__))

    def __init__(self, spec: Spec):
        self.loader = spec.loader
        spec.loader_state = self.State.INIT

    def create_module(self, spec: Spec):
        assert spec.loader is self, (spec.loader, self)

        if self.__busy:
            return None

        self.__busy = True

        try:
            target = spec.target if spec.target is not None else self.loader.create_module(spec)
            target = module_from_spec(spec) if target is None else target
            target = spec.finder.Module(spec, target) if not isinstance(target, spec.finder.Module) else target

            spec.loader_state = self.State.CREA

            if conf.FORCE_LOAD_MODULE:
                self.__forc = True

            return target

        finally:
            self.__busy = False

    def exec_module(self, module: Module, spec: Spec | None = None, force: bool | None = None, /):
        spec = spec if spec is not None else module.__spec__
        force = force if force is not None else self.__forc

        assert spec.loader is self, (spec.loader, self)

        name = spec.name
        state = spec.loader_state

        assert state in (self.State.INIT, self.State.CREA, self.State.LAZY), state

        if not force and conf.NO_STDLIB_LAZLOAD and spec.stdlib:
            force = True

        nexts = spec.loader_state = self.State.EXEC if force else self.State.LAZY

        if (mod := modules.get(name)) is not module:
            assert None is debug.trace(
                f"[{id(module)}] {state} {name}:{nexts} "
                f"[{id(spec.target)}]::[{id(mod) if mod is not spec.target else 'same' if mod is not None else '-'}] "
                "(before)"
            )
            spec.target = mod
            modules[name] = module

        assert None is debug.traced(
            1, f"[{id(module)}] {state} {name}:{nexts} [{id(spec.target)}] "
               f"{'>>>>' if nexts is self.State.EXEC else ''} {'(std)' if spec.stdlib else ''}"
        )

        if nexts is self.State.EXEC:
            try:
                (self.loader.exec_module(spec.target, spec, force)
                    if isinstance(self.loader, type(self)) else
                    self.loader.exec_module(spec.target))

                state = nexts
                nexts = spec.loader_state = self.State.LOAD

            except Exception as e:
                assert None is debug.traced(
                    -1, f"[{id(module)}] {state} {name}:{nexts} [{id(spec.target)}] !!!! {type(e).__name__}: {e}"
                )
                raise
            else:
                assert None is debug.traced(1, f"[{id(module)}] {state} {name}:{nexts} [{id(spec.target)}] ++++ ")

        if (mod := modules.get(name)) is not module:
            assert None is debug.trace(
                f"[{id(module)}] {state} {name}:{nexts} "
                f"[{id(spec.target)}]::[{id(mod) if mod is not spec.target else 'same' if mod is not None else '-'}] "
                "(after)"
            )
            spec.target = mod
            modules[name] = module

        # if nexts is self.State.LOAD and spec.target is not None:
        #     modules[name] = spec.target

    def unload_module(self, spec: Spec) -> ModuleType | None:
        module = modules.pop(spec.name, None)
        assert None is debug.traced(
            2, f"[{id(module) if module else 'not-in-modules!'}] {spec.loader_state} {spec.name}:DEAD [{id(spec.target)}]"
        )
        spec.loader_state = self.State.DEAD
        return spec.target
