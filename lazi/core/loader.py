from __future__ import annotations

from sys import modules
from types import ModuleType
from typing import ForwardRef
from enum import IntEnum
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

    class State(IntEnum):
        __str__ = lambda self: self.name
        INIT = 0
        CREA = 1
        LAZY = 2
        EXEC = 3
        LOAD = 4
        DEAD = 5

    def __init__(self, spec: Spec):
        self.loader = spec.loader
        spec.loader_state = Loader.State.INIT

    def create_module(self, spec: Spec):
        assert spec.loader is self, (spec.loader, self)

        if self.__busy:
            return None

        self.__busy = True

        try:
            target = spec.target if spec.target is not None else self.loader.create_module(spec)
            target = module_from_spec(spec) if target is None else target
            target = spec.finder.Module(spec, target) if not isinstance(target, spec.finder.Module) else target

            spec.loader_state = Loader.State.CREA

            if conf.FORCE_LOAD_MODULE:
                self.__forc = True

            return target

        finally:
            self.__busy = False

    def exec_module(self, module: Module, spec: Spec | None = None, force: bool | None = None, /):
        spec = spec if spec is not None else module.__spec__
        lazy = not (force if force is not None else self.__forc)

        assert spec.loader is self, (spec.loader, self)

        name = spec.name
        state = spec.loader_state
        nexts = Loader.State.LAZY if lazy else Loader.State.EXEC

        assert state in (Loader.State.CREA, Loader.State.LAZY), state

        if (mod := modules.get(name)) is not module:
            assert None is debug.trace(
                f"[{id(module)}] {state} {name}:{nexts} "
                f"[{id(spec.target)}]::[{id(mod) if mod is not spec.target else 'same' if mod is not None else '-'}] "
                "(before)"
            )
            spec.target = mod
            modules[name] = module

        assert None is debug.traced(
            1,  # if nexts is Loader.State.EXEC else 2,
            f"[{id(module)}] {state} {name}:{nexts} [{id(spec.target)}] "
            f"{'>>> ' if nexts is Loader.State.EXEC and not lazy else ''}{'(std)' if spec.stdlib else ''}"
        )

        if state < Loader.State.EXEC:
            spec.loader_state = nexts
            return

        try:
            self.loader.exec_module(module)
            state = nexts
            spec.loader_state = nexts = Loader.State.LOAD

            assert None is debug.traced(
                1,  # if nexts is Loader.State.LOAD else 2,
                f"[{id(module)}] {state} {name}:{nexts} [{id(spec.target)}] "
                f"{'++++ ' if nexts is Loader.State.LOAD else ':)'}"
            )

        except Exception as e:
            state = nexts
            spec.loader_state = nexts = Loader.State.DEAD
            assert None is debug.traced(
                -1, f"[{id(module)}] {state} {name}:{nexts} [{id(spec.target)}] !!!! {type(e).__name__}: {e}"
            )
            raise

        if (mod := modules.get(name)) is not module:
            assert None is debug.trace(
                f"[{id(module)}] {state} {name}:{nexts} "
                f"[{id(spec.target)}]::[{id(mod) if mod is not spec.target else 'same' if mod is not None else '-'}] "
                "(after)"
            )
            spec.target = mod
            modules[name] = module

        # if nexts is Loader.State.LOAD and spec.target is not None:
        #     modules[name] = spec.target

    def unload_module(self, spec: Spec) -> ModuleType | None:
        module = modules.pop(spec.name, None)
        assert None is debug.traced(
            2, f"[{id(module) if module else 'not-in-modules!'}] "
               f"{spec.loader_state} {spec.name}:DEAD [{id(spec.target)}]"
        )
        spec.loader_state = Loader.State.DEAD
        return spec.target
