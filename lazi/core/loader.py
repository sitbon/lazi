"""Lazy import loader.

Various methods have been tried here. During investigation of PEP 302,
 this awesome discussion was found:
    https://softwareengineering.stackexchange.com/questions/154247/experience-of-pythons-pep-302-new-import-hooks?newreg=40439eb1fac24c8dbe6baf72af975d57
"""
from __future__ import annotations

from sys import modules
from types import ModuleType
from typing import ForwardRef
from enum import IntEnum
from importlib.abc import Loader as _Loader

from lazi.conf import conf
from lazi.util import debug, oid

__all__ = "Loader",

Spec = ForwardRef("Spec")
Module = ForwardRef("Module")

NO_LAZY = conf.NO_LAZY
TRACE = conf.TRACE


class Loader(_Loader):
    spec: Spec
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

    class Error(ImportError):
        exc: BaseException

        def __init__(self, exc: BaseException, msg: str, /):
            self.exc = exc
            super().__init__(msg)

    def __init__(self, spec: Spec):
        self.spec = spec
        self.loader = spec.loader
        spec.loader_state = Loader.State.INIT

    def create_module(self, spec: Spec | None = None):
        spec = spec if spec is not None else self.spec
        assert spec.loader is self, (spec.loader, self)

        if self.__busy:
            return None

        self.__busy = True

        try:
            module = spec.target if spec.target is not None else self.loader.create_module(spec)
            module = ModuleType(spec.name) if module is None else module
            module = spec.finder.Module(spec, module) if not isinstance(module, spec.finder.Module) else module

            spec.loader_state = Loader.State.CREA

            if NO_LAZY:  # or spec.s_path is None:  # Consider whether spec is a (namespace?) package?
                self.__forc = True
                if NO_LAZY >= 2 and module is not spec.target:
                    module = spec.target
                if NO_LAZY >= 3:
                    spec.loader_state = None
                    module.__loader__ = self.loader
                    spec.loader = self.loader
                    spec.target = None

            modules[spec.name] = module  # TODO: Determine where internals are doing this already.

            return module

        finally:
            self.__busy = False

    def exec_module(self, module: Module, force: bool | None = None, /):
        spec = self.spec
        lazy = not ((force or self.__forc) if force is not None else self.__forc)

        name = spec.name
        name_ = spec.f_name
        state = spec.loader_state
        nexts = Loader.State.LAZY if lazy else Loader.State.EXEC
        target = spec.target
        in_sys = name in modules

        assert state in (Loader.State.CREA, Loader.State.LAZY), state

        if (mod := modules.get(name)) is not module:
            if in_sys:
                assert None is debug.trace(
                    f"[{oid(module)}] {state} {nexts} [{oid(target) if target is not None else '*'*15}] {name_} "
                    f"::[{oid(mod) if mod is not target else 'same' if mod is not None else '-'}] "
                    "(before)"
                ), "module was replaced in sys.modules before exec_module"

                modules[name] = module

            if mod is not None and mod is not target:
                spec.target = target = mod

        assert None is debug.traced(
            1,  # if nexts is Loader.State.EXEC else 2,
            f"[{oid(module)}] {state} {nexts} [{oid(target) if target is not None else '*'*15}] {name_} "
            f"{'>>>> ' if nexts is Loader.State.EXEC else '.... '}"
        )

        if nexts < Loader.State.EXEC:
            spec.loader_state = nexts
            return

        try:
            spec.loader_state = state = nexts

            self.loader.exec_module(target if target is not None else module)

            state = nexts
            spec.loader_state = nexts = Loader.State.LOAD
            target = spec.target

            assert None is debug.traced(
                1,  # if nexts is Loader.State.LOAD else 2,
                f"[{oid(module)}] {state} {nexts} [{oid(target) if target is not None else '*'*15}] {name_} "
                f"++++ "
            )

        except Exception as e:
            spec.loader_state = nexts = Loader.State.DEAD
            assert None is debug.trace(
                msg :=
                f"[{oid(module)}] {state} {nexts} [{oid(target) if target is not None else '*'*15}] {name_} !!!! "
                f"{type(e).__name__ if not isinstance(e, Loader.Error) else ''}"
            )

            if not isinstance(e, Loader.Error):
                raise Loader.Error(e, f"Error loading {name_}" if not __debug__ else msg) from e

            raise

        if (mod := modules.get(name)) is not module:
            if in_sys:
                assert None is debug.trace(
                    f"[{oid(module)}] {state} {nexts} [{oid(target) if target is not None else '*'*15}] {name_} "
                    f"::[{oid(mod) if mod is not target else 'same' if mod is not None else '-'}] "
                    "(after)"
                ), "module was replaced in sys.modules after exec_module"

                modules[name] = module

            if mod is not None and mod is not spec.target:
                spec.target = mod

    def invalidate_caches(self) -> None:
        spec = self.spec

        if (mod := modules.get(spec.name)) is spec.target and mod is not None:
            del modules[spec.name]

        assert None is debug.traced(
            2,
            f"[{oid(mod) if mod is not None else '*'*15}] "
            f"{spec.loader_state} DEAD [{oid(spec.target) if spec.target else '*'*15}] {spec.f_name}"
        )

        spec.loader = self.loader
        spec.loader_state = None  # type: ignore
        spec.target = None
        self.__forc = False
        self.spec = None  # type: ignore
        self.loader = None  # type: ignore
