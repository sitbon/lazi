from types import ModuleType
from typing import ForwardRef

from lazi.util import debug, oid

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
        self.__spec__ = spec

        for module_attr, attr in MODULE_SPEC_ATTR_MAP.items():
            match attr:
                case "__file__":
                    if spec.has_location:
                        module.__file__ = spec.origin
                case "__cached__":
                    if spec.has_location and spec.cached is not None:
                        module.__cached__ = spec.cached
                case "__path__":
                    if spec.submodule_search_locations is not None:
                        module.__path__ = spec.submodule_search_locations
                case _:
                    setattr(module, module_attr, getattr(spec, attr))

    def __getattribute__(self, attr):
        spec = super().__getattribute__("__spec__")

        if (target := getattr(spec, "target", None)) is None:
            if attr == "__spec__":
                return spec
            return super().__getattribute__(attr)

        assert None is debug.traced(
            3, f"[{oid(self)}] {spec.loader_state} .... [{oid(target) if target is not None else '*' * 15}] "
               f"{spec.f_name} {attr}"
        )

        if attr in GETATTR_PASS and (index := GETATTR_PASS.index(attr)) >= 0:
            return spec if not index else target.__getattribute__(attr)

        if attr in MODULE_SPEC_ATTR_MAP:
            return target.__getattribute__(attr)

        swap = False

        if spec.loader_state <= spec.loader.State.LAZY:
            assert None is debug.trace(
                f"[{oid(self)}] {spec.loader_state} >>>> [{oid(target) if target is not None else '*' * 15}] "
                f"{spec.f_name} {attr}"
            )
            spec.loader.exec_module(self, True)
            swap = spec.level >= spec.Level.SWAP

        valu = spec.target.__getattribute__(attr)  # NB: Don't use `target` here, as it may have changed.

        if swap:
            self_dict = super().__getattribute__("__dict__")
            target_dict = spec.target.__getattribute__("__dict__")
            self_dict.update(target_dict)
            super().__setattr__("__class__", ModuleType)

        return valu

    def __setattr__(self, attr, valu):
        if attr == "__spec__":
            if (target := getattr(valu, "target", None)) is not None:
                target.__setattr__(attr, valu)
            return super().__setattr__(attr, valu)

        spec = super().__getattribute__("__spec__")

        assert None is debug.traced(
            3, f"[{oid(self)}] {spec.loader_state} .... [{oid(spec.target) if spec.target is not None else '*' * 15}] "
               f"{spec.f_name} {attr} = [{oid(valu)}]"
        )

        if (target := getattr(spec, "target", None)) is None:
            return super().__setattr__(attr, valu)

        swap = False

        if attr not in SETATTR_PASS and spec.loader_state <= spec.loader.State.LAZY:
            assert None is debug.trace(
                f"[{oid(self)}] {spec.loader_state} >>>> [{oid(target) if target is not None else '*' * 15}] "
                f"{spec.f_name} {attr} = [{oid(valu)}]"
            )

            target.__setattr__(attr, valu)  # Preload the variable? Yes: Fixes stdlib (asyncio.coroutines) errors in README.md.
            spec.loader.exec_module(self, True)
            swap = spec.level >= spec.Level.SWAP

        spec.target.__setattr__(attr, valu)  # NB: Don't use `target` here, as it may have changed.

        if swap:
            self_dict = super().__getattribute__("__dict__")
            target_dict = spec.target.__getattribute__("__dict__")
            self_dict.update(target_dict)
            super().__setattr__("__class__", ModuleType)
