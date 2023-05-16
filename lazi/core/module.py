from types import ModuleType
from typing import ForwardRef

from lazi.conf import conf
from lazi.util import debug

__all__ = "Module",

Spec = ForwardRef("Spec")
Loader = ForwardRef("Loader")

# See https://peps.python.org/pep-0451/#attributes
MODULE_SPEC_ATTR_MAP = dict(
    __name__="name",
    __loader__="loader",
    __package__="parent",
    __file__="origin",
    __cached__="cached",
    __path__="submodule_search_locations",
)

GETATTR_PASS = ("__spec__", "__class__")
SETATTR_PASS = GETATTR_PASS + tuple(MODULE_SPEC_ATTR_MAP)


class Module(ModuleType):
    __name__: str
    __loader__: Loader
    __package__: str
    __spec__: Spec

    def __init__(self, spec: Spec, module: ModuleType):
        super().__init__(spec.name)
        self.__spec__ = module.__spec__ = spec
        spec.target = module

    def __getattribute__(self, attr):
        spec = super().__getattribute__("__spec__")

        assert None is debug.traced(3, f"[{id(self)}] <GET> {spec.loader_state} {spec.name}[.{attr}]")

        if attr in GETATTR_PASS and (index := GETATTR_PASS.index(attr)) >= 0:
            return spec if not index else spec.target.__getattribute__(attr)

        if name := MODULE_SPEC_ATTR_MAP.get(attr):
            match attr:
                case "__file__":
                    if spec.has_location:
                        return spec.origin
                case "__cached__":
                    if spec.has_location and spec.cached is not None:
                        return spec.cached
                case "__path__":
                    if spec.submodule_search_locations is not None:
                        return spec.submodule_search_locations
                case _:
                    return getattr(spec, name)

            return spec.target.__getattribute__(attr)

        if spec.loader_state.value <= spec.loader.State.LAZY.value:
            assert None is debug.trace(f"[{id(self)}] <get> {spec.loader_state} {spec.name}[.{attr}]")
            spec.loader.exec_module(self, spec, True)

        return spec.target.__getattribute__(attr)

    def __setattr__(self, attr, valu):
        spec = super().__getattribute__("__spec__")

        if attr in SETATTR_PASS:
            if attr == "__spec__":
                return super().__setattr__(attr, valu)

            return spec.target.__setattr__(attr, valu)

        if spec.loader_state.value <= spec.loader.State.LAZY.value:
            assert None is debug.trace(f"[{id(self)}] <set> {spec.loader_state} {spec.name}[.{attr}] [{id(valu)}]")
            spec.loader.exec_module(self, spec, True)

        return spec.target.__setattr__(attr, valu)
