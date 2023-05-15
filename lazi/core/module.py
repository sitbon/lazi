from types import ModuleType
from typing import ForwardRef

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

GETATTR_PASS = ("__spec__", "__dict__", "__class__")
SETATTR_PASS = GETATTR_PASS + tuple(MODULE_SPEC_ATTR_MAP)


class Module:
    __name__: str
    __loader__: Loader
    __package__: str
    __spec__: Spec

    def __init__(self, spec: Spec, module: ModuleType | None = None):
        super().__setattr__("__spec__", spec)
        spec.target = module if module is not None else self

    def __getattribute__(self, attr):
        spec = super().__getattribute__("__spec__")

        assert None is debug.traced(2, f"<get> {spec.name}[.{attr}] <L:{spec.loader_state}>")

        if attr in GETATTR_PASS:
            return super().__getattribute__(attr) if spec.target is self else spec.target.__getattribute__(attr)

        if attr in MODULE_SPEC_ATTR_MAP:
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
                    return getattr(spec, MODULE_SPEC_ATTR_MAP[attr])

            return super().__getattribute__(attr) if spec.target is self else spec.target.__getattribute__(attr)

        self_dict = super().__getattribute__("__dict__")

        if attr in self_dict:
            return super().__getattribute__(attr)

        if spec.target is not self and attr in (module_dict := spec.target.__getattribute__("__dict__")):
            return module_dict[attr]

        assert None is debug.trace(f"<attr> {spec.name}[.{attr}] <L:{spec.loader_state}>")

        if spec.loader_state.value <= spec.loader.State.LAZY.value:
            spec.loader.exec_module(self, lazy=False)

        return super().__getattribute__(attr) if spec.target is self else spec.target.__getattribute__(attr)

    def __setattr__(self, attr, valu):
        spec = super().__getattribute__("__spec__")

        assert None is debug.traced(
            1,
            f"<set> {spec.name}[.{attr}] = " +
            (f'<{valu.name}>' if isinstance(valu, type(spec)) else repr(valu)) +
            f" <L:{spec.loader_state}>"
        )

        if attr in SETATTR_PASS:
            return super().__setattr__(attr, valu) if spec.target is self else spec.target.__setattr__(attr, valu)

        getattr(self, attr)
        return super().__setattr__(attr, valu) if spec.target is self else spec.target.__setattr__(attr, valu)

    def __delattr__(self, attr):
        spec = super().__getattribute__("__spec__")
        assert None is debug.trace(f"<del> {spec.name}[.{attr}] <L:{spec.loader_state}>")
        getattr(self, attr)
        return super().__delattr__(attr) if spec.target is self else spec.target.__delattr__(attr)
