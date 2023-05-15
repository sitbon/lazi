from types import ModuleType
from typing import ForwardRef

from lazi.conf import conf

__all__ = "Module",

Spec = ForwardRef("Spec")


class Module(ModuleType):
    __spec__: Spec

    def __init__(self, spec: Spec, module: ModuleType | None = None):
        super().__init__(spec.name)
        super().__setattr__("__spec__", spec)
        spec.loader_state = False
        spec.target = module if module is not None else self

    def __getattribute__(self, attr):
        self_dict = super().__getattribute__("__dict__")

        if attr == "__dict__":
            return self_dict

        if attr in self_dict:
            return super().__getattribute__(attr)

        spec: Spec = self_dict["__spec__"]

        # if spec.loader_state is False:
        #     raise spec.NeedsExecution(self, attr)

        if spec.target is self:
            return super().__getattribute__(attr)
        else:
            return spec.target.__getattribute__(attr)

    def __setattr__(self, attr, valu):
        if attr in conf.LOADER_FAKE_ATTR + ("__dict__", "__class__"):
            return super().__setattr__(attr, valu)

        getattr(self, attr)
        spec = self.__spec__

        if spec.target is self:
            return super().__setattr__(attr, valu)
        else:
            return spec.target.__setattr__(attr, valu)

    def __delattr__(self, attr):
        # assert attr not in conf.LOADER_FAKE_ATTR, attr

        getattr(self, attr)
        spec = self.__spec__

        if spec.target is self:
            return super().__delattr__(attr)
        else:
            return spec.target.__delattr__(attr)

