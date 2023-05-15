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

GETATTR_PASS = ("__spec__", "__class__") + (("__dict__",) if not conf.NO_DICT_LAZY_ATTR else ())
SETATTR_PASS = GETATTR_PASS + tuple(MODULE_SPEC_ATTR_MAP)


class Module(ModuleType):
    __name__: str
    __loader__: Loader
    __package__: str
    __spec__: Spec

    def __init__(self, spec: Spec, module: ModuleType):
        super().__init__(spec.name)
        self.__spec__ = spec
        spec.target = module

    def __getattribute__(self, attr):
        spec = super().__getattribute__("__spec__")

        assert None is debug.traced(2, f"<get> {spec.name}[.{attr}] <L:{spec.loader_state}>")

        if attr in GETATTR_PASS:
            return spec.target.__getattribute__(attr)

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

            return spec.target.__getattribute__(attr)

        if not conf.NO_DICT_LAZY_ATTR:
            module_dict = spec.target.__getattribute__("__dict__")
            if attr == "__dict__":
                return module_dict
            if attr in module_dict:
                return module_dict[attr]

        assert None is debug.traced(
            0 if spec.loader_state.value < spec.loader.State.LOAD.value else 1,
            f"<attr> {spec.name}[.{attr}] <L:{spec.loader_state}>"
        )

        if spec.loader_state.value <= spec.loader.State.LAZY.value:
            spec.loader.exec_module(self, lazy=False)

        return spec.target.__getattribute__(attr)

    def __setattr__(self, attr, valu):
        spec = super().__getattribute__("__spec__")

        if attr in SETATTR_PASS:
            if attr == "__spec__":
                return super().__setattr__(attr, valu)

            return spec.target.__setattr__(attr, valu)

        assert None is debug.traced(
            1,
            f"<set> {spec.name}[.{attr}] = " +
            (f'<{valu.name}>' if isinstance(valu, type(spec)) else repr(valu)) +
            f" <L:{spec.loader_state}>"
        )

        # TODO: We have recursion issues in some cases now?
        getattr(self, attr)
        return spec.target.__setattr__(attr, valu)
