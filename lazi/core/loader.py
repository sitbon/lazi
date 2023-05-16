from __future__ import annotations

from sys import modules
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

    def create_module(self, spec: Spec):
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

    def exec_module(self, module: Module, spec: Spec | None = None, lazy: bool = True, /):
        spec = spec if spec is not None else module.__spec__
        assert spec.loader is self, (spec.loader, self)
        assert spec.loader_state in (self.State.CREA, self.State.LAZY), spec.loader_state

        name = spec.name  # This may be overly cautious: >>> spec.target.__getattribute__("__name__")

        assert None is debug.traced(
            1,
            f"<exec> {name} <L:{spec.loader_state}> <l:{lazy}> <std:{spec.is_stdlib}> <bi:{spec.is_builtin}> "
            f"<in:{name in modules}> <is-m:{modules.get(name) is module}> "
            f"<is-t:{modules[name] is spec.target}>"
        )

        if name not in modules:
            assert None is debug.trace(
                f"<exec> {name} <L:{spec.loader_state}> <l:{lazy}> "
                f"<missing-in-sys-modules-before>"
            )
            modules[name] = module

        elif modules[name] is not module:
            assert None is debug.trace(
                f"<exec> {name} <L:{spec.loader_state}> <l:{lazy}> "
                f"<replaced-in-sys-modules-before>"
            )
            spec.target = modules[name]
            modules[name] = module

        if not lazy or conf.FORCE_LOAD_MODULE:
            spec.loader_state = self.State.EXEC
            self.loader.exec_module(module)
            spec.loader_state = self.State.LOAD
        else:
            spec.loader_state = self.State.LAZY

        assert None is debug.traced(
            3,
            f"<sys> {name} <L:{spec.loader_state}> <l:{lazy}> <m:{module}:{module.__name__}> "
            f"<in:{name in modules}> <is-m:{modules[name] is module}> "
            f"<is-t:{modules[name] is spec.target}>"
        )

        if name not in modules:
            assert None is debug.trace(
                f"<exec> {name} <L:{spec.loader_state}> <l:{lazy}> "
                f"<deleted-from-sys-modules-after>"
            )

        elif modules[name] is not spec.target and modules[name] is not module:
            assert None is debug.trace(
                f"<exec> {name} <L:{spec.loader_state}> <l:{lazy}> "
                f"<replaced-in-sys-modules-after>"
            )
            spec.target = modules[name]

    def unload_module(self, spec: Spec):
        assert spec.loader is self, (spec.loader, self)
        assert spec.loader_state is self.State.LOAD, spec.loader_state

        # NOTE: This alone seems ineffective in terms of freeing memory.
        # TODO: Re-enable and watch GC activity.
        # if (name := spec.target.__name__) in modules:
        #     del modules[name]

        spec.loader_state = self.State.DEAD
