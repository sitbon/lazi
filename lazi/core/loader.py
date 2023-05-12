import sys
from types import ModuleType
from importlib.util import LazyLoader
# noinspection PyUnresolvedReferences,PyProtectedMember
from importlib.util import _LazyModule  # type: type[ModuleType]

from lazi.conf import conf
from lazi.util import debug
from .record import SpecRecord

__all__ = "Loader",


class Loader(LazyLoader):
    spec_record: SpecRecord

    def __init__(self, spec_record: SpecRecord):
        self.spec_record = spec_record
        super().__init__(spec_record.spec.loader)

    @property
    def used(self) -> bool:
        return self.spec_record.used

    def hook(self):
        assert self.spec_record.hook is True
        self.spec_record.spec.loader = self

    def pre_load(self):
        return self.spec_record.pre_load()

    def on_load(self):

        if conf.LOADER_AUTO_DEPS:
            for dep in (dep for dep in self.spec_record.deps if dep.spec is not None and not dep.used):
                debug.trace("dep_load", self.spec_record.name, "->", dep.name, dep.used, dep.spec.name in sys.modules)

                try:
                    getattr(dep.module, "__dict__", None)  # Force the module to load.
                except Exception as exci:
                    debug.trace("dep_load[recursive-exc]", self.spec_record.name, "->", dep.name)
                    debug.trace(" " * 23, "  ", f"{type(exci).__name__}:", exci)
                    debug.trace(" " * 23, "  ", "self.spec:", self.spec_record.spec)
                    debug.trace(" " * 23, "  ", "dep.spec:", dep.spec)
                    pass

        return self.spec_record.on_load()

    def on_exec_exc(self, exc):
        return self.spec_record.on_exec_exc(exc)

    def on_exec(self, module: ModuleType):
        return self.spec_record.on_exec(module)

    def exec_module(self, module: ModuleType):
        # TODO(?): Detect recursion issues.

        mdic = object.__getattribute__(module, "__dict__")
        self.on_exec(module)
        super().exec_module(module)

        loader_orig = self.spec_record.spec.loader
        self.spec_record.spec.loader = self
        mdic["__loader__"] = self

        # noinspection PyMethodParameters
        class LazyModule(_LazyModule):
            def __setattr__(_, key, value):
                debug.trace("setattribute", self.spec_record.name, key)
                return super().__setattr__(key, value)

            def __getattribute__(_, attr):
                if (attr == "__class__" or attr in conf.LOADER_FAKE_ATTR) and attr in mdic:
                    debug.trace("geyattribute", self.spec_record.name, attr)
                    return mdic[attr]
                elif attr in conf.LOADER_FAKE_ATTR:
                    debug.trace("geeattribute", self.spec_record.name, attr)
                    raise AttributeError(attr)

                self.spec_record.spec.loader = loader_orig
                mdic["__loader__"] = loader_orig

                self.pre_load()

                try:
                    debug.trace("getattribute", self.spec_record.name, attr, "<load>")
                    valu = super().__getattribute__(attr)

                except Exception as exc:
                    self.on_exec_exc(exc)
                    raise

                else:
                    self.on_load()
                    return valu

            def __delattr__(_, attr):
                return _LazyModule.__delattr__(_,  attr)

        module.__class__ = LazyModule
