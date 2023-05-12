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
    def loaded(self) -> bool:
        return self.spec_record.used

    def hook(self):
        assert self.spec_record.hook is True
        self.spec_record.spec.loader = self

    def pre_load(self):
        return self.spec_record.pre_load()

    def on_load(self, exc=None):
        assert self.loaded is False

        if exc is None and conf.LOADER_AUTO_DEPS:
            for dep in (dep for dep in self.spec_record.deps if dep.spec is not None):
                # New discovery from this: dep.spec.loader gets changed between its on_create() and here.
                debug.trace("dep_load", self.spec_record.name, "->", dep.name, dep.used, dep.spec.name in sys.modules)

                try:
                    getattr(dep.module, "__dict__", None)  # Force the module to load.
                except Exception as exci:
                    debug.trace("dep_load[recursive-exc]", self.spec_record.name, "->", dep.name)
                    debug.trace(" " * 23, "  ", "err:", exci)
                    debug.trace(" " * 23, "  ", "self.spec:", self.spec_record.spec)
                    debug.trace(" " * 23, "  ", "dep.spec:", dep.spec)
                    pass

        return self.spec_record.on_load(exc=exc)

    def on_create(self, module: ModuleType):
        return self.spec_record.on_create(module)

    def exec_module(self, module: ModuleType):
        self.on_create(module)
        super().exec_module(module)

        # noinspection PyMethodParameters
        class LazyModule(_LazyModule):
            def __getattribute__(_, attr):
                debug.trace("getattribute", self.spec_record.name, attr)
                assert self.loaded is False

                if attr in conf.LOADER_FAKE_ATTR:
                    match attr:
                        case "__spec__":
                            return self.spec_record.spec
                        case "__loader__":
                            return self
                        case "__name__":
                            return self.spec_record.name
                        case "__class__":
                            return LazyModule
                        case "__package__":
                            return self.spec_record.spec.parent
                        case "__file__":
                            if self.spec_record.spec.has_location:
                                return self.spec_record.spec.origin
                        case "__path__":
                            return self.spec_record.spec.submodule_search_locations or []

                self.pre_load()

                try:
                    debug.trace("getattribute", self.spec_record.name, attr, "load")

                    value = _LazyModule.__getattribute__(_, attr)

                except Exception as exc:
                    self.on_load(exc=exc)
                    raise

                else:
                    self.on_load()
                    return value


            @classmethod
            def __delattr__(_, attr):
                return _LazyModule.__delattr__(_,  attr)

        module.__class__ = LazyModule
